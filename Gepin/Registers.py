
class Registers:

    class Register:

        def __init__(self, interface, addr, Info="", Details=""):           
            self.interface = interface
            self.addr = addr
            self.Info = Info
            self.Details = Details

        def write(self, data):
            self.interface.write(self.addr, data)

        def read(self):
            return self.interface.read(self.addr)[0]

        def read_fifo(self, len):
            return self.interface.read(self.addr, len, incr=False)

        def set_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val | (1 << index)
            self.interface.write(self.addr, val)

        def clear_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val & ~(1 << index)
            self.interface.write(self.addr, val)


        def get_abs_addr(self):
            return self.interface.offset + self.addr

    def __init__(self, interface='none'):
        self.interface = interface
        self.csr = None
        self.registers = None
        self.offset = 0
        
    def populate(self, csr):
        self.csr = csr
        csrlist = self.csr.get_reg_list()
        # create dictionary with registers
        self.reg = {}

        for i in range(0, len(csrlist)):
            self.reg[csrlist[i][1]] = self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1])
            setattr(self, csrlist[i][1], self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1]))

    def reg(self, name):
        return self.registers[name]
  
   

   
