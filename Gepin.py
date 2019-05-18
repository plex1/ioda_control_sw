
#gepin general purpose interconnect

import GepinPhySerial


class Gepin(object):

    phy = ...  # type: GepinPhySerial

    def __init__(self, phy):
        self.phy = phy
        # constants
        self.id = 0xcf
        self.w_byte = 8
        self.w_word = 32
        self.n_bw = int(self.w_word / self.w_byte)
        self.n_header = 3  # in words
        # addrshift
        print("Pepin Created")

# ----------------------- point-to-point

    def intToByteArray(self, value):
        a=[]
        for n in reversed(range(0, self.n_bw)):
            a.append((value >> ((4-1-n)*self.w_byte)) & 0xFF)
        return a


    def byteArrayToInt(self, byteArray):
        value = 0
        for n in range(0, self.n_bw):
            value += byteArray[n] << ((n)*self.w_byte)
        return value

    def wordsToBytes(self, wa):
        ba=[]
        for n in range(0, len(wa)):
            ba+=self.intToByteArray(wa[n])
        return ba

    def bytesToWords(self, ba):
        wa = []
        while len(ba) > 0:
            wa.append(self.byteArrayToInt(ba[0:4]))
            ba = ba[4::]
        return wa


    def encode_frame(self, command, addr, length, data, incr=True, request = 1):
        if incr:
            incr_num = 1
        else:
            incr_num = 0
        idcval = (self.id << (self.w_word - self.w_byte)) + (command << self.w_byte) + (request << 1) + incr_num

        return self.intToByteArray(idcval) + self.intToByteArray(addr) + self.intToByteArray(length)\
               + self.wordsToBytes(data)

    def decode_frame(self, frame_data):
        idcval = self.byteArrayToInt(frame_data[0 :4])

        frame = {
            "id": (idcval & (0xFF << (self.w_word - self.w_byte))) >> (self.w_word - self.w_byte),
            "command":  (idcval & (0xFF << (self.w_byte))) >> self.w_byte,
            "request": (idcval & 0x2) >> 1,
            "incr": idcval & 0x1,
            "addr": self.byteArrayToInt(frame_data[4:8]),
            "length": self.byteArrayToInt(frame_data[8:12]),
            "data": self.bytesToWords(frame_data[12:])
        }
        return frame

# ---------------------------- master-slave

    def read(self, addr, length=1, incr=False):

        self.bytesToWords([0,1,2,3])
        e = self.encode_frame(command=0, addr=addr, length=length, data=[])
        self.phy.write_list(e)

        h = self.phy.read_list(self.n_header*self.n_bw)
        dh = self.decode_frame(h)
        d = self.phy.read_list(self.n_bw*dh.get('length'))
        df = self.decode_frame(h+d)
        return df.get('data')

    def write(self, addr, data, length=1, incr=False):

        e = self.encode_frame(command=1, addr=addr, length=length, data=list(data))
        self.phy.write_list(e)

        h = self.phy.read_list(self.n_header*self.n_bw)
        dh = self.decode_frame(h)




