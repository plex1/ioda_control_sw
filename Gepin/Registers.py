import json


class Registers:

    class Field:
        def __init__(self, interface, addr, bit_offset, bit_width, name, description="", access_read=True, access_write=True):
            self.interface = interface
            self.addr = addr
            self.bit_offset = bit_offset
            self.bit_width = bit_width
            self.description = description
            self.access_read = access_read
            self.access_write = access_write

        def write(self, data):
            self.interface.write(self.addr, (data & (2**self.bit_width-1)) << self.bit_offset)

        def read(self):
            return (self.interface.read(self.addr)[0] >> self.bit_offset) & (2**self.bit_width-1)

        def set_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val | (1 << index)
            self.interface.write(self.addr, val)

        def clear_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val & ~(1 << index)
            self.interface.write(self.addr, val)

        def set(self):
            self.set_bit(0)

        def clear(self):
            self.clear_bit(0)

    class Register:

        def __init__(self, interface, addr, name="", description=""):
            self.interface = interface
            self.addr = addr
            self.name = name
            self.description = description
            self.field = {}

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
        self.csr_file = None
        self.name = ""
        self.description = ""
        self.offset = 0
        self.reg = {}
        self.use_json_offset = True
        
    def populate(self, csr):
        self.csr_file = csr
        csrlist = self.csr_file.get_reg_list()
        # create dictionary with registers
        self.reg = {}

        for i in range(0, len(csrlist)):
            self.reg[csrlist[i][1]] = self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1])
            setattr(self, csrlist[i][1], self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1]))

    def populate_json(self, csr_json_file):

        self.reg = {}
        with open(csr_json_file, "r") as read_file:
            data = json.load(read_file)
            self.csr_file = csr_json_file
            self.name = data['name']
            self.description = data['description']
            if self.use_json_offset:
                self.offset = data['offset']
            for reg_def in data['registers']:
                self.reg[reg_def['name']] = \
                    self.Register(self.interface, reg_def['address'] + self.offset, reg_def['name'])

                for field_def in reg_def['fields']:
                    fields = self.reg[reg_def['name']].field
                    fields[field_def['name']] = \
                        self.Field(self.interface, reg_def['address'], field_def['bitOffset'], field_def['bitWidth'],
                                   field_def['name'], field_def['description'], field_def['access']['read'],
                                   field_def['access']['write'])
