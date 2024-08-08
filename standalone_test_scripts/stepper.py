#! /usr/bin/env python
# title           : stepper.py
# description     :
# author          : Felix Arnold
# python_version  : 3.5.2

#import numpy as np
#from numpy.random import rand, randn
#from scipy.stats import norm
#import matplotlib.pyplot as plt


from serial import Serial
import time

# constants
id = 0xcf
w_byte = 8
w_word = 32
n_bw = int(w_word  / w_byte)
n_header = 3  # in words

def main():


    print("Loopback Test")
    e = encode_frame(command=1, addr=1, len=4, data=[5, 6, 7, 8])
    print(str(e))
    d = decode_frame(e)
    print(str(d))


    ser = Serial('/dev/ttyUSB0')  # open serial port
    print(ser.name)  # check which port was really used
    #ser.write(b'hellosdfdsfasdfsdf')  # write a string
    ser.write(bytearray(e))

    time.sleep(1.0)
    back=ser.read_all()
    print(len(back))
    print("back: ")
    print(back)
    b = decode_frame(list(back))
    print(str(b))

    ser.write(bytearray(encode_frame(command=0, addr=1, len=4, data=[0, 0, 0, 0])))

    time.sleep(1.0)
    back=ser.read_all()
    print(len(back))
    print("back: ")
    print(back)
    b = decode_frame(list(back))
    print(str(b))


    ser.close()  # close port


def intToByteArray(value):
    a=[]
    for n in reversed(range(0, n_bw)):
        a.append((value >> ((4-1-n)*w_byte)) & 0xFF)
    return a


def byteArrayToInt(byteArray):
    value = 0
    for n in range(0, n_bw):
        value += byteArray[n] << ((n)*w_byte)
    return value


def encode_frame(command, addr, len, data, incr=True, request = 1):
    if incr:
        incr_num = 1
    else:
        incr_num = 0
    idcval = (id << (w_word - w_byte)) + (command << w_byte) + (request << 1) + incr_num

    return intToByteArray(idcval) + intToByteArray(addr) + intToByteArray(len) + data


def decode_frame(frame_data):
    idcval = byteArrayToInt(frame_data[0 :4])
    print("idcdval=" + hex(idcval))

    frame = {
        "id": (idcval & (0xFF << (w_word - w_byte))) >> (w_word - w_byte),
        "command":  (idcval & (0xFF << (w_byte))) >> w_byte,
        "request": (idcval & 0x2) >> 1,
        "incr": idcval & 0x1,
        "addr": byteArrayToInt(frame_data[4:8]),
        "len": byteArrayToInt(frame_data[8:12]),
        "data": frame_data[12:]
    }
    return frame









#frame = idcontrol + + CodecFormat.intToByteArray(addr) + + CodecFormat.intToByteArray(len) + + data


if __name__ == "__main__":
    main()
