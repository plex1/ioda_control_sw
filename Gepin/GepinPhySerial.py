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
        try:
            self.ser = Serial(port, baudrate=baudrate, timeout=5.0)  # open serial port
            self.clear_if()
        except:
            self.ser = None
            print("Error: Could not connect to interface")
        self.debug = 0
        if self.debug > 0:
            print("GepinSerial created" + self.ser.name)  # check which port was really used


    def write_list(self, wl):
        try:
            if self.debug>0:
                print("sent bytes: " + str(wl))
            self.ser.write(bytearray(wl))
        except:
            print("Physerial, Write error")

    def read_list(self, len):
        try:
            rl = list(self.ser.read(len))
            if self.debug > 0:
                print("received bytes: " + str(rl))
            return rl
        except:
            print("Physerial, read error")

    def clear_if(self):
        self.ser.read_all()

    def close_if(self):
        pass
