
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from csr_tofperipheral_manual import csr_tofperipheral
from registers import Registers
import collections
from Checker import AbstractTestCase
from RequirementsManager import RequirementsManager
from TestCases import TestCases
from TestCases import UnitHierarchy
from TestCases import Unit
from TestCases import Controllers


import TofTestCases


def list_test_cases():
    # list of test cases
    collections.OrderedDict()
    test_cases = collections.OrderedDict([('Id', TofTestCases.TestCaseID),
                                          ('Calibrate', TofTestCases.TestCaseCalibrate),
                                          ('Measure', TofTestCases.TestCaseMeasure)])
    return test_cases

def list_test_cases2():
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

def gen_hierarchy():
    tch = UnitHierarchy()
    tch.add_unit('ioda', ['motorcontroller_unit', 'toffpga'])
    tch.add_unit('motorcontroller_unit', ['motorcontrollerpower_unit'])
    return tch

def gen_setup(hierarchy, controllers, testif):
    ioda_setup = Unit('ioda', testif)
    ioda_setup.populate(hierarchy, controllers)
    return ioda_setup

def create_testif():
    # init interface
    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    # init registers
    test_csri = csr_tofperipheral()
    registers = Registers(gepin)
    registers.offset = 0xF0030000
    registers.populate(test_csri)

    # define test interfaces
    test_ifs={}
    test_ifs['registers'] = registers
    test_ifs['gepin'] = gepin
    return test_ifs


def main(id):

    # create test interfaces for tester
    testif = create_testif()

    # list of test cases
    test_cases = list_test_cases()


    # execute test cases
    for name in test_cases:
        print('Analyzig Test Case: ' + name)
        tc = test_cases[name](id, testif)
        tc.execute()


def analyze(id):

    # list of test cases
    hierarchy = gen_hierarchy()
    test_cases = list_test_cases2().get_test_cases_units(hierarchy.get_sub_units_incl('ioda'))

    # execute test cases
    for name in test_cases:
        print('Evaluating Test Case: ' + name)
        tc = eval(name)(id) # test cases classes could also be populated in external function such as in unit.populate
        tc.evaluate()

def control():

    testif =  create_testif()
    hierarchy = gen_hierarchy()
    controllers = list_controllers()

    ioda_setup = gen_setup(hierarchy, controllers, testif)

    print('Read: ID=' + hex(ioda_setup.sub_unit['toffpga'].testif['registers'].reg['id'].read()))

def collect_results(id):

    # list of test cases
    test_cases = list_test_cases()
    rm = RequirementsManager()

    # collect checkers
    for name in test_cases:
        tc = test_cases[name](id)
        rm.add_checker(tc.checker)

    rm.collect_checks()
    rm.check_requirements()
    rm.print_results()

if __name__ == "__main__":

    id = AbstractTestCase.gen_id()
    #id = '20190802-183801'

    print("ID: " + id)

    main(id)
    control()
    analyze(id)
    collect_results(id)

