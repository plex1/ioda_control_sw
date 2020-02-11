from tinydb import TinyDB, Query, where
import datetime
from TestEnv.TestEnvLog import DataLogger
from TestEnv.TestEnvLog import Checker
import logging
import importlib


# todo: tags could have key and value (and type: boolean, integer)

# can be used to filter test cases or
# todo: can be used to filter units
class TestEnvFilter(object):

    def __init__(self, tc_tags=[], units=[], unit_filter_type='remove', tc_filter_type='remove'):
        self.tc_tags = tc_tags
        self.unit_filter_type = unit_filter_type
        self.tc_filter_type = tc_filter_type # filter type for tags
        self.units = units

    def filter_unit_names(self, list_in):
        list_out = []
        for elem in list_in:
            if elem in self.units:
                if self.unit_filter_type == "keep":
                    list_out.append(elem)
            else:
                if self.unit_filter_type == "remove":
                    list_out.append(elem)
        return list_out

    def filter_tc_tags(self, list_in):
        list_out = []
        for elem in list_in:
                elem_is_tagged = False
                for tag in elem['tags']:
                    if tag in self.tc_tags:
                        elem_is_tagged = True
                if (self.tc_filter_type == 'keep' and elem_is_tagged) or \
                        (self.tc_filter_type == 'remove' and not elem_is_tagged):
                    list_out.append(elem)
        return list_out


noFilter = TestEnvFilter([])


class AbstractTestCase(object):

    def __init__(self, TestCaseName, id='', unit_name='', controller=None, setup = None):
        self.time =datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        prefix = self.time
        if id != '':
            prefix = id
        prefix = prefix+'_' + unit_name + '_' + TestCaseName
        self.data_logger = DataLogger(prefix)
        self.checker = Checker(prefix)
        self.TestCaseName=TestCaseName
        self.prefix = prefix
        self.id = id
        self.controller = controller
        self.setup = setup

        # create logger with 'spam_application'
        logger = logging.getLogger(prefix)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('db/' + prefix + '.log')
        fh.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)

        logger.info('creating an instance '+ prefix)

        self.logger = logger

    @staticmethod
    def gen_id():
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # @abstractmethod
    # execute test
    def execute(self):
        self.logger.info('Start Test Execution ')
        self.checker.start_exec()

    #@abstractmethod
    # post processing
    def evaluate(self):
        self.logger.info('Start Test Evaluation ')
        self.checker.start_eval()


