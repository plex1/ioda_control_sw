import json
import yaml
import os


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

        def readModifyWrite(self, data):
            val = self.interface.read(self.addr)[0]
            # clear
            val = val & ~((2 ** self.bit_width - 1) << self.bit_offset)
            # modify
            val = val | ((data & (2 ** self.bit_width - 1)) << self.bit_offset)
            #write
            self.interface.write(self.addr, val)

        def set_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val | (1 << (index+self.bit_offset))
            self.interface.write(self.addr, val)

        def clear_bit(self, index):
            val = self.interface.read(self.addr)[0]
            val = val & ~(1 << (index+self.bit_offset))
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
        self.address_shift = 0
        
    def populate(self, csr):
        self.csr_file = csr
        csrlist = self.csr_file.get_reg_list()
        # create dictionary with registers
        self.reg = {}

        for i in range(0, len(csrlist)):
            self.reg[csrlist[i][1]] = self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1])
            setattr(self, csrlist[i][1], self.Register(self.interface, csrlist[i][0] + self.offset, csrlist[i][1]))

        self.name = self.csr_file.get_name()

    def cheby_to_internal_format(self, cheby_data):

        data1=cheby_data
        data = {}
        data['name'] = data1['memory-map']['name']
        data['offset'] = 0  # tbd
        data['description'] = data1['memory-map']['description']
        data['registers'] = []
        for regitem in data1['memory-map']['children']:
            reg = regitem['reg']
            reg_new = {}
            reg_new['name'] = reg['name']
            reg_new['address'] = reg['address']
            reg_new['fields'] = []
            for fielditem in reg['children']:
                field = fielditem['field']
                field_new = {}
                if '-' in field['range']:
                    rangesplit = field['range'].split('-')
                    bitOffset = int(rangesplit[1])
                    bitWidth = int(rangesplit[0]) - int(rangesplit[1]) + 1
                else:
                    bitOffset = int(field['range'])
                    bitWidth = 1
                field_new['bitOffset'] = bitOffset
                field_new['bitWidth'] = bitWidth
                field_new['name'] = field['name']
                field_new['description'] = field['description']
                field_new['access'] = {}
                if 'r' in reg['access']:
                    field_new['access']['read'] = True
                else:
                    field_new['access']['read'] = False
                if 'w' in reg['access']:
                    field_new['access']['write'] = True
                else:
                    field_new['access']['write'] = False
                reg_new['fields'].append(field_new)
            data['registers'].append(reg_new)
        return data

    def populate_file(self, csr_file):

        self.reg = {}
        with open(csr_file, "r") as read_file:

            filename, file_extension = os.path.splitext(csr_file)
            if file_extension==".json":
                data = json.load(read_file)
            elif file_extension==".yaml" or file_extension==".cheby":
                data1 = yaml.load(read_file, Loader=yaml.FullLoader)
                data = self.cheby_to_internal_format(data1)
            else:
                print("file type not supported")
            self.csr_file = csr_file
            self.name = data['name']
            self.description = data['description']
            if self.use_json_offset:
                self.offset = int(data['offset']* 2**self.address_shift)
            for reg_def in data['registers']:
                self.reg[reg_def['name']] = \
                    self.Register(self.interface, int(reg_def['address']*(2**self.address_shift)) + self.offset, reg_def['name'])

                for field_def in reg_def['fields']:
                    fields = self.reg[reg_def['name']].field
                    fields[field_def['name']] = \
                        self.Field(self.interface, int(reg_def['address']*(2**self.address_shift)) + self.offset,
                                   field_def['bitOffset'], field_def['bitWidth'],
                                   field_def['name'], field_def['description'], field_def['access']['read'],
                                   field_def['access']['write'])