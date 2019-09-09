from tinydb import TinyDB, Query, where
import datetime
from TestEnvLog import DataLogger
from TestEnvLog import Checker
import logging


# todo: tags could have key and value (and type: boolean, integer)

# can be used to filter test cases or
# todo: can be used to filter units
class TestEnvFilter(object):

    def __init__(self, tags, filter_type='out'):
        self.tags = tags
        self.filter_type = filter_type


def testenv_filter(list_in, testenv_filter):
    list_out = []
    for elem in list_in:
            elem_istagged = False
            for tag in elem['tags']:
                if tag in testenv_filter.tags:
                    elem_istagged = True
            if (testenv_filter.filter_type == 'keep' and elem_istagged) or \
                    (testenv_filter.filter_type == 'out' and not elem_istagged):
                list_out.append(elem)
    return list_out


def testenv_to_names(list_in):
    list_out = []
    for elem in list_in:
        list_out.append(elem['name'])
    return list_out


class AbstractTestCase(object):

    def __init__(self, TestCaseName, id='', unit_name=''):
        self.time =datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        prefix = self.time
        if id != '':
            prefix = id
        prefix = prefix+'_' + unit_name + '+' + TestCaseName
        self.data_logger = DataLogger(prefix)
        self.checker = Checker(prefix)
        self.TestCaseName=TestCaseName
        self.prefix = prefix

        # create logger with 'spam_application'
        logger = logging.getLogger(prefix)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler('db/' + prefix + '.log')
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        #ch = logging.StreamHandler()
        #ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        #ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)
        #logger.addHandler(ch)

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

    def add_test_case(self, name, units, tags=[]):
        self.db.insert({'name': name,
                        'units': units,
                        'tags' : tags,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_test_cases(self):
        return self.db.all()

    def get_test_cases_units(self, unit_list):
        test_cases = []
        for unit in unit_list:
            test_cases += self.db.search(self.query.units.any(str(unit))) #todo: shouldn't work with 'unit_' + unit
        return test_cases

import importlib

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

    def populate(self, unit_hierarchy, controllers, guis = {}):

        for su in unit_hierarchy.get_sub_units(self.name, False):
            self.add_sub_unit(su)
            self.sub_unit[su].populate(unit_hierarchy, controllers, guis)

        try:
            ctrl = controllers.get_controller_instance(self.name)
            self.set_controller(ctrl) #
        except:
            self.set_controller(None)
            print("Warning: Controller for " + self.name + " not found")


        try:
            gui = guis.get_gui_instance(self.name, ctrl)
            self.set_gui(gui) # todo: instance self.sub_unit could also be passed to controller
        except:
            self.set_gui(None)
            print("Warning: GUI for " + self.name + " not found")


class UnitHierarchy(object):

    # todo: return unit dictionay, then write a function which can filter for tags and one that returns just a list of names
    # this allows for easy filtering for tags in units and test cases: filterout and filter keep (standard)
    #
    # todo: ++++=++++++++++++++++++++++++++++++++++++++++++
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
        unitfound = self.db.search(where('UnitName') == unit_name)[0]
        return unitfound['Controller']

    def get_controller_parameters(self, unit_name):
        unitfound = self.db.search(where('UnitName') == unit_name)[0]
        return unitfound['Parameters']

    def get_controller_instance(self, unit_name):
        ctrl_name = self.get_controller(unit_name)
        p, m = ctrl_name.rsplit('.', 1)
        mod = importlib.import_module(p)
        ctrl = getattr(mod, m)
        parameters = self.get_controller_parameters(unit_name)
        sub_units = None # todo get subunits ????????????????
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
        unitfound = self.db.search(where('UnitName') == unit_name)[0]
        return unitfound['GuiView'], unitfound['GuiController']

    def get_gui_instance(self, unit_name, controller):
        gui_ctrl = self.get_gui(unit_name)[1]
        p, m = gui_ctrl.rsplit('.', 1)
        mod = importlib.import_module(p)
        ctrl = getattr(mod, m)

        gui_view = self.get_gui(unit_name)[0]
        p, m = gui_view.rsplit('.', 1)
        mod = importlib.import_module(p)
        view = getattr(mod, m)

        gv = view()
        gc = ctrl(gv, controller)
        return gc




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
