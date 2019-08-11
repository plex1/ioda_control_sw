import time
from TofProcessing import HistogramProcessing
from TofProcessing import TofProcessing
import numpy as np

class TofControl(object):

    def __init__(self, testif, sub_unit = []): # todo abstract class for controllers with this constructor
        self.tofregs = testif['registers']
        self.debug = 0
        self.cal_time = 0.5
        self.n_taps = 100
        self.clock_period = 25  # 25ns 40MHz clock
        self.sub_unit = []

    def modes(self, modename):
        modedef = {'reset': 0, 'record': 1, 'resetaddr': 3, 'read': 2}
        return modedef[modename]

    def init(self):
        pass

    def set_delay(self, delay):
        self.tofregs.delay.write(delay)

    def get_delay(self):
        return self.tofregs.delay.read()

    def set_mode(self, mode):
        self.tofregs.histMode.write(mode)

    def get_histogram(self, n_taps, period=0.5):
        self.set_mode(self.modes("reset"))
        self.set_mode(self.modes("record"))
        time.sleep(period)  # time to acquire data
        self.set_mode(self.modes("resetaddr"))
        self.set_mode(self.modes("read"))
        self.tofregs.histValues.read()
        self.tofregs.histValues.read()
        values = self.tofregs.histValues.read_fifo(n_taps)
        return values

    def get_calibration_histograms(self, n_taps):
        self.tofregs.reg['trigTestPeriod'].write(20)

        # calibrate
        self.tofregs.histogramFilter.write(0)  # filter off

        self.tofregs.reg['ringOscSetting'].write(4)  # set to internal Oscillator
        values = self.get_histogram(n_taps, self.cal_time)
        hist_rand = HistogramProcessing(values)

        self.tofregs.reg['ringOscSetting'].write(0)  # set to external input
        self.set_delay(20)
        values = self.get_histogram(n_taps, self.cal_time)
        hist_pulse = HistogramProcessing(values)

        return [hist_pulse, hist_rand]

    def calibrate(self):
        # init tof processing
        self.tofp = TofProcessing()
        self.tofp.use_correlation = False
        self.tofp.use_midpoint = True
        self.tofp.calibrate_bins = True

        # calibrate
        calib_histograms = self.get_calibration_histograms(self.n_taps)
        self.tofp.calibration_update(calib_histograms[0], calib_histograms[1], self.clock_period)

    def verify_calibration(self, dt_per_bin):
        n_taps = len(dt_per_bin)
        # verify calibration
        self.tofregs.reg['ringOscSetting'].write(4)  # set to internal Oscillator
        values = self.get_histogram(n_taps, self.cal_time)
        corrected_distribution = np.array(values) / np.array(dt_per_bin)
        cd_norm = corrected_distribution / np.mean(corrected_distribution)
        cd_norm_std = np.sqrt(np.var(cd_norm))
        return float(cd_norm_std)

    def verify_calibartion_period(self, tofp, clock_period):
        n_taps = len(tofp.dt_per_bin)
        # settings for time read
        self.tofregs.reg['trigTestPeriod'].write(20)
        self.tofregs.ringOscSetting.write(0)  # set to external input
        self.tofregs.histogramFilter.write(0)  # no slot select

        step_size = 10
        delay_set = range(0, 151, step_size)
        period_dev_meas = []

        for delay in delay_set:
            self.set_delay(delay)
            values = self.get_histogram(n_taps, self.cal_time)
            if self.debug > 0: print(str(values))

            # period estimation
            hp0 = HistogramProcessing(values)
            hp1 = HistogramProcessing(values.copy())
            hp0.prune_keep_group(1)
            hp1.prune_keep_group(2)

            t0 = tofp.get_time(hp0, 0)
            t1 = tofp.get_time(hp1, 0)
            if self.debug >0: print("t0= " + str(t0) + " t1= " + str(t1))
            period_meas = - (t1 - t0)
            perod_deviation = period_meas - clock_period
            period_dev_meas.append(perod_deviation)
            if self.debug >0: print("Period deviation = " + str(perod_deviation))

        if self.debug >0: print("Period deviation: " + str(period_dev_meas))
        period_std = np.sqrt(np.var(np.array(period_dev_meas)))
        if self.debug >0: print("Period deviation std: " + str(period_std))
        return float(period_std)

    def measure_delay(self):
        time_meas = self.measure_delay_tofp(self.tofp, self.n_taps)
        return time_meas

    def measure_delay_tofp(self, tofp, n_taps):

        slot_select = self.tofregs.reg['averageFilter'].read()
        slot_select = int(slot_select+1)
        self.tofregs.reg['histogramFilter'].write(2 ** 16 + slot_select)

        hp = HistogramProcessing()
        values = self.get_histogram(n_taps, 1)
        hp.set_histogram(values)
        hp.prune_keep_group(0)

        time_meas = tofp.get_time(hp, slot_select)
        return time_meas




