import time

class TofControl(object):

    def __init__(self, regs):
        self.tofregs = regs

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

    def get_histogram(self, n_taps, period = 1.0):
        self.set_mode(self.modes("reset"))
        self.set_mode(self.modes("record"))
        time.sleep(period)  # time to acquire data
        self.set_mode(self.modes("resetaddr"))
        self.set_mode(self.modes("read"))
        self.tofregs.histValues.read()
        self.tofregs.histValues.read()
        values = self.tofregs.histValues.read_fifo(n_taps)
        return values




