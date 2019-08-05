from Checker import AbstractTestCase
from TofControl import TofControl
from TofProcessing import TofProcessing
import numpy as np


class TestCaseID(AbstractTestCase):

    def __init__(self, framework=[]):
        self.fw = framework
        TestCaseName = 'TestCaseID'
        super().__init__(TestCaseName)

    def execute(self):

        reg = self.fw['registers'].reg
        self.checker.check('is_equal', reg['id'].read(), 0x1a, 'Read out ID')

    def evaluate(self):
        return self.checker.num_errors == 0


class TestCaseCalibrate(AbstractTestCase):

    def __init__(self, framework=[]):
        self.fw = framework
        TestCaseName = 'TestCaseCalibrate'
        super().__init__(TestCaseName)

    def execute(self):

        n_taps = 100
        clock_period = 25  # 25ns 40MHz clock

        # init tofcontrol
        tofc = TofControl(self.fw['registers'])
        tofc.init()
        tofc.cal_time = 1

        # init tof processing
        tofp = TofProcessing()
        tofp.use_correlation = False
        tofp.use_midpoint = True
        tofp.calibrate_bins = True

        # calibrate
        calib_histograms = tofc.get_calibration_histograms(n_taps)
        tofp.calibrate(calib_histograms[0], calib_histograms[1], clock_period)

        # verify calibration via random bin distribution
        std_norm = tofc.verify_calibration(tofp.dt_per_bin)
        print('cd_norm_std = ' + str(std_norm))
        self.checker.check('is_smaller', std_norm, 0.01, 'Check cd_norm_std [in ns] upper bound')

        # verify calibration via period measurement
        period_std = tofc.verify_calibartion_period(tofp, clock_period)
        print('period_std  = ' + str(period_std))
        self.checker.check('is_smaller', period_std, 0.03, 'Check period_std [in ns] upper bound')

        self.logger.add_dataset('calibration_histograms pulse', calib_histograms[0].histogram)
        self.logger.add_dataset('calibration_histograms rand', calib_histograms[1].histogram)
        self.logger.add_dataset('tofp.dt_per_bin', tofp.dt_per_bin.tolist())

    def evaluate(self):
        return self.checker.num_errors == 0


class TestCaseMeasure(AbstractTestCase):

    def __init__(self, framework=[]):
        self.fw = framework
        TestCaseName = 'TestCaseMeasure'
        super().__init__(TestCaseName)

    def execute(self):

        registers = self.fw['registers']

        n_taps = 100
        clock_period = 25  # 25ns 40MHz clock
        variable_slot = True

        # init tofcontrol
        tofc = TofControl(registers)
        tofc.init()
        tofc.cal_time = 1

        # init tof processing
        tofp = TofProcessing()
        tofp.use_correlation = False
        tofp.use_midpoint = True
        tofp.calibrate_bins = True

        # calibrate
        calib_histograms = tofc.get_calibration_histograms(n_taps)
        tofp.calibrate(calib_histograms[0], calib_histograms[1], clock_period)

        # settings for time measurements
        registers.reg['trigTestPeriod'].write(20)
        registers.ringOscSetting.write(0)
        slot_select = 6
        registers.histogramFilter.write(2 ** 16 + slot_select)

        delay_set = range(10, 141, 1)
        delay_tmeas = []

        for delay in delay_set:
            tofc.set_delay(delay)
            if variable_slot:
                slot_select = registers.reg['averageFilter'].read()
                print('Slot select' + str(slot_select))
                registers.histogramFilter.write(2 ** 16 + slot_select)
            time_meas = tofc.measure_delay(tofp, n_taps)
            delay_tmeas.append(time_meas)
            print("time: " + str(time_meas))

        self.logger.add_dataset('calibration_histograms pulse', (np.array(delay_set)*0.25).tolist())
        self.logger.add_dataset('calibration_histograms rand', delay_tmeas)

    def evaluate(self):
        return self.checker.num_errors == 0

