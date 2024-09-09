from TestEnv.TestEnvStructure import AbstractTestCase
import numpy as np
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


class MotTestCaseDriveShowCase(AbstractTestCase):

    def __init__(self,id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'MotTestCaseDriveShowCase'
        super().__init__(TestCaseName, id, unit_name, controller)

    def execute(self):
        AbstractTestCase.execute(self)

        registers = self.controller.registers

        # set zero
        self.controller.set_zero_pos()

        self.controller.set_step_resolution_1o2()
        self.controller.enable_motors()
        time.sleep(0.1)
        #registers.reg['target_speed'].write(1200)
        self.controller.set_speed(42*20)

        def ae_deg(ae):
            return [np.rad2deg(ae[0]*2*np.pi), np.rad2deg(ae[1]*2*np.pi)]


        def run_mot_test(step_size, axis=0):
            target_pos = [step_size*(1-axis), step_size*axis]
            self.controller.goto_pos(target_pos)
            print("going to position, ", ae_deg(target_pos), " deg (azimut-elevation )")
            while self.controller.is_running():
                pass
            target_pos = [0.0, 0.0]
            self.controller.goto_pos(target_pos)
            print("going to position, ", ae_deg(target_pos), " deg (azimut-elevation )")
            while self.controller.is_running():
                pass

        def run_mot_test_microsteps(step_size, axis):
            target_pos = [step_size*(1-axis), step_size*axis]
            self.controller.goto_motor_pos(target_pos)
            print("going to position, ", target_pos, " microsteps")
            while self.controller.is_running():
                pass
            target_pos = [0.0, 0.0]
            self.controller.goto_pos(target_pos)
            print("going to position, ", ae_deg(target_pos), " microsteps")
            while self.controller.is_running():
                pass

        def run_step_test(step_size, number_of_steps, axis):
            for i, pos in enumerate(list(np.linspace(0, number_of_steps * step_size, number_of_steps, endpoint=True))):
                target_pos = [pos*(1-axis), pos*axis]
                self.controller.goto_pos(target_pos)
                print("going to position, ", ae_deg(target_pos), " deg (azimut-elevation)")
                while self.controller.is_running():
                    pass

            target_pos = [0.0, 0.0]
            self.controller.goto_pos(target_pos)
            print("going to position, ", ae_deg(target_pos), " deg (azimut-elevation )")
            while self.controller.is_running():
                pass

        print("Micro Step Tests, half step resolution----")
        run_mot_test_microsteps(200, axis=0)
        run_mot_test_microsteps(200, axis=1)

        print("Run Coordinate Tests, half step resolution---- ----")
        run_mot_test(np.deg2rad(180) / (np.pi * 2), axis=1)
        run_mot_test(np.deg2rad(180) / (np.pi*2), axis=0)

        print("Run Coordinate Stepping Tests, half step resolution---- ----")
        # stepping
        step_size = np.deg2rad(30)/(2*np.pi)
        number_of_steps = 3

        run_step_test(step_size, number_of_steps, axis=1)
        run_step_test(step_size, number_of_steps, axis=0)

        print("Run Coordinate Stepping Tests, 1/16 microstep resolution ----")
        self.controller.set_step_resolution_1o16()
        step_size = np.deg2rad(30) / (2 * np.pi)
        run_step_test(step_size, number_of_steps, axis=1)
        run_step_test(step_size, number_of_steps, axis=0)

        self.controller.disable_motors()


    def evaluate(self):
        AbstractTestCase.evaluate(self)

        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')
