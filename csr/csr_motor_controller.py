#  Register definitions

class csr_motor_controller():

    def register(self, addr, name, descr=''):
        reg = []  # create empty list
        reg.append(addr)
        reg.append(name)
        reg.append(descr)
        return reg

    def get_reg_list(self):
        registers = []
        registers.append(self.register(0x0, "id"))
        registers.append(self.register(0x1, "control"))
        registers.append(self.register(0x2, "motor1_target_pos"))
        registers.append(self.register(0x3, "motor2_target_pos"))
        registers.append(self.register(0x4, "motor1_pos"))
        registers.append(self.register(0x5, "motor2_pos"))

        registers.append(self.register(0x6, "motor1_status"))
        registers.append(self.register(0x7, "motor2_status"))
        registers.append(self.register(0x8, "target_speed"))

        registers.append(self.register(0x9, "var4"))


        return registers