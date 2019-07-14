
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster

import time
import numpy as np
import matplotlib.pyplot as plt




def main():


    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)

    print(str(hex(gepin.read(0xF0030008)[0]))) #should be 1a
    #gepin.write(0xF003000c, [2])
    #gepin.read(0xF003000c)
    #gepin.write(0xF003001c, [10])
    #gepin.read(0xF0030010)
    #gepin.write(0xF003001c, [0])


    period = 0
    gepin.write(0xF003001c, [period])

    return

    for delay in range (0,255,20):
        gepin.write(0xF0030018, [delay])
        print(str((gepin.read(0xF0030018)[0])))
        time.sleep(1)







if __name__ == "__main__":
    main()