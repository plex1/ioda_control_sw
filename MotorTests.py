
from Gepin.GepinPhySerial import GepinPhySerial
from Gepin.GepinPhyTcp import GepinPhyTcp
from Gepin.Gepin import GepinMaster
from TestEnv.TestEnvStructure import AbstractTestCase, TestEnvFilter
from TestEnv.TestEnvRequirements import RequirementsManager
from TestEnv.TestEnvStructure import TestCases
from TestEnv.TestEnvStructure import UnitHierarchy
from TestEnv.TestEnvStructure import Controllers
from TestEnv.TestEnvStructure import Guis
from TestEnv.TestEnvStructure import TestEnvMainControl

# Define the project setup -------------------------------------------------------------

def list_test_cases():
    # list of test cases
    tc = TestCases()
    tc.add_test_case('TestCases.MotorTestCases.MotTestCaseID', ['motorcontroller_unit'], ['connection_test','testnow'])
    tc.add_test_case('TestCases.MotorTestCases.MotTestCaseDrive', ['motorcontroller_unit'])
    tc.add_test_case('TestCases.MotorTestCases.MotTestCaseDriveShowCase', ['motorcontroller_unit'], ['testnow'])

    return tc


def list_controllers():
    # list of test controllers corresponding to each unit
    con = Controllers()
    con.add_controller('motorcontroller_unit', 'Controllers.MotorControl.MotorControl')
    return con


def list_guis():
    # list of test gui, with controller and view for each unit
    guis = Guis()
    guis.add_gui('motorcontroller_unit','default', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')
    return guis


def create_hierarchy():
    # create a hierarchy of the units with 'ioda' being the main unit
    tch = UnitHierarchy()
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])
    return tch


def create_testif():

    # creates interfaces


    # in case of using uart instead of tcp, another physical layer needs to be instantiated
    serial_port = 'COM5'
    gepin_phy_serial = GepinPhySerial(serial_port, baudrate=9600)
    gepin_motor = GepinMaster(gepin_phy_serial)

    # list test interfaces
    test_ifs={}
    test_ifs['gepin_motor'] = gepin_motor
    return test_ifs

# End Define the project setup ---------------------------------------------------------

def main():

    # create test TestEnv framework
    testif = create_testif()
    testcases = list_test_cases()
    requirements = RequirementsManager() # no requirements defined
    hierarchy = create_hierarchy()
    controllers = list_controllers()
    controllers.set_testif(testif)
    guis = list_guis()

    # test id
    new = True  # False: process existing data (don't run execute, only evaluate)
    # select id of run

    id = AbstractTestCase.gen_id()

    # create Test Environment and set id
    main_controller = TestEnvMainControl(testif, hierarchy, controllers, testcases, requirements, guis)
    main_controller.set_id(id)

    # run test
    mode = 'test'  # to be adopted by user
    if mode == 'test':

        print("Test ID: " + id)

        testenv_filter = TestEnvFilter()

        # filters: to be adapted by user,
        # with these only a subset of the testcases can be selected
        #filter for units
        testenv_filter.unit_filter_type = 'keep'
        testenv_filter.units = ['motorcontroller_unit']

        #filter for test case tags
        testenv_filter.tc_filter_type = 'keep'
        testenv_filter.tc_tags = ['testnow']

        # run test cases for 'ioda' including all subunits
        if new:
            main_controller.run("motorcontroller_unit", True, testenv_filter)
        main_controller.analyze("motorcontroller_unit", True, testenv_filter)
        main_controller.collect_results("motorcontroller_unit", True, testenv_filter)

    if mode == 'gui':
        # run guis for units
        ioda_setup = main_controller.control()
        ioda_setup.sub_unit['motorcontroller_unit'].guis["default"].run_gui()
        ioda_setup.guis["default"].run_gui()
        ioda_setup.sub_unit['motorcontroller_unit'].guis["default"].gui_view.run_gtk()


if __name__ == "__main__":
    main()

