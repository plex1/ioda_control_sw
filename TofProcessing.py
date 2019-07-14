import numpy as np
import matplotlib.pyplot as plt


class HistogramProcessing(object):

    def __init__(self, histogram = None):
        self.histogram = histogram

    def set_histogram(self, histogram):
        self.histogram = histogram

    def get_num_taps(self):
        return len(self.histogram)

    def get_weighted_average(self):
        taps = np.arange(self.get_num_taps())
        return np.average(taps, weights=self.histogram)

    def prune_keep_group(self, n):
        group_nr = -1
        in_group = False
        min_detect = 100
        for i in range(1, self.get_num_taps()):
            if self.histogram[i] > min_detect:
                if not in_group:
                    in_group = True
                    group_nr = group_nr + 1
                if group_nr != n:
                    self.histogram[i] = 0  # prune
            else:
                in_group = False

    def plot_histogram(self):
        plt.figure(1)
        taps = np.arange(self.get_num_taps())
        plt.bar(taps, self.histogram, align='center')
        plt.xticks(taps, taps)
        plt.ylabel('occurrences')
        plt.title('histogram')
        plt.show()


class TofProcessing(object):

    def __init__(self):
        self.dt_per_bin = None
        self.t_per_bin = None
        self.clk_period = None

    def get_frac(self, val):
        return np.modf(val)[0]

    def get_int(self, val):
        return int(np.modf(val)[1])

    def calibrate(self, hist_pulse, hist_rand, clk_period):
        self.clk_period = clk_period
        values0 = hist_pulse.histogram.copy()
        values1 = hist_pulse.histogram.copy()
        h0 = HistogramProcessing(values0)
        h1 = HistogramProcessing(values1)
        h0.prune_keep_group(1)
        h1.prune_keep_group(2)
        wa0 = h0.get_weighted_average()
        wa1 = h1.get_weighted_average()
        sum_in_period = 0
        # sum part of first bin
        sum_in_period += hist_rand.histogram[self.get_int(wa0)] * (1-self.get_frac(wa0))
        # sum part of last bin
        sum_in_period += hist_rand.histogram[self.get_int(wa1) + 1] * self.get_frac(wa1)
        # sum bins in between
        for i in range(self.get_int(wa0)+1, self.get_int(wa1)):
            sum_in_period += hist_rand.histogram[i]

        dt_per_bin = hist_rand.histogram / sum_in_period * clk_period
        t_per_bin = []
        sums = 0
        for i in range(0, len(dt_per_bin)):
            t_per_bin.append(sums)
            sums += dt_per_bin[i]
        self.dt_per_bin = dt_per_bin
        self.t_per_bin = t_per_bin

    def get_time(self, hist, slot_select):
        wa = hist.get_weighted_average()
        dtime = self.t_per_bin[self.get_int(wa)] + self.get_frac(wa)*self.dt_per_bin[self.get_int(wa)]

        return slot_select*self.clk_period - dtime


    def init(self):
        pass



