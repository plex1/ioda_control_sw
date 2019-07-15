import time
from TofProcessing import HistogramProcessing
from TofProcessing import TofProcessing
import numpy as np

class TofControl(object):

    def __init__(self, regs):
        self.tofregs = regs
        self.debug = 1
        self.cal_time = 0.5

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

    def verify_calibration(self, dt_per_bin):
        n_taps = len(dt_per_bin)
        # verify calibration
        self.tofregs.reg['ringOscSetting'].write(4)  # set to internal Oscillator
        values = self.get_histogram(n_taps, self.cal_time)
        corrected_distribution = np.array(values) / np.array(dt_per_bin)
        cd_norm = corrected_distribution / np.mean(corrected_distribution)
        cd_norm_std = np.sqrt(np.var(cd_norm))
        return cd_norm_std

    def verify_calibartion_period(self, tofp, clock_period):
        n_taps = len(tofp.dt_per_bin)
        # settings for time read
        self.tofregs.reg['trigTestPeriod'].write(20)
        self.tofregs.ringOscSetting.write(0) # set to external input
        self.tofregs.histogramFilter.write(0) # no slot select

        delay_set = range(60, 171, 5)
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
        return period_std




