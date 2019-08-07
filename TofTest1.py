
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
    variable_slot = True

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
    tofp.use_midpoint = True
    tofp.calibrate_bins = True

    # calibrate
    calib_histograms = tofc.get_calibration_histograms(n_taps)
    tofp.calibration_update(calib_histograms[0], calib_histograms[1], clock_period)

    # verify calibration via random bin distribution
    std_norm = tofc.verify_calibration(tofp.dt_per_bin)
    print('cd_norm_std = ' + str(std_norm))

    # verify calibration via period measurement
    period_std=tofc.verify_calibartion_period(tofp, clock_period)
    print('period_std  = ' + str(period_std))


    # settings for time measurements
    registers.reg['trigTestPeriod'].write(20)
    registers.ringOscSetting.write(0)
    slot_select = 6
    registers.histogramFilter.write(2**16+slot_select)

    delay_set = range(10, 141, 1)
    delay_tmeas = []

    for delay in delay_set:
        tofc.set_delay(delay)
        if variable_slot:
            slot_select = registers.reg['averageFilter'].read()
            print('Slot select'+str(slot_select))
            registers.histogramFilter.write(2 ** 16 + slot_select)
        time_meas=tofc.measure_delay_tofp(tofp, n_taps)
        delay_tmeas.append(time_meas)
        print("time: " + str(time_meas))

    # plot results
    plt.figure(0)
    plt.plot(np.array(delay_set)*0.25, delay_tmeas)
    plt.grid(True, which="both")
    plt.xlabel('Delay Setting [ns]')
    plt.ylabel('Delay Measured [ns]')
    plt.show()


if __name__ == "__main__":
    main()
