
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
    tc.add_test_case('TofTestCases.TestCaseGetAllHistograms', ['toffpga'])
    tc.add_test_case('TofTestCases.TestCaseTofRegHistogram', ['toffpga'])
    tc.add_test_case('MotorTestCases.MotTestCaseID', ['motorcontroller_unit'], ['connection_test'])
    tc.add_test_case('MotorTestCases.MotTestCaseDrive', ['motorcontroller_unit'])
    tc.add_test_case('IodaTestCases.TestCaseID', ['ioda'], ['connection_test'])
    tc.add_test_case('IodaTestCases.TestCaseADC', ['ioda'])
    tc.add_test_case('IodaTestCases.TestCaseVapdCalibration', ['ioda'])
    tc.add_test_case('IodaTestCases.TestCaseAbsorptionCalibration', ['ioda'], ['testnow'])
    tc.add_test_case('IodaTestCases.TestCaseLine', ['ioda'])
    tc.add_test_case('IodaTestCases.TestCase3d', ['ioda'])



    return tc


def list_controllers():
    # list of test cases
    con = Controllers()
    con.add_controller('toffpga', 'TofControl.TofControl', {"gepin_offset": 0xF0030000})
    con.add_controller('motorcontroller_unit', 'MotorControl.MotorControl')
    con.add_controller('tofpcb', 'TofPCBControl.TofPcbControl')
    con.add_controller('ioda', 'IodaControl.IodaControl')
    return con


def list_guis():
    # list of test cases
    guis = Guis()
    guis.add_gui('toffpga', 'default', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')
    guis.add_gui('motorcontroller_unit','default', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')
    guis.add_gui('tofpcb', 'default', 'gui.GuiCtrl.GuiCtrl', 'gui.GuiView.GuiView')
    guis.add_gui('ioda', 'default', 'gui.DistanceMeasureGuiCtrl.DistanceMeasureGuiCtrl',
                 'gui.DistanceMeasureGuiView.DistanceMeasureGuiView')
    return guis


def create_hierarchy():
    tch = UnitHierarchy()
    tch.add_unit('ioda', ['motorcontroller_unit', 'toffpga', 'tofpcb'])
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])
    return tch


def create_testif():

    gepin_tcp = GepinPhyTcp("192.168.1.105", 9801)

    # init interface (Gepin: General Purpose Interface)
    #serial_port = '/dev/ttyS0'
    #serial_port = '/dev/ttyUSB0'
    #gepin_phy_serial = GepinPhySerial(serial_port, baudrate=9600)

    gepin = GepinMaster(gepin_tcp)

    gepin_tcp2 = GepinPhyTcp("192.168.1.105", 9802)
    gepin_motor = GepinMaster(gepin_tcp2)

    gepin_phy_tof = GepinPhyTcp("192.168.1.105", 9803)
    gepin_tofpcb = GepinMaster(gepin_phy_tof)

    # list test interfaces
    test_ifs={}
    test_ifs['gepin'] = gepin
    test_ifs['gepin_motor'] = gepin_motor
    test_ifs['gepin_tofpcb'] = gepin_tofpcb
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
    new = False  # to be adopted by user
    if new:
        id = AbstractTestCase.gen_id()
    else:
        id = '20200125-042610' #3d map
        id = '20200126-053540'


    # create Test Env Main Controller and set id
    main_controller = TestEnvMainControl(testif, hierarchy, controllers, testcases, requirements, guis)
    main_controller.set_id(id)

    # run test
    mode = 'gui'  # to be adopted by user
    if mode == 'test':

        print("Test ID: " + id)

        testenv_filter = TestEnvFilter()

        # filters: to be adapted by user
        #filter for units
        testenv_filter.unit_filter_type = 'keep'
        testenv_filter.units = ['ioda'] #toffpga

        #filter for test case tags
        #testenv_filter.units = ['toffpga']
        #testenv_filter.tc_filter_type = 'keep'
        #testenv_filter.tc_tags = ['connection_test']
        testenv_filter.tc_filter_type = 'keep'
        testenv_filter.tc_tags = ['testnow']


        if new:
            main_controller.run("ioda", True, testenv_filter)
        main_controller.analyze("ioda", True, testenv_filter)
        main_controller.collect_results("ioda", True, testenv_filter)

    if mode == 'gui':

        ioda_setup = main_controller.control()
        ioda_setup.sub_unit['tofpcb'].guis["default"].run_gui()
        ioda_setup.sub_unit['toffpga'].guis["default"].run_gui()
        ioda_setup.sub_unit['motorcontroller_unit'].guis["default"].run_gui()
        ioda_setup.guis["default"].run_gui()

        ioda_setup.sub_unit['toffpga'].guis["default"].gui_view.run_gtk()


if __name__ == "__main__":

    main()

