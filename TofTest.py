
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster
from csr_tofperipheral_manual import csr_tofperipheral
from registers import Registers
from TofControl import TofControl
from TofProcessing import HistogramProcessing
from TofProcessing import TofProcessing

import time
import numpy as np
import matplotlib.pyplot as plt


def main():


    # init interface
    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    n_taps = 100

    # init registers
    test_csri = csr_tofperipheral()
    registers = Registers(gepin)
    registers.offset = 0xF0030000
    registers.populate(test_csri)

    tofc = TofControl(registers)
    tofc.init()

    registers.reg['trigTestPeriod'].write(20)

    #calibrate
    registers.histogramFilter.write(0)  # filter off

    registers.reg['ringOscSetting'].write(4)  # set to internal Oscillator
    values = tofc.get_histogram(n_taps, 1)
    hist_rand = HistogramProcessing(values)

    registers.reg['ringOscSetting'].write(0)  # set to external input
    tofc.set_delay(20)
    values = tofc.get_histogram(n_taps, 1)
    hist_pulse = HistogramProcessing(values)
    dt = 25 #25ns
    tofp = TofProcessing()
    tofp.calibrate(hist_pulse, hist_rand, dt)



    registers.ringOscSetting.write(0)
    slot_select = 6
    registers.histogramFilter.write(2**16+slot_select)



    delay_set = range (0,40,2)
    #delay_set = range(0, 240, 20)
    delay_set = range(10, 31, 10)
    delay_meas = []
    delay_tmeas = []

    hp = HistogramProcessing()
    for delay in delay_set:
        tofc.set_delay(delay)
        values = tofc.get_histogram(n_taps, 1)
        print(str(values))
        hp.set_histogram(values)
        hp.prune_keep_group(0)
        av_meas = hp.get_weighted_average()
        time_meas = tofp.get_time(hp, slot_select)
        print("Average: " + str(av_meas))
        print("time: " + str(time_meas))
        delay_meas.append(av_meas)
        delay_tmeas.append(time_meas)
        print('AverageFiter: ' + str(registers.reg['averageFilter'].read()))

    plt.figure(0)
    plt.plot(delay_set, delay_meas)
    plt.show()
    plt.figure(0)
    plt.plot(delay_set, delay_tmeas)
    plt.show()


    hp.plot_histogram()


if __name__ == "__main__":
    main()
