
from GepinPhySerial import GepinPhySerial
from Gepin import GepinMaster

import time
import numpy

n_pinion = 8  # number of teeth in pinon gear
n_upper = 42  # number of teeth in upper gear
n_lower = 42  # number of teeth in lower gear
n_outer = 64  # number of teeth in outer gear
n_spr = 200  # motor steps per revolution
n_ms = 16 # micro stepping
k1 = n_pinion / n_lower * 1 / n_spr * 1 / n_ms
k2 = n_pinion / n_upper * 1 / n_spr * 1 / n_ms
k12 = k1 * n_outer / n_upper
k12_inv = -(k1*k2)/k12

# ae = azimuth / elevation = theta / inclination
def ae_to_mot(ae_coord):
    s1 =  ae_coord[0]/k1
    s2 =  ae_coord[1]/k2 + ae_coord[0]/k12_inv
    s1 = round(int(s1))
    s2 = round(int(s2))
    mot_coord = [s1, s2]
    return mot_coord

def mot_to_ae(mot_coord):
    s1 =  mot_coord[0]*k1
    s2 =  mot_coord[1]*k2 + mot_coord[0]*k12
    ae_coord = [s1, s2]
    return ae_coord


def main():

    ae_coord = [1,1]
    mot_cord = ae_to_mot(ae_coord)
    print(str(mot_cord))
    print(str(mot_to_ae(mot_cord)))


    gepin_phy = GepinPhySerial('/dev/ttyUSB0')
    gepin = GepinMaster(gepin_phy)

    #gepin.write(0, [-55,31, 22])

    #data = gepin.read(0, 3)
    #print(str(data))



    if False:
        gepin.write(0,[66])

        data=gepin.read(1)
        print(str(data))

        gepin.write(1,[77])

        data=gepin.read(0,4)
        print(str(data))

        gepin.read(100)
        gepin.read(0)

    addr_map = {
        "motor1_target_pos": 0,
        "motor2_target_pos": 1,
        "motor1_pos": 2,
        "motor2_pos": 3,
        "motor1_status": 4,
        "motor2_status": 5
    }

    time.sleep(4)

    for pos in numpy.arange(0.1,1.1, 0.1):
        print("target position=" + str(pos))
        mot_cord = ae_to_mot([pos, 0])
        print(str(mot_cord))
        gepin.write(addr_map['motor1_target_pos'], mot_cord)
        time.sleep(7)



    gepin.write(addr_map['motor1_target_pos'], [0,0])


    time.sleep(26)

    for pos in numpy.arange(0.1,1.1, 0.1):
        print("target position=" + str(pos))
        mot_cord = ae_to_mot([0, pos])
        print(str(mot_cord))
        gepin.write(addr_map['motor1_target_pos'], mot_cord)
        time.sleep(6)

    gepin.write(addr_map['motor1_target_pos'], [0,0])

if __name__ == "__main__":
    main()
