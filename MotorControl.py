import time
import numpy as np

from TestEnv.TestEnvStructure import BaseController
from Gepin.Gepin import BaseGepinRegisters
from csr.csr_motor_controller import csr_motor_controller


class MotorControl(BaseController, BaseGepinRegisters):

    def __init__(self, testif, sub_units = [], parameters={}):

        BaseController.__init__(self, testif, sub_units, parameters)
        csr_def = csr_motor_controller()
        BaseGepinRegisters.__init__(self, csr_def, testif['gepin_motor'], parameters)

        self.debug = 0
        self.n_pinion = 8  # number of teeth in pinon gear
        self.n_upper = 42  # number of teeth in upper gear
        self.n_lower = 42  # number of teeth in lower gear
        self.n_outer = 64  # number of teeth in outer gear
        self.n_spr = 200  # motor steps per revolution
        self.n_ms = 16  # micro stepping
        self.k1 = self.n_pinion / self.n_lower * 1 / self.n_spr * 1 / self.n_ms
        self.k2 = self.n_pinion / self.n_upper * 1 / self.n_spr * 1 / self.n_ms
        self.k12 = self.k1 * self.n_outer / self.n_upper
        self.k12_inv = -(self.k1 * self.k2) / self.k12

    def write_back_test(self):
        txdata = 0x1234
        self.registers.reg['var4'].write(txdata)
        rxdata = self.registers.reg['var4'].read()
        print("back: " + hex(rxdata))
        if txdata == rxdata:
            return True
        else:
            return False

    # ae = azimuth / elevation = theta / inclination
    def ae_to_mot(self, ae_coord):
        s1 =  ae_coord[0]/self.k1
        s2 =  ae_coord[1]/self.k2 + ae_coord[0]/self.k12_inv
        s1 = round(int(s1))
        s2 = round(int(s2))
        mot_coord = [s1, s2]
        return mot_coord

    def mot_to_ae(self, mot_coord):
        s1 =  mot_coord[0]*self.k1
        s2 =  mot_coord[1]*self.k2 + mot_coord[0]*self.k12
        ae_coord = [s1, s2]
        return ae_coord

    def goto_zero(self):
        mot_cord = [0, 0]
        self.registers.reg['motor1_target_pos'].write(mot_cord)

    # azimuth elevation
    def goto_pos(self, ae_cord):
        mot_cord = self.ae_to_mot(ae_cord)
        self.registers.reg['motor1_target_pos'].write(mot_cord)

    # motors
    def goto_motor_pos(self, mot_coord):
        self.registers.reg['motor1_target_pos'].write(mot_coord)

    # motors
    def set_zero_pos(self):
        self.registers.reg['control'].write(4)

    # motors
    def enable_motors(self):
        self.registers.reg['control'].write(2)

    # motors
    def disable_motors(self):
        self.registers.reg['control'].write(1)

    # motors
    def set_step_resolution(self, m0, m1):
        self.registers.reg['control'].write(2**5+m0*2**3+m1*2**4)

    def set_step_resolution_1o8(self):
        m0 = 0
        m1 = 1
        self.set_step_resolution(m0, m1)

    def set_step_resolution_1o16(self):
        m0 = 1
        m1 = 1
        self.set_step_resolution(m0, m1)

    def set_step_resolution_1o2(self):
        m0 = 1
        m1 = 0
        self.set_step_resolution(m0, m1)

    def is_running(self):
        return ((self.registers.reg['motor1_status'].read() & 1) != 0) or \
               ((self.registers.reg['motor2_status'].read() & 1) != 0)
