
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from TestEnv.TestEnvStructure import AbstractTestCase
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

    #todo: execute test cases in the order as defined


if __name__ == "__main__":

    main()

