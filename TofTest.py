
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
import collections
from TestEnvStructure import AbstractTestCase
from TestEnvRequirements import RequirementsManager
from TestEnvStructure import TestCases
from TestEnvStructure import UnitHierarchy
from TestEnvStructure import Unit
from TestEnvStructure import Controllers

# Define the project setup -------------------------------------------------------------

def list_test_cases():
    # list of test cases
    tc = TestCases()
    tc.add_test_case('TofTestCases.TestCaseID', ['toffpga'])
    tc.add_test_case('TofTestCases.TestCaseCalibrate', ['toffpga'])
    tc.add_test_case('TofTestCases.TestCaseMeasure', ['toffpga'])

    return tc


def list_controllers():
    # list of test cases
    con = Controllers()
    con.add_controller('toffpga', 'TofControl.TofControl')

    return con


def create_hierarchy():
    tch = UnitHierarchy()
    tch.add_unit('ioda', ['motorcontroller_unit', 'toffpga'])
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])
    return tch


def create_testif():
    # init interface
    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    # define test interfaces
    test_ifs={}
    test_ifs['gepin'] = gepin
    return test_ifs

# End Define the project setup ---------------------------------------------------------


class TestEnvMainControl(object):

    def __init__(self, testif, hierarchy, controllers, testcases, requirements):
        self.testif = testif
        self.hierarchy = hierarchy
        self.controllers = controllers
        self.testcases = testcases
        self.requirements = requirements
        self.id = "id1"

    def set_id(self, id):
        self.id = id

    def run(self, unit='', recursive=True):

        # create test interfaces for tester
        testif = self.testif

        # list of test cases
        if unit == '':
            test_cases = self.testcases.get_test_cases()
        else:
            if recursive:
                test_cases = self.testcases.get_test_cases_units(self.hierarchy.get_sub_units_incl(unit))
            else:
                test_cases = self.testcases.get_test_cases_units([unit])

        # execute test cases
        for name in test_cases:
            print('Running Test Case: ' + name)
            tc = eval(name)(self.id, self.testif) # test cases classes could also be populated in external function such as in unit.populate
            tc.execute()

    def analyze(self, unit = '', recursive=True):

        # list of test cases
        if unit == '':
            test_cases = self.testcases.get_test_cases()
        else:
            if recursive:
                test_cases = self.testcases.get_test_cases_units(self.hierarchy.get_sub_units_incl(unit))
            else:
                test_cases = self.testcases.get_test_cases_units([unit])


        # execute test cases
        for name in test_cases:
            print('Evaluating Test Case: ' + name)
            tc = eval(name)(self.id) # test cases classes could also be populated in external function such as in unit.populate
            tc.evaluate()

    def gen_setup(self, hierarchy, controllers, testif, top_unit = 'ioda'):
        ioda_setup = Unit(top_unit, testif)
        ioda_setup.populate(hierarchy, controllers)
        return ioda_setup

    def control(self):
        ioda_setup = self.gen_setup(self.hierarchy, self.controllers, self.testif)
        print('Read: ID=' + hex(ioda_setup.sub_unit['toffpga'].testif['registers'].reg['id'].read()))
        return ioda_setup

    def collect_results(self):

        # list of test cases
        test_cases = self.testcases
        rm = self.requirements

        # collect checkers
        for name in test_cases:
            tc = test_cases[name](self.id)
            rm.add_checker(tc.checker)

        rm.collect_checks()
        rm.check_requirements()
        rm.print_results()

def main():

    testif = create_testif()
    testcases = list_test_cases()
    requirements = RequirementsManager()
    hierarchy = create_hierarchy()
    controllers = list_controllers()

    id = AbstractTestCase.gen_id()
    #id = '20190802-183801'

    main_controller = TestEnvMainControl(testif, hierarchy, controllers, testcases, requirements)
    main_controller.set_id(id)
    main_controller.run()
    main_controller.control()
    main_controller.analyze()
    main_controller.collect_results()

if __name__ == "__main__":

    main()

