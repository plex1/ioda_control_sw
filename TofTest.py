
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
    clock_period = 25  # 25ns 40MHz clock

    # init registers
    test_csri = csr_tofperipheral()
    registers = Registers(gepin)
    registers.offset = 0xF0030000
    registers.populate(test_csri)

    # init tofcontrol
    tofc = TofControl(registers)
    tofc.init()
    tofc.cal_time = 1

    # init tof processing
    tofp = TofProcessing()
    tofp.use_correlation = False

    # calibrate
    calib_histograms = tofc.get_calibration_histograms(n_taps)
    tofp.calibrate(calib_histograms[0], calib_histograms[1], clock_period)

    # # test
    # # settings for time read
    # registers.reg['trigTestPeriod'].write(20)
    # registers.ringOscSetting.write(0)
    # # no slot select
    # registers.histogramFilter.write(0)
    #
    # hp = HistogramProcessing()
    # tofc.set_delay(40)
    # values = tofc.get_histogram(n_taps, 1)
    # print(str(values))
    # hp.set_histogram(values)
    # hp.prune_keep_group(1)
    # hp.set_histogram(values)
    # tofp.use_correlation=False
    # t1=tofp.get_time(hp, 0)
    # print(str(t1))
    # tofp.use_correlation = True
    # t2 = tofp.get_time(hp, 0)
    # print(str(t2))

    # verify calibration
    std_norm = tofc.verify_calibration(tofp.dt_per_bin)
    print('cd_norm_std =' + str(std_norm))

    # verify calibration via period measurement
    period_std=tofc.verify_calibartion_period(tofp, clock_period)
    print('period_std =' + str(period_std))

    return

    # settings for time read
    registers.reg['trigTestPeriod'].write(20)
    registers.ringOscSetting.write(0)
    slot_select = 5
    registers.histogramFilter.write(2**16+slot_select)

    # no slot select
    registers.histogramFilter.write(0)

    delay_set = range (0,40,2)
    #delay_set = range(0, 240, 20)
    delay_set = range(10, 41, 10)
    delay_meas = []
    delay_tmeas = []

    hp = HistogramProcessing()
    for delay in delay_set:
        tofc.set_delay(delay)
        values = tofc.get_histogram(n_taps, 1)
        valuesc = values.copy()
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
