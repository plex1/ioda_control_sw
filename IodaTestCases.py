from TestEnv.TestEnvStructure import AbstractTestCase
from MotorControl import MotorControl
import numpy as np
import matplotlib.pyplot as plt
import time
from TofProcessing import TofProcessing
import numpy as np
import matplotlib.pyplot as plt


class TestCaseID(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseID'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registersTofFPGA = self.setup.sub_unit['toffpga'].ctrl.registers
        self.checker.check('is_equal', registersTofFPGA.reg['id'].read(), 0x1a, 'Read out ID')

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

class TestCaseADC(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseID'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers

        n_taps = 100
        clock_period = 25  # 25ns 40MHz clock

        registers_toffpga.reg['control'].field['edge'].clear()
        print("control reg: " + hex(registers_toffpga.reg['control'].read()))
        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        registers_tofpcb.reg['pwm_comp_level1'].write(132)
        tofc.calibrate()
        print("calbrated")

        #registers_toffpga.reg['control'].field['edge'].clear()
        time.sleep(0.1)

        delay_measured=[]
        threshold_set = range(129, 166)
        for threshold in threshold_set:
            registers_tofpcb.reg['pwm_comp_level1'].write(threshold)
            time.sleep(0.1)
            slot_select = registers_toffpga.reg['averageFilter'].read() + 0  # todo: tbd +1?
            print('Slot select' + str(slot_select))
            registers_toffpga.reg['histogramFilter'].write(2 ** 16 + slot_select)
            delay_meas1 = tofc.measure_delay()
            print(str(delay_meas1))
            delay_measured.append(delay_meas1)

        registers_toffpga.reg['control'].field['edge'].set()
        delay_measured2 = []
        for threshold in threshold_set:
            registers_tofpcb.reg['pwm_comp_level1'].write(threshold)
            time.sleep(0.1)
            slot_select = registers_toffpga.reg['averageFilter'].read() + 0  # todo: tbd +1?
            print('Slot select' + str(slot_select))
            registers_toffpga.reg['histogramFilter'].write(2 ** 16 + slot_select)
            delay_meas1 = tofc.measure_delay()
            print(str(delay_meas1))
            delay_measured2.append(delay_meas1)



        self.data_logger.add_data('threshold_set', np.array(threshold_set).tolist())
        self.data_logger.add_data('delay_measured', delay_measured)
        self.data_logger.add_data('delay_measured2', delay_measured2)


    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing
        threshold_set = self.data_logger.get_data("threshold_set")
        delay_measured = self.data_logger.get_data("delay_measured")
        delay_measured2 = self.data_logger.get_data("delay_measured2")

        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_measured), threshold_set, 'x-')
        plt.plot(np.array(delay_measured2), threshold_set, 'x-')
        plt.xlabel('Delay Measured [ns]')
        plt.ylabel('Threshold setting [LSB]')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_th_adc.png')

