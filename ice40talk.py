
from Gepin.GepinPhySerial import GepinPhySerial
from Gepin.Gepin import GepinMaster

import time
import numpy as np
import matplotlib.pyplot as plt


def main():


    gepin_phy = GepinPhySerial('/dev/ttyUSB0', baudrate=115200)
    gepin = GepinMaster(gepin_phy)


    #gepin.write(4, [3,4])
    if False:
        gepin.write(0xF003000c, [2])
        gepin.read(0xF003000c)
        gepin.write(0xF003001c, [10])
        gepin.read(0xF0030010)
    gepin.write(0xF003001c, [60]) #period
    #print(hex(gepin.read(0xF0030020, signed=False)[0]))
    #print(hex(gepin.read(0xF0030020, signed=False)[0]))
    if False:
        interest_list =[]
        n_read = 200
        for i in range(0,n_read):
            value = gepin.read(0xF0030010, signed=False)[0]
            if (value  != 0xaaaaaaaa and  value  != 0x55555555):
                interest_list.append(value)
        print("interest list")
        print(str(len(interest_list)))
        for elem in interest_list:
            print(bin(elem))

        print("average number of ns per tap:")
        sig_mhz=1
        print(float(len(interest_list))/n_read/2*1000/sig_mhz/32) #1 mhz = 1000 ns

    #return

    delay = 100 #220
    gepin.write(0xF0030018, [delay])

    gepin.write(0xF0030028, [0])  # set reset mem mode
    gepin.write(0xF0030028, [1])  # set record mode
    time.sleep(1.0)
    gepin.write(0xF0030028, [3])  # set reset addr
    gepin.write(0xF0030028, [2])  # set read addr
    values = []
    n_taps = 100
    print(str(gepin.read(0xF003002c))) # drop first two values value
    print(str(gepin.read(0xF003002c)))
    for i in range(0, n_taps):
        values.append(gepin.read(0xF003002c)[0])
    print(str(values))
    print("min value / average:")
    print(str(np.min(values[0:31])/np.average(values)))


    taps = np.arange(n_taps)
    print("Average: " + str(np.average(taps, weights = values)))
    plt.bar(taps, values, align='center')
    plt.xticks(taps, taps)
    plt.ylabel('occurrences')
    plt.title('histogram')
    plt.show()







if __name__ == "__main__":
    main()