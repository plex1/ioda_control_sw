from serial import Serial

# class DataStream:
#
#     ser = 0
#
#     def __iter__(self, serin):
#         self.ser = serin
#         return self
#
#     def __next__(self):
#         return self.ser.read() #return one byte


class GepinPhySerial(object):

    def __init__(self, port, baudrate=9600):
        print("Pepin Created")
        self.ser = Serial(port, baudrate=baudrate)  # open serial port
        self.debug = 1

        print(self.ser.name)  # check which port was really used


    def write_list(self, wl):
        if self.debug>0:
            print("sent bytes: " + str(wl))
        self.ser.write(bytearray(wl))

    def read_list(self, len):
        print("start reading: "+ str(len))
        #for i in range(0,12):
        #    print(str(self.ser.read(1)))
        #print("end reading")
        rl = list(self.ser.read(len))
        if self.debug > 0:
            print("received bytes: " + str(rl))
        return rl

    def clear_if(self):
        self.ser.read_all()
