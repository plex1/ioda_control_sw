
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
    tc.add_test_case('TofTestCases.TestCaseID', ['toffpga'], ['connection_test'])
    tc.add_test_case('TofTestCases.TestCaseCalibrate', ['toffpga'])
    tc.add_test_case('TofTestCases.TestCaseMeasure', ['toffpga'])
    tc.add_test_case('MotorTestCases.MotTestCaseID', ['motorcontroller_unit'], ['connection_test'])
    tc.add_test_case('MotorTestCases.MotTestCaseDrive', ['motorcontroller_unit'])

    return tc


def list_controllers():
    # list of test cases
    con = Controllers()
    con.add_controller('toffpga', 'TofControl.TofControl', {"gepin_offset": 0xF0030000})
    con.add_controller('motorcontroller_unit', 'MotorControl.MotorControl')

    return con


def list_guis():
    # list of test cases
    guis = Guis()
    guis.add_gui('toffpga', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')
    guis.add_gui('motorcontroller_unit', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')

    return guis


def create_hierarchy():
    tch = UnitHierarchy()
    tch.add_unit('ioda', ['motorcontroller_unit', 'toffpga'])
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])
    return tch


def create_testif():

    gepin_tcp = GepinPhyTcp("192.168.1.105", 9801)

    # init interface (Gepin: General Purpose Interface)
    serial_port = '/dev/ttyS0' #'/dev/ttyUSB0'
    #gepin_phy = GepinPhySerial(serial_port, baudrate=115200)
    gepin = GepinMaster(gepin_tcp)

    gepin_tcp2 = GepinPhyTcp("192.168.1.105", 9802)
    gepin_motor = GepinMaster(gepin_tcp2)

    # list test interfaces
    test_ifs={}
    test_ifs['gepin'] = gepin
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
    new = True  # to be adopted by user
    if new:
        id = AbstractTestCase.gen_id()
    else:
        id = '20190916-134835'
        id = '20190916-154813'

    # create Test Env Main Controller and set id
    main_controller = TestEnvMainControl(testif, hierarchy, controllers, testcases, requirements, guis)
    main_controller.set_id(id)

    # run test
    mode = 'test'  # to be adopted by user
    if mode == 'test':

        testenv_filter = TestEnvFilter()

        # filters: to be adapted by user
        #filter for units
        testenv_filter.unit_filter_type = 'keep'
        testenv_filter.units = ['motorcontroller_unit']

        #filter for test case tags
        #testenv_filter.units = ['toffpga']
        #testenv_filter.tc_filter_type = 'keep'
        #testenv_filter.tc_tags = ['connection_test']

        if new:
            main_controller.run("ioda", True, testenv_filter)
        main_controller.analyze("ioda", True, testenv_filter)
        main_controller.collect_results("ioda", True, testenv_filter)

    if mode == 'gui':

        ioda_setup = main_controller.control()
        ioda_setup.sub_unit['toffpga'].gui.run_gui()
        #ioda_setup.sub_unit['motorcontroller_unit'].gui.run_gui()


if __name__ == "__main__":

    main()

