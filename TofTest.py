
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from csr_tofperipheral_manual import csr_tofperipheral
from registers import Registers
import collections
from Checker import AbstractTestCase


import TofTestCases


def list_test_cases():
    # list of test cases
    collections.OrderedDict()
    test_cases = collections.OrderedDict([('Id', TofTestCases.TestCaseID),
                                          ('Calibrate', TofTestCases.TestCaseCalibrate),
                                          ('Measure', TofTestCases.TestCaseMeasure)])
    return test_cases

def create_framework():
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

    # create framework for test
    fw = create_framework()

    # list of test cases
    test_cases = list_test_cases()

    id = AbstractTestCase.gen_id()

    # execute test cases
    for name in test_cases:
        print('Analyzig Test Case: ' + name)
        tc = test_cases[name](fw, id)
        tc.execute()


def analyze(id):

    # define framework
    fw = {} # none needed for analyzing

    # list of test cases
    test_cases = list_test_cases()

    # execute test cases
    for name in test_cases:
        print('Evaluating Test Case: ' + name)
        tc = test_cases[name](fw, id)
        tc.evaluate()


if __name__ == "__main__":
    #main()
    id = '20190802-183801'
    analyze(id)

