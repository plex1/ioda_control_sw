from tinydb import TinyDB, Query, where
import datetime


class TestCases(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_testcases.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_test_case(self, name, tags):
        self.db.insert({'Name': name,
                        'tags' : tags, #['unit_' + tags[0]],
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_test_cases(self):
        test_case_list = []
        for item in self.db.all():
            test_case_list.append(item['Name'])
        return test_case_list

    def get_test_cases_units(self, unit_list):
        test_cases = []
        for unit in unit_list:
            test_cases += self.db.search(self.query.tags.any(str(unit))) #todo: shouldn't work with 'unit_' + unit
        test_case_list = []
        for item in test_cases:
            test_case_list.append(item['Name'])
        return test_case_list

import importlib

class Unit(object):

    def __init__(self, name, testif):
        self.ctrl = None
        self.sub_unit={}
        self.name = name
        self.testif = testif

    def set_controller(self, ctrl):
        self.ctrl = ctrl

    def add_sub_unit(self, name):
        self.sub_unit[name] = Unit(name, self.testif)

    def populate(self, unit_hierarchy, controllers):

        for su in unit_hierarchy.get_sub_units(self.name, False):
            self.add_sub_unit(su)
            self.sub_unit[su].populate(unit_hierarchy, controllers)

        try:
            ctrl_name = controllers.get_controller(self.name)
            p, m = ctrl_name.rsplit('.', 1)
            mod = importlib.import_module(p)
            ctrl = getattr(mod, m)
            self.set_controller(ctrl(self.testif, self.sub_unit)) # todo: instance self.sub_unit could also be passed to controller
        except:
            self.set_controller(None)
            print("Controller for" + self.name + " not found")


class UnitHierarchy(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_module_hierarchy.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_unit(self, name, sub_units):
        self.db.insert({'Name': name,
                        'sub_units' : sub_units,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })

    def get_sub_units(self, unit_name, recursive=True):
        unitfound = self.db.search(where('Name') == unit_name)
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


class Controllers(object):

    def __init__(self, prefix='1', purge=True):
        self.db = TinyDB('db/' + prefix +'_controllers.json')
        if purge:
            self.db.purge_tables()
        self.query = Query()

    def add_controller(self, unit_name, controller, tags=[]):
        self.db.insert({'UnitName': unit_name,
                        'Controller' : controller,
                        'Tags' : tags,
                        'Time': datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
                        })
    def get_controller(self, unit_name):
        unitfound = self.db.search(where('UnitName') == unit_name)[0]
        return unitfound['Controller']


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

    print(tc.get_test_cases())
    print(tch.get_sub_units_incl('ioda', True))
    print(tc.get_test_cases_units(tch.get_sub_units_incl('ioda', False)))
    print(tc.get_test_cases_units(tch.get_sub_units_incl('ioda')))


if __name__ == "__main__":
    main()
