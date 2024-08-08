import time
from Library.TofProcessing import HistogramProcessing
from Library.TofProcessing import TofProcessing
import numpy as np

from TestEnv.TestEnvStructure import BaseController
from Gepin.Gepin import BaseGepinRegisters


class TofControl(BaseController, BaseGepinRegisters):

    def __init__(self, testif, sub_units=[], parameters={}):

        BaseController.__init__(self, testif, sub_units, parameters)
        csr_def = 'csr/TofPeripheral.json' #csr_tofperipheral()
        BaseGepinRegisters.__init__(self, csr_def, testif['gepin'], parameters)

        self.debug = 0
        self.cal_time = 0.5
        self.measure_time = 1
        self.n_taps = 100
        self.clock_period = 25  # 25ns 40MHz clock
        self.last_histogram = None

        #self.registers.reg['control'].field['edge'].clear()


    def modes(self, modename):
        modedef = {'reset': 0, 'record': 1, 'resetaddr': 3, 'read': 2}
        return modedef[modename]

    def enable_trig(self):
        self.registers.reg['control'].set_bit(6)

    def disable_trig(self):
        self.registers.reg['control'].clear_bit(6)

    def enable_lockin(self):
        self.registers.reg['control'].set_bit(7)

    def disable_lockin(self):
        self.registers.reg['control'].clear_bit(7)

    def init(self):
        self.enable_trig()

    def set_delay(self, delay):
        delay_inv = 0
        for i in range(8):
            if delay & 2**i:
                delay_inv = delay_inv + 2**(7-i)

        #self.registers.reg['delay'].write(delay)
        self.registers.reg['delay'].write(delay_inv) # temporary fix, correct fpga mapping

    def get_delay(self):
        return self.registers.reg['delay'].read()

    def set_mode(self, hist_mode):
         self.registers.reg['control'].field['histMode'].readModifyWrite(hist_mode)

    def get_histogram(self, n_taps, period=0.5):
        self.set_mode(self.modes("reset"))
        self.set_mode(self.modes("record"))
        time.sleep(period)  # time to acquire data
        self.set_mode(self.modes("resetaddr"))
        self.set_mode(self.modes("read"))
        self.registers.reg['histValues'].read() #remove first 2, why?? todo
        self.registers.reg['histValues'].read()
        values = self.registers.reg['histValues'].read_fifo(n_taps)
        return values

    def get_calibration_histograms(self, n_taps):
        self.registers.reg['trigTestPeriod'].write(20)

        # calibrate
        self.registers.reg['histogramFilter'].write(0)  # filter off

        self.registers.reg['ringOscSetting'].write(4)  # set to internal Oscillator
        values = self.get_histogram(n_taps, self.cal_time)
        hist_rand = HistogramProcessing(values)

        self.registers.reg['ringOscSetting'].write(0)  # set to external input
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

        self.init()

        # calibrate
        calib_histograms = self.get_calibration_histograms(self.n_taps)
        self.tofp.calibration_update(calib_histograms[0], calib_histograms[1], self.clock_period)

    def verify_calibration(self, dt_per_bin):
        n_taps = len(dt_per_bin)
        # verify calibration
        self.registers.reg['ringOscSetting'].write(4)  # set to internal Oscillator
        values = self.get_histogram(n_taps, self.cal_time)
        corrected_distribution = np.array(values) / np.array(dt_per_bin)
        cd_norm = corrected_distribution / np.mean(corrected_distribution)
        cd_norm_std = np.sqrt(np.var(cd_norm))
        return float(cd_norm_std)

    def verify_calibartion_period(self, tofp, clock_period):
        n_taps = len(tofp.dt_per_bin)
        # settings for time read
        self.registers.reg['trigTestPeriod'].write(20)
        self.registers.reg['ringOscSetting'].write(0)  # set to external input
        self.registers.reg['histogramFilter'].write(0)  # no slot select

        step_size = 10
        delay_set = range(0, 120, step_size)
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
        [time_meas, snr] = self.measure_delay_tofp(self.tofp, self.n_taps)
        return time_meas

    def measure_delay_snr(self):
        timesnr_meas = self.measure_delay_tofp(self.tofp, self.n_taps)
        return timesnr_meas

    def select_slot(self, n):
        self.registers.reg['histogramFilter'].write(2 ** 16 + n)

    def measure_delay_tofp(self, tofp, n_taps):

        slot_select = self.registers.reg['averageFilter'].read()
        slot_select = int(slot_select+1)
        slot_select = 7 #hack
        self.select_slot(slot_select)

        hp = HistogramProcessing()
        values = self.get_histogram(n_taps, self.measure_time)
        self.last_histogram = values.copy()
        hp.set_histogram(values)
        snr=hp.prune_keep_group(0)

        time_meas = tofp.get_time(hp, slot_select)
        return [time_meas, snr]


    def get_tofreg_histogram(self, n, rising=True):
        def get_edge(value, rising=True):

            first = (value & 1)

            prev = first
            for j in range(1,30):

                current = value & (1 << j)

                if current == prev:
                    return j
                    if (j % 2 == 0):
                        is_rising_edge = bool(current)
                    if (j % 2 == 1):
                        is_rising_edge = not bool(current)
                    if is_rising_edge and rising:
                        return j
                    if (not is_rising_edge) and (not rising):
                        return j

                prev = current

            return None
        histogram = [0]*32
        start = 2 #first two toregisters are not considered, see get_histogram
        b_len = 10000
        #tofregs =self.registers.reg['tofReg'].read_fifo(b_len)
        for i in range(0, b_len):
            tofreg= self.registers.reg['tofReg'].read() #tofregs[i]
            if tofreg < 0:
                tofreg += 2 **32 - 1
            edge = get_edge(tofreg>>2, rising)
            if edge is not None:
                #edge = edge -start
                if edge>0:
                    histogram[edge] = histogram[edge] +1
        return histogram






