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
        self.ser = Serial(port, baudrate=baudrate)  # open serial port
        self.debug = 0
        if self.debug > 0:
            print("GepinSerial created" + self.ser.name)  # check which port was really used


    def write_list(self, wl):
        if self.debug>0:
            print("sent bytes: " + str(wl))
        self.ser.write(bytearray(wl))

    def read_list(self, len):
        rl = list(self.ser.read(len))
        if self.debug > 0:
            print("received bytes: " + str(rl))
        return rl

    def clear_if(self):
        self.ser.read_all()
