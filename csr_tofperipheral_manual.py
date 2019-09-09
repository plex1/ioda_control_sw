#  Register definitions for slave core: SVEC carrier control and status registers

class csr_tofperipheral():

    def register(self, addr, name, descr=''):
        reg = []  # create empty list
        reg.append(addr)
        reg.append(name)
        reg.append(descr)
        return reg

    def get_reg_list(self):
        registers = []

        registers.append(self.register(0x0, "led"))
        registers.append(self.register(0x4, "led2"))
        registers.append(self.register(0x8, "id"))
        registers.append(self.register(0xc, "test"))

        registers.append(self.register(0x10, "tofReg"))
        registers.append(self.register(0x18, "delay"))
        registers.append(self.register(0x1c, "trigTestPeriod"))

        registers.append(self.register(0x24, "trigPosition"))
        registers.append(self.register(0x28, "control"))
        registers.append(self.register(0x28, "histMode"))
        registers.append(self.register(0x2c, "histValues"))

        registers.append(self.register(0x30, "ringOscSetting"))
        registers.append(self.register(0x34, "histogramFilter"))
        registers.append(self.register(0x38, "averageFilter"))

        return registers
