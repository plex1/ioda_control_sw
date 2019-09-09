
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
import collections
from TestEnvStructure import AbstractTestCase
from TestEnvRequirements import RequirementsManager
from TestEnvStructure import TestCases
from TestEnvStructure import UnitHierarchy
from TestEnvStructure import Unit
from TestEnvStructure import Controllers
from TestEnvStructure import Guis
import TofTestCases

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

def list_guis():
    # list of test cases
    guis = Guis()
    guis.add_gui('toffpga', 'GuiCtrl.GuiCtrl', 'GuiView.GuiView')

    return guis


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

# todo mode Main control to TestEnv file
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
        for test_case in test_cases:
            # todo add filtering for test case tags
            print('Running Test Case: ' + test_case['name'])
            for test_case_unit in test_case['units']:
                if unit == '' or unit == unit:
                    tc = eval(test_case['name'])(self.id, test_case_unit, self.testif,
                                                 self.controllers.get_controller_instance(test_case_unit)) #todo: sub units instances from setup
                    # todo: test cases classes could also be populated in external function such as in unit.populate
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


        # evaluate test cases
        for test_case in test_cases:
            # todo add filtering for tags
            print('Running Test Case: ' + test_case['name'])
            for test_case_unit in test_case['units']:
                if unit == '' or unit == unit:
                    tc = eval(test_case['name'])(self.id, test_case_unit)
                    # todo: test cases classes could also be populated in external function such as in unit.populate
                    tc.evaluate()

    def gen_setup(self, hierarchy, controllers, testif, guis={}, top_unit = 'ioda',):
        ioda_setup = Unit(top_unit, testif)
        ioda_setup.populate(hierarchy, controllers, guis)
        return ioda_setup

    def control(self):
        ioda_setup = self.gen_setup(self.hierarchy, self.controllers, self.testif, self.guis)
        print('Read: ID=' + hex(ioda_setup.sub_unit['toffpga'].ctrl.registers.reg['id'].read()))
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
    controllers.set_testif(testif)
    guis = list_guis()

    id = AbstractTestCase.gen_id()
    #id = '20190802-183801'

    main_controller = TestEnvMainControl(testif, hierarchy, controllers, testcases, requirements, guis)
    main_controller.set_id(id)

    mode = 'gui'
    if mode == 'test':
        main_controller.run()
        main_controller.analyze()
        main_controller.collect_results()
    if mode == 'gui':
        ioda_setup = main_controller.control()
        ioda_setup.sub_unit['toffpga'].gui.run_gui()

    #todo: most imporant todos:
    #todo: get all testcases as instances (used 3 times in run, analyze and collect results), collect results doesn't work at the moment
    #todo: add sub_units to controllers
    #todo: execute test cases in the order as defined
    #todo: put TestEnvMainControl in separate file

if __name__ == "__main__":

    main()

