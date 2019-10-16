from TestEnv.TestEnvStructure import AbstractTestCase
from TofControl import TofControl
from TofProcessing import TofProcessing
import numpy as np
import matplotlib.pyplot as plt


class TestCaseID(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None):
        self.testif = testif
        TestCaseName = 'TestCaseID'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)
        registers = self.controller.registers
        self.checker.check('is_equal', registers.reg['id'].read(), 0x1a, 'Read out ID')

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')


class TestCaseCalibrate(AbstractTestCase):

    def __init__(self,id, unit_name='', testif={}, controller=None):
        self.testif = testif
        TestCaseName = 'TestCaseCalibrate'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)

        n_taps = 100
        clock_period = 25  # 25ns 40MHz clock

        # init tofcontrol
        tofc = self.controller
        tofc.init()
        tofc.cal_time = 1

        # init tof processing
        tofp = TofProcessing()
        tofp.use_correlation = False
        tofp.use_midpoint = True
        tofp.calibrate_bins = True

        # calibrate
        calib_histograms = tofc.get_calibration_histograms(n_taps)
        tofp.calibration_update(calib_histograms[0], calib_histograms[1], clock_period)

        # verify calibration via random bin distribution
        std_norm = tofc.verify_calibration(tofp.dt_per_bin)
        print('cd_norm_std = ' + str(std_norm))
        self.checker.check('is_smaller', std_norm, 0.01, 'Check cd_norm_std [in ns] upper bound')

        # verify calibration via period measurement
        period_std = tofc.verify_calibartion_period(tofp, clock_period)
        print('period_std  = ' + str(period_std))
        self.checker.check('is_smaller', period_std, 0.03, 'Check period_std [in ns] upper bound')

        self.data_logger.add_data('calibration_histograms_pulse', calib_histograms[0].histogram)
        self.data_logger.add_data('calibration_histograms_rand', calib_histograms[1].histogram)
        self.data_logger.add_data('dt_per_bin', tofp.dt_per_bin.tolist())

    def evaluate(self):
        AbstractTestCase.evaluate(self)

        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        hist_pulse = self.data_logger.get_data("calibration_histograms_pulse")
        hist_rand = self.data_logger.get_data("calibration_histograms_rand")
        dt_per_bin = self.data_logger.get_data("dt_per_bin")

        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(hist_pulse), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('Tap')
        plt.ylabel('Counts')
        plt.savefig('data/' + self.prefix+'_pulse.png')

        plt.figure(1)
        plt.clf()
        plt.plot(np.array(hist_rand), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('Tap')
        plt.ylabel('Counts')
        plt.savefig('data/' + self.prefix+'_rand.png')

        plt.figure(2)
        plt.clf()
        plt.plot(np.array(dt_per_bin), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('Tap')
        plt.ylabel('Delay per Tap [ns]')
        plt.savefig('data/' + self.prefix+'_dtperbin.png')


class TestCaseMeasure(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None):
        self.testif = testif
        TestCaseName = 'TestCaseMeasure'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)

        variable_slot = True

        # init tofcontrol
        tofc = self.controller
        registers = tofc.registers
        tofc.init()
        tofc.cal_time = 1
        tofc.calibrate()

        # settings for time measurements
        registers.reg['trigTestPeriod'].write(20)
        registers.reg['ringOscSetting'].write(0)
        slot_select = 6
        registers.reg['histogramFilter'].write(2 ** 16 + slot_select)

        delta = 1
        delay_set = range(0, 141, delta)
        delay_tmeas = []

        for delay in delay_set:
            tofc.set_delay(delay)
            if variable_slot:
                slot_select = registers.reg['averageFilter'].read() + 1 # todo: tbd +1?
                print('Slot select' + str(slot_select))
                registers.reg['histogramFilter'].write(2 ** 16 + slot_select)
            time_meas = tofc.measure_delay()
            delay_tmeas.append(time_meas)
            print("time: " + str(time_meas))

        self.data_logger.add_data('delay_set', (np.array(delay_set) * 0.25).tolist())
        self.data_logger.add_data('delay_meas', delay_tmeas)

    def evaluate(self):
        AbstractTestCase.evaluate(self)

        # post processing
        delay_set = self.data_logger.get_data("delay_set")
        delay_tmeas = self.data_logger.get_data("delay_meas")

        delay_tmeas_rel = np.array(delay_tmeas) - delay_tmeas[0]
        delay_tmeas_rel = delay_tmeas_rel / delay_tmeas_rel[-1] * delay_set[-1]

        delay_error = delay_tmeas_rel - np.linspace(0.0, delay_set[-1], num=len(delay_tmeas_rel))

        delay_tmeas_diff_rel = np.diff(delay_tmeas_rel)

        self.checker.check('is_smaller_all', np.abs(delay_error).tolist(), 0.40, 'Check error bound')
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_set), delay_tmeas)
        plt.grid(True, which="both")
        plt.xlabel('Delay Setting [ns]')
        plt.ylabel('Delay Measured [ns]')
        plt.savefig('data/' + self.prefix+'_measured.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_set), delay_tmeas_rel)
        plt.grid(True, which="both")
        plt.xlabel('Delay Setting [ns]')
        plt.ylabel('Delay Measured, offset corrected / gain corrected [ns]')
        plt.savefig('data/' + self.prefix+'_measured_rel.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_set), delay_error*1000, 'x-')
        plt.grid(True, which="both")
        plt.xlabel('Delay Setting [ns]')
        plt.ylabel('Delay Measured Error, offset corrected / gain corrected [ps]')
        plt.savefig('data/' + self.prefix+'_measured_rel_err.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_set[0:-1]), delay_tmeas_diff_rel * 1000, 'x-')
        plt.grid(True, which="both")
        plt.xlabel('Delay Setting [ns]')
        plt.ylabel('Delay Measured Difference, offset corrected / gain corrected [ps]')
        plt.savefig('data/' + self.prefix + '_measured_rel_diff.png')

