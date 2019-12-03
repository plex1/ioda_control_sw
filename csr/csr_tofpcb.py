#  Register definitions

class csr_tofpcb():

    def register(self, addr, name, descr=''):
        reg = []  # create empty list
        reg.append(addr)
        reg.append(name)
        reg.append(descr)
        return reg

    def get_reg_list(self):
        registers = []
        registers.append(self.register(0x0, "id"))
        registers.append(self.register(0x1, "pwm_comp_level1"))
        registers.append(self.register(0x2, "pwm_comp_level2"))
        registers.append(self.register(0x3, "pwm_v_adj_apd"))
        registers.append(self.register(0x4, "v_5v_sense"))
        registers.append(self.register(0x5, "v_apd_sense"))
        registers.append(self.register(0x6, "v_apd_r_sense"))
        registers.append(self.register(0x7, "v_sipm_sense"))
        registers.append(self.register(0x8, "lockin_1_filt"))
        registers.append(self.register(0x9, "lockin_2_filt"))
        registers.append(self.register(0xa, "lockin_1_peak"))
        registers.append(self.register(0xb, "temperature"))
        registers.append(self.register(0xc, "start_pulses"))
        registers.append(self.register(0xd, "stop_pulses"))


        return registers