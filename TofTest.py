
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from csr_tofperipheral_manual import csr_tofperipheral
from registers import Registers
from TofControl import TofControl
from TofProcessing import HistogramProcessing
from TofProcessing import TofProcessing
import collections

import time
import numpy as np
import matplotlib.pyplot as plt

import TofTestCases

def main():

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

    # list of test cases

    collections.OrderedDict()
    test_cases =collections.OrderedDict([('Id', TofTestCases.TestCaseID),
                                        ('Calibrate', TofTestCases.TestCaseCalibrate),
                                         ('Measure', TofTestCases.TestCaseMeasure)])

    # execute test cases
    for name in test_cases:
        print('Test Case: ' + name)
        tc = test_cases[name](fw)
        tc.execute()

def analyze(id):

    # init interface
    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    # init registers
    test_csri = csr_tofperipheral()
    registers = Registers(gepin)
    registers.offset = 0xF0030000
    registers.populate(test_csri)

    # define framework
    fw = {}
    fw['registers'] = registers

    # list of test cases

    collections.OrderedDict()
    test_cases = collections.OrderedDict([('Id', TofTestCases.TestCaseID),
                                          ('Calibrate', TofTestCases.TestCaseCalibrate),
                                          ('Measure', TofTestCases.TestCaseMeasure)])

    # execute test cases
    for name in test_cases:
        print('Test Case: ' + name)
        tc = test_cases[name](fw)
        tc.execute()

if __name__ == "__main__":
    main()
