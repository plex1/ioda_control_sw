
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster

def main():

    gepin_phy = GepinPhySerial('/dev/ttyUSB0')
    gepin = GepinMaster(gepin_phy)

    gepin.write(0,[66])

    data=gepin.read(1)
    print(str(data))

    gepin.write(1,[77])

    data=gepin.read(0,4)
    print(str(data))

    gepin.read(100)
    gepin.read(0)



if __name__ == "__main__":
    main()
