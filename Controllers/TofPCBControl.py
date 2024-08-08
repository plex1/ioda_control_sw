import time
import numpy as np

from TestEnv.TestEnvStructure import BaseController
from Gepin.Gepin import BaseGepinRegisters
from csr.csr_tofpcb import csr_tofpcb


class TofPcbControl(BaseController, BaseGepinRegisters):

    def __init__(self, testif, sub_units = [], parameters={}):

        BaseController.__init__(self, testif, sub_units, parameters)
        #csr_def = csr_tofpcb()
        csr_def = "csr/TofPCB.cheby" #file also used in embedded sw
        BaseGepinRegisters.__init__(self, csr_def, testif['gepin_tofpcb'], parameters, -2)

        self.debug = 0


    def write_back_test(self):
        txdata = 0x1234
        self.registers.reg['var4'].write(txdata)
        rxdata = self.registers.reg['var4'].read()
        print("back: " + hex(rxdata))
        if txdata == rxdata:
            return True
        else:
            return False