
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from csr_tofperipheral_manual import csr_tofperipheral
from registers import Registers
import collections
from Checker import AbstractTestCase
from RequirementsManager import RequirementsManager


import TofTestCases


def list_test_cases():
    # list of test cases
    collections.OrderedDict()
    test_cases = collections.OrderedDict([('Id', TofTestCases.TestCaseID),
                                          ('Calibrate', TofTestCases.TestCaseCalibrate),
                                          ('Measure', TofTestCases.TestCaseMeasure)])
    return test_cases

def create_testif():
    # init interface
    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    # init registers
    test_csri = csr_tofperipheral()
    registers = Registers(gepin)
    registers.offset = 0xF0030000
    registers.populate(test_csri)

    # define framework
    fw={}
    fw['registers'] = registers
    return fw


def main():

    # create test interfaces for tester
    testif = create_testif()

    # list of test cases
    test_cases = list_test_cases()

    id = AbstractTestCase.gen_id()

    # execute test cases
    for name in test_cases:
        print('Analyzig Test Case: ' + name)
        tc = test_cases[name](id, testif)
        tc.execute()


def analyze(id):

    # list of test cases
    test_cases = list_test_cases()

    # execute test cases
    for name in test_cases:
        print('Evaluating Test Case: ' + name)
        tc = test_cases[name](id)
        tc.evaluate()

def collect_results(id):

    # list of test cases
    test_cases = list_test_cases()
    rm = RequirementsManager()

    # execute test cases
    for name in test_cases:
        tc = test_cases[name](id)
        rm.add_checker(tc.checker)

    rm.collect_checks()
    rm.check_requirements()
    rm.print_results()

if __name__ == "__main__":
    #main()
    id = '20190802-183801'
    analyze(id)
    collect_results(id)

