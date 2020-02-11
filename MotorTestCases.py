from TestEnv.TestEnvStructure import AbstractTestCase
from MotorControl import MotorControl
import numpy as np
import matplotlib.pyplot as plt
import time


class MotTestCaseID(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'MotTestCaseID'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)
        registers = self.controller.registers
        self.checker.check('is_equal', registers.reg['id'].read(), 0xfa84, 'Read out ID')

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')


class MotTestCaseDrive(AbstractTestCase):

    def __init__(self,id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'MotTestCaseDrive'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)

        registers = self.controller.registers

        mot_coord=[2000,3000]
        ae_coord=self.controller.mot_to_ae(mot_coord)
        mot_coord_2=self.controller.ae_to_mot(ae_coord)
        self.checker.check('is_equal', mot_coord, mot_coord_2, 'Transformation between coordinate systems')


        # set zero
        self.controller.set_zero_pos()
        self.controller.set_step_resolution_1o16()
        self.controller.enable_motors()
        time.sleep(0.1)
        registers.reg['target_speed'].write(1024)
        pos = 1000
        self.controller.goto_motor_pos([pos, 0])
        self.checker.check('is_equal', registers.reg['motor1_status'].read(), 1, 'Motor 1 status running')
        time.sleep(4)
        self.checker.check('is_equal', registers.reg['motor1_status'].read(), 0, 'Motor 1 status not running')
        self.controller.goto_motor_pos([0, 0])
        time.sleep(4)

        self.controller.goto_motor_pos([pos, pos])
        self.checker.check('is_equal', registers.reg['motor2_status'].read(), 1, 'Motor 2 status running')
        time.sleep(4)
        self.checker.check('is_equal', registers.reg['motor2_status'].read(), 0, 'Motor 2 status not running')
        self.controller.goto_motor_pos([0, 0])

        pos1=10
        pos2=11
        self.controller.goto_motor_pos([pos1, pos2])
        while self.controller.is_running():
            pass

        self.checker.check('is_equal', registers.reg['motor1_pos'].read(), pos1, 'Motor 1 position')
        self.checker.check('is_equal', registers.reg['motor2_pos'].read(), pos2, 'Motor 2 position')

        self.controller.goto_motor_pos([0, 0])
        while self.controller.is_running():
            pass
        setp_mrad= 3
        step=setp_mrad/(1000*2*np.pi)
        for pos in np.arange(0.0, 0.02, step):
            self.controller.goto_pos([pos, 0])
            time.sleep(0.5)
            print(str(pos))

        self.controller.goto_motor_pos([0, 0])
        while self.controller.is_running():
            pass

        for pos in np.arange(0.0, 0.02, step):
            self.controller.goto_pos([0, pos])
            time.sleep(0.5)
            print(str(pos))

        #self.controller.goto_pos([1, 0])
        #while self.controller.is_running():
        #    pass

        self.controller.goto_motor_pos([0, 0])
        while self.controller.is_running():
            pass


        self.controller.disable_motors()

    def evaluate(self):
        AbstractTestCase.evaluate(self)

        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

