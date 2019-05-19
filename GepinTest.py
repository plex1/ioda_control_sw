
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster

def main():

    gepin_phy = GepinPhySerial('/dev/ttyUSB0')
    gepin = GepinMaster(gepin_phy)

    gepin.write(1,[66])

    data=gepin.read(1)
    print(str(data))

    gepin.write(2,[77])

    data=gepin.read(1,3)
    print(str(data))



if __name__ == "__main__":
    main()