class TestCases(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_testcases.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()
        self.id = 0

    def add_test_case(self, name, units, tags=[]):
        self.db.insert({'name': name,
                        'units': units,
                        'tags' : tags,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'id' : self.id
                        })
        self.id = self.id+1

    def get_test_cases(self):
        return self.db.all()

    def get_test_cases_units(self, unit_list):
        test_cases = []
        for unit in unit_list:
            test_cases += self.db.search(self.query.units.any(str(unit))) #todo: shouldn't work with 'unit_' + unit
        return test_cases


class Unit(object):

    def __init__(self, name, testif):
        self.ctrl = None
        self.gui = None
        self.sub_unit={}
        self.name = name
        self.testif = testif

    def set_controller(self, ctrl):
        self.ctrl = ctrl

    def set_gui(self, gui):
        self.gui = gui

    def add_sub_unit(self, name):
        self.sub_unit[name] = Unit(name, self.testif)

    def populate(self, unit_hierarchy, controllers, guis):

        for su in unit_hierarchy.get_sub_units(self.name, False):
            self.add_sub_unit(su)
            self.sub_unit[su].populate(unit_hierarchy, controllers, guis)


        ctrl = controllers.get_controller_instance(self.name)
        self.set_controller(ctrl)
        if ctrl is None:
            self.set_controller(None)
            #print("Warning: Controller for " + self.name + " not found")
        else:
            ctrl.set_sub_units(self.sub_unit)

        gui = guis.get_gui_instance(self.name, ctrl)
        self.set_gui(gui)
        if gui is None:
            pass
            #print("Warning: GUI for " + self.name + " not found")


class UnitHierarchy(object):

    # todo: return unit dictionay, then write a function which can filter for tags and one that returns just a list of names
    # this allows for easy filtering for tags in units and test cases: filterout and filter keep (standard)

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_module_hierarchy.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_unit(self, name, sub_units, tags = []):
        self.db.insert({'name': name,
                        'sub_units' : sub_units,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"),
                        'tags' : tags
                        })

    def get_sub_units(self, unit_name, recursive=True):
        unitfound = self.db.search(where('name') == unit_name)
        if len(unitfound)>0:
            unit = unitfound[0]
            sub_units = unit['sub_units']
        else:
            sub_units = []
        sub_units_list = []
        for sub_unit in sub_units:
            sub_units_list.append(sub_unit)
        if recursive:
            sub_units_list1 = sub_units_list.copy()
            for unit in sub_units_list1:
                sub_units_list += self.get_sub_units(unit, recursive)
        return sub_units_list

    def get_sub_units_incl(self, unit_name, recursive=True):
        return [unit_name] + self.get_sub_units(unit_name, recursive)


class BaseController(object):
    def __init__(self, testif, sub_units=[], parameters={}):
        self.sub_units = sub_units
        self.parameters = parameters
        self.testif = testif

    def set_sub_units(self, sub_units):
        self.sub_units = sub_units


class Controllers(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_controllers.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()
        self.testif = None

    def set_testif(self, testif):
        self.testif = testif

    def add_controller(self, unit_name, controller, parameters={}, tags=[]): #tags = parameters=?
        self.db.insert({'UnitName': unit_name,
                        'Controller' : controller,
                        'Tags' : tags,
                        'Parameters' : parameters,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_controller(self, unit_name):
        result = self.db.search(where('UnitName') == unit_name)
        if len(result) == 0:
            return None
        else:
            unitfound = result[0]
            return unitfound['Controller']

    def get_controller_parameters(self, unit_name):
        unitfound = self.db.search(where('UnitName') == unit_name)[0]
        return unitfound['Parameters']

    def get_controller_instance(self, unit_name):
        ctrl_name = self.get_controller(unit_name)
        if ctrl_name is None:
            return None
        else:
            p, m = ctrl_name.rsplit('.', 1)
            mod = importlib.import_module(p)
            ctrl = getattr(mod, m)
            parameters = self.get_controller_parameters(unit_name)
            sub_units = None  # sub-units get assigned afterwards
            return ctrl(self.testif, sub_units, parameters)


class Guis(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix + '_guis.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_gui(self, unit_name, gui_controller, gui_view, tags=[]):
        self.db.insert({'UnitName': unit_name,
                        'GuiController' : gui_controller,
                        'GuiView': gui_view,
                        'Tags' : tags,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_gui(self, unit_name):
        result = self.db.search(where('UnitName') == unit_name)
        if len(result) == 0:
            return None
        else:
            unitfound = result[0]
            return unitfound['GuiView'], unitfound['GuiController']


    def get_gui_instance(self, unit_name, controller):
        gui = self.get_gui(unit_name)
        if gui is None:
            return None
        else:
            gui_ctrl = gui[1]
            p, m = gui_ctrl.rsplit('.', 1)
            mod = importlib.import_module(p)
            ctrl = getattr(mod, m)

            gui_view = gui[0]
            p, m = gui_view.rsplit('.', 1)
            mod = importlib.import_module(p)
            view = getattr(mod, m)

            gv = view()
            gc = ctrl(gv, controller)
            return gc


class TestEnvMainControl(object):

    def __init__(self, testif, hierarchy, controllers, testcases, requirements, guis={}):
        self.testif = testif
        self.hierarchy = hierarchy
        self.controllers = controllers
        self.testcases = testcases
        self.requirements = requirements
        self.guis = guis
        self.id = "id1"

    def set_id(self, id):
        self.id = id

    # todo give the following parameters: units, recursive, filter_units, filter_testcases, maybe in a different function
    def run(self, unit='', recursive=True, testenv_filter=noFilter):

        tc_inst = self.get_test_cases_populate(unit, recursive, testenv_filter)

        # execute test cases
        for test_case_inst in tc_inst:
            # todo add filtering for test case tags
            print('Executing Test Case ' + test_case_inst['name'] + ' for unit: ' + test_case_inst['unit'])
            tc = test_case_inst['inst']
            # todo: test cases classes could also be populated in external function such as in unit.populate
            tc.execute()

    def analyze(self, unit='', recursive=True, testenv_filter=noFilter):

        tc_inst = self.get_test_cases_populate(unit, recursive, testenv_filter)

        # execute test cases
        for test_case_inst in tc_inst:
            # todo add filtering for test case tags
            print('Evaluating Test Case ' + test_case_inst['name'] + ' for unit: ' + test_case_inst['unit'])
            tc = test_case_inst['inst']
            # todo: test cases classes could also be populated in external function such as in unit.populate
            tc.evaluate()

    def get_test_cases_populate(self, unit='', recursive=True, testenv_filter=noFilter):

        # list of test cases
        if unit == '':
            selected_test_cases = self.testcases.get_test_cases()
        else:
            if recursive:
                selected_units = self.hierarchy.get_sub_units_incl(unit)
            else:
                selected_units = [unit]
            #filter units
            selected_test_cases = self.testcases.get_test_cases_units(testenv_filter.filter_unit_names(selected_units))

        #todo: filter out tags for units
        # todo: 1) filter units with tags and names, 2) filter testcases with tags and names
        #filter out tags for test cases
        selected_test_cases_tag = testenv_filter.filter_tc_tags(selected_test_cases)

        # create instance of testcases
        tc = []
        for test_case in sorted(selected_test_cases_tag, key=lambda item:  item['id']):
            for test_case_unit in test_case['units']:
                class_name = test_case['name']
                p, m = class_name.rsplit('.', 1)
                mod = importlib.import_module(p)
                testcaseclass = getattr(mod, m)
                top_unit = test_case_unit
                setup = self.gen_setup(self.hierarchy, self.controllers, self.testif, self.guis, top_unit)
                inst = testcaseclass(self.id, test_case_unit, self.testif,
                                     setup.ctrl, setup)

                tc.append({'name': test_case['name'], 'unit': test_case_unit, 'inst': inst})

        return tc

    def gen_setup(self, hierarchy, controllers, testif, guis={}, top_unit='ioda'):
        ioda_setup = Unit(top_unit, testif)
        ioda_setup.populate(hierarchy, controllers, guis)
        return ioda_setup

    def control(self):
        ioda_setup = self.gen_setup(self.hierarchy, self.controllers, self.testif, self.guis)
        return ioda_setup

    def collect_results(self, unit='', recursive=True, testenv_filter=noFilter):

        rm = self.requirements

        # get all testcases
        tc_inst = self.get_test_cases_populate(unit, recursive, testenv_filter)

        # collect checkers
        for test_case_inst in tc_inst:
            rm.add_checker(test_case_inst['inst'].checker)

        rm.collect_checks()
        rm.check_requirements()
        rm.print_results()


def main():

    tc = TestCases()
    tc.add_test_case('MotorPos', ['motorcontroller_unit'])
    tc.add_test_case('MotorSpeed', ['motorcontroller_unit'])
    tc.add_test_case('MotorAutoZero', ['motorcontroller_unit'])
    tc.add_test_case('MotorPower', ['motorcontrollerpower_unit'])
    tc.add_test_case('MotorPower2', ['motorcontrollerpower_unit'])
    tc.add_test_case('TofCalibration', ['toffpga_unit'])
    tc.add_test_case('TofMeasure', ['toffpga_unit'])

    tch = UnitHierarchy()
    tch.add_unit('ioda', ['motorcontroller_unit', 'toffpga_unit'])
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])

    print(testenv_to_names(tc.get_test_cases()))
    print(tch.get_sub_units_incl('ioda', True))
    print(testenv_to_names(tc.get_test_cases_units(tch.get_sub_units_incl('ioda', False))))
    print(testenv_to_names(tc.get_test_cases_units(tch.get_sub_units_incl('ioda'))))


if __name__ == "__main__":
    main()
