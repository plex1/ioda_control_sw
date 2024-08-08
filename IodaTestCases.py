from TestEnv.TestEnvStructure import AbstractTestCase
from MotorControl import MotorControl
import numpy as np
import matplotlib.pyplot as plt
import time
from TofProcessing import TofProcessing
import numpy as np
import matplotlib.pyplot as plt
from IodaControl import PointMeasured
from IodaControl import PointCloud
from TestEnv.TestEnvLog import DataLogger

class TestCaseID(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseID'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registersTofFPGA = self.setup.sub_unit['toffpga'].ctrl.registers
        self.checker.check('is_equal', registersTofFPGA.reg['id'].read(), 0x1a, 'Read out ID')

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

class TestCaseADC(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseADC'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers

        n_taps = 100
        clock_period = 25  # 25ns 40MHz clock

        registers_toffpga.reg['control'].field['edge'].clear()
        registers_toffpga.reg['control'].field['trigOn'].set()
        print("control reg: " + hex(registers_toffpga.reg['control'].read()))
        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        registers_tofpcb.reg['pwm_comp_level_1'].write(140)
        registers_tofpcb.reg['pwm_v_adj_apd'].write(100)
        tofc.calibrate()
        print("calibrated")

        #registers_toffpga.reg['control'].field['edge'].clear()
        time.sleep(0.1)

        delay_measured=[]
        threshold_set = range(128, 166)
        for threshold in threshold_set:
            registers_tofpcb.reg['pwm_comp_level_1'].write(threshold)
            time.sleep(0.1)
            slot_select = registers_toffpga.reg['averageFilter'].read() + 0  # todo: tbd +1?
            print('Slot select' + str(slot_select))
            registers_toffpga.reg['histogramFilter'].write(2 ** 16 + slot_select)
            delay_meas1 = tofc.measure_delay()
            print(str(delay_meas1))
            delay_measured.append(delay_meas1)

        registers_toffpga.reg['control'].field['edge'].set()
        delay_measured2 = []
        for threshold in threshold_set:
            registers_tofpcb.reg['pwm_comp_level_1'].write(threshold)
            time.sleep(0.1)
            slot_select = registers_toffpga.reg['averageFilter'].read() + 0  # todo: tbd +1?
            print('Slot select' + str(slot_select))
            registers_toffpga.reg['histogramFilter'].write(2 ** 16 + slot_select)
            delay_meas1 = tofc.measure_delay()
            print(str(delay_meas1))
            delay_measured2.append(delay_meas1)



        self.data_logger.add_data('threshold_set', np.array(threshold_set).tolist())
        self.data_logger.add_data('delay_measured', delay_measured)
        self.data_logger.add_data('delay_measured2', delay_measured2)


    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing
        threshold_set = self.data_logger.get_data("threshold_set")
        delay_measured = self.data_logger.get_data("delay_measured")
        delay_measured2 = self.data_logger.get_data("delay_measured2")

        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(delay_measured), threshold_set, 'x-')
        plt.plot(np.array(delay_measured2), threshold_set, 'x-')
        plt.xlabel('Delay Measured [ns]')
        plt.ylabel('Threshold setting [LSB]')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_th_adc.png')


class TestCaseVapdCalibration(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseVapdCalibration'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers

        registers_toffpga.reg['control'].field['edge'].clear()
        registers_toffpga.reg['control'].field['trigOn'].set()
        registers_toffpga.reg['control'].field['SyncOn'].clear()
        registers_toffpga.reg['lockin_sync1_start'].write(0)
        registers_toffpga.reg['lockin_sync1_end'].write(2)
        registers_toffpga.reg['lockin_sync2_start'].write(2)
        registers_toffpga.reg['lockin_sync2_end'].write(0)

        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        registers_tofpcb.reg['pwm_comp_level_1'].write(140)
        registers_tofpcb.reg['pwm_v_adj_apd'].write(100)
        tofc.calibrate()
        print("calibrated")


        time.sleep(0.1)

        hv_value = list(range(0, 140, 5))
        absorption_index=range(0, len(hv_value))
        absorption_delays = []
        lockin1_filt_measured = []
        lockin_1_peak_measured = []
        lockin_2_filt_measured = []


        for i in absorption_index:

            registers_tofpcb.reg['pwm_v_adj_apd'].write(hv_value[i])
            delay_measured=[]

            threshold_set = range(129, 136, 3)
            for threshold in threshold_set:
                #set delay
                registers_tofpcb.reg['pwm_comp_level_1'].write(threshold)
                time.sleep(0.1)

                # time measurement
                delay_meas1 = tofc.measure_delay()
                print(str(delay_meas1))
                delay_measured.append(delay_meas1)

            # lockin measurement
            registers_toffpga.reg['control'].field['SyncOn'].set()
            time.sleep(0.1)
            sum1=0
            for m in range (0,16):
                sum1+=registers_tofpcb.reg['lockin_1_filt'].read()
            lockin1_filt_measured.append(sum1/16)

            sum1=0
            for m in range (0,16):
                sum1+=registers_tofpcb.reg['lockin_1_peak'].read()
            lockin_1_peak_measured.append(sum1/16)

            sum1=0
            for m in range (0,16):
                sum1+=registers_tofpcb.reg['lockin_2_filt'].read()
            lockin_2_filt_measured.append(sum1/16)


            registers_toffpga.reg['control'].field['SyncOn'].clear()
            time.sleep(0.1)


            absorption_delays.append(delay_measured)


        self.data_logger.add_data('absorption_index', list(absorption_index))
        self.data_logger.add_data('absorption_delays', absorption_delays)
        self.data_logger.add_data('lockin1_filt_measured', lockin1_filt_measured)
        self.data_logger.add_data('lockin_1_peak_measured', lockin_1_peak_measured)


    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing
        absorption_index = self.data_logger.get_data("absorption_index")
        absorption_delays = self.data_logger.get_data("absorption_delays")
        lockin1_filt_measured = self.data_logger.get_data("lockin1_filt_measured")
        lockin_1_peak_measured = self.data_logger.get_data("lockin_1_peak_measured")

        derivations_inv = []
        for i in absorption_index:
            derivations_inv.append(absorption_delays[i][1]-absorption_delays[i][0])

        delays = []
        for i in absorption_index:
            delays.append(absorption_delays[i][1])

        xp = np.flip(np.array(derivations_inv))
        yp = np.flip(np.array(delays))
        correction = np.interp(1.6, xp, yp)

        self.setup.sub_unit['toffpga'].ctrl.load_calibration()
        c2 = self.setup.sub_unit['toffpga'].ctrl.correct_delay(128, 1.6)

        self.controller.write_back_test()


        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(derivations_inv), np.array(delays), 'x-')
        plt.ylabel('Delay Measured [ns]')
        plt.xlabel('time between two thresholds (1/derivation)')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_derivation.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(lockin1_filt_measured), np.array(delays), 'x-')
        plt.ylabel('Delay Measured [ns]')
        plt.xlabel('Lockin filt ADC value')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_lockin_filt.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(lockin_1_peak_measured), np.array(delays), 'x-')
        plt.ylabel('Delay Measured [ns]')
        plt.xlabel('Lockin peak ADC value')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_lockin_peak.png')




class TestCaseLine(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseLine'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers
        registers_motor = self.setup.sub_unit['motorcontroller_unit'].ctrl.registers

        registers_toffpga.reg['control'].field['edge'].clear()
        registers_toffpga.reg['control'].field['trigOn'].set()
        registers_toffpga.reg['control'].field['SyncOn'].clear()
        registers_toffpga.reg['lockin_sync1_start'].write(0)
        registers_toffpga.reg['lockin_sync1_end'].write(2)
        registers_toffpga.reg['lockin_sync2_start'].write(2)
        registers_toffpga.reg['lockin_sync2_end'].write(0)

        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        registers_tofpcb.reg['pwm_comp_level_1'].write(133)
        registers_tofpcb.reg['pwm_v_adj_apd'].write(120)
        tofc.calibrate()
        print("calibrated")
        time.sleep(5)

        # init motor
        # set zero
        motc = self.setup.sub_unit['motorcontroller_unit'].ctrl
        motc.set_zero_pos()
        motc.set_step_resolution_1o16()
        motc.enable_motors()
        time.sleep(0.1)
        registers_motor.reg['target_speed'].write(1024)


        time.sleep(0.1)

        point_list = []
        azimuth=0.0
        for elevation in np.arange(0, -0.32, -0.005): #np.arange(0, 0.9, 0.005):
            motc.goto_pos([azimuth, elevation])
            while motc.is_running():
                pass
            point = self.controller.get_point_measurement()
            point["azimuth"]=azimuth
            point["elevation"]=elevation
            point_list.append(point)

        self.data_logger.add_data('point_list', list(point_list))

        motc.goto_motor_pos([0, 0])
        while motc.is_running():
            pass
        motc.disable_motors()


    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing
        point_list = self.data_logger.get_data("point_list")

        motc = self.setup.sub_unit['motorcontroller_unit'].ctrl
        self.controller.load_calibration2()
        points_measured = []
        for point in point_list:
            az=point["azimuth"]
            el=point["elevation"]
            p1 = PointMeasured(point["delays"], az, el)
            p1.set_correction_function(self.controller.correct_delay2)
            points_measured.append(p1)


        time_vec=[]
        time_vec_calibrated=[]
        dist_vec_calibrated=[]
        derivation_inv_array=[]
        y_vec=[]
        z_vec=[]
        elevation_vec=[]
        point_cloud_cartesian=[]
        for point_measured in points_measured:
            time_vec.append(point_measured.get_time())
            time_vec_calibrated.append(point_measured.get_corrected_time())
            dist_vec_calibrated.append(point_measured.get_corrected_distance())
            derivation_inv_array.append(point_measured.get_derivation_inv())
            xyz = point_measured.get_cartesian()
            y_vec.append(xyz[1])
            z_vec.append(xyz[2])
            point_cloud_cartesian.append(xyz)
            elevation_vec.append(point_measured.elevation)


        plt.figure(0)
        plt.clf()
        plt.plot(np.array(elevation_vec), np.array(time_vec), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('elevation')
        plt.ylabel('Time [ns]')
        plt.savefig('data/' + self.prefix + '_time_vec.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(elevation_vec), np.array(time_vec_calibrated), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('elevation')
        plt.ylabel('Time [ns]')
        plt.savefig('data/' + self.prefix + '_time_vec_cal.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(elevation_vec), np.array(dist_vec_calibrated)*100, 'x-')
        plt.grid(True, which="both")
        plt.xlabel('elevation')
        plt.ylabel('Distance [cm]')
        plt.savefig('data/' + self.prefix + '_dist_vec_cal.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(y_vec)*100, np.array(z_vec)*100, '.')
        max_y = np.max(np.array(y_vec)*100)
        min_y = np.min(np.array(y_vec)*100)
        max_z = np.max(np.array(z_vec) * 100)
        min_z = np.min(np.array(z_vec) * 100)
        max_yz = np.max(np.array([max_y, max_z]))
        min_yz = np.min(np.array([min_y, min_z]))
        plt.xlim(min_yz, max_yz)
        plt.ylim(min_yz, max_yz)
        plt.grid(True, which="both")
        plt.xlabel('x [cm]')
        plt.ylabel('z [cm]')
        plt.savefig('data/' + self.prefix + '_y_z.png')

        plt.figure(0)
        plt.clf()
        plt.plot(np.array(elevation_vec), np.array(derivation_inv_array), 'x-')
        plt.grid(True, which="both")
        plt.xlabel('elevation')
        plt.ylabel('deviation_inv [ns]')
        plt.savefig('data/' + self.prefix + '_deviation_inv.png')


class TestCaseAbsorptionCalibration(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCaseAbsorptionCalibration'

        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers
        registers_motor = self.setup.sub_unit['motorcontroller_unit'].ctrl.registers

        registers_toffpga.reg['control'].field['edge'].clear()
        registers_toffpga.reg['control'].field['trigOn'].set()
        registers_toffpga.reg['control'].field['syncOn'].clear()


        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        registers_tofpcb.reg['pwm_comp_level_1'].write(140)
        vapd=110
        registers_tofpcb.reg['pwm_v_adj_apd'].write(vapd)
        tofc.calibrate()
        print("calibrated")


        time.sleep(0.1)

        # init motor
        # set zero
        motc = self.setup.sub_unit['motorcontroller_unit'].ctrl
        motc.set_zero_pos()
        motc.set_step_resolution_1o16()
        motc.enable_motors()
        time.sleep(0.1)
        registers_motor.reg['target_speed'].write(1024)


        absorption_index=range(0,7)
        point_list=[]

        vapd_list = [110] #range(70,131,10)#[80, 100, 120]
        for vapd in vapd_list:

            registers_tofpcb.reg['pwm_v_adj_apd'].write(vapd)

            elevation = 0
            for i in absorption_index:
                azimuth = 0
                motc.goto_pos([azimuth, elevation])
                elevation -= 0.015
                while motc.is_running():
                    pass

                point = self.controller.get_point_measurement()
                point["azimuth"] = azimuth
                point["elevation"] = elevation
                point["vapd"]=vapd
                point_list.append(point)
                p1 = PointMeasured(point["delays"], azimuth, elevation, point["vapd"], point["snrs"])
                print("delay: " + str(p1.get_time()))
                print("derivation_inv: "+str(p1.get_derivation_inv()))
                print("snr0: " + str(p1.get_snr0()))
                print("count: " + str(p1.get_count()))
                print("-------")



        self.data_logger.add_data('absorption_index', list(absorption_index))
        self.data_logger.add_data('point_list', point_list)

        #motc.goto_pos([0, -0.6])
        #while motc.is_running():
        #    pass

        motc.goto_motor_pos([0, 0])
        while motc.is_running():
            pass
        motc.disable_motors()

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing

        point_list = self.data_logger.get_data("point_list")


        # pack into class
        point_cloud = PointCloud()
        for point in point_list:
            az=point["azimuth"]
            el=point["elevation"]
            p1 = PointMeasured(point["delays"], az, el, point["vapd"], point["snrs"])
            p1.set_correction_function(self.controller.correct_delay2)
            point_cloud.add_point(p1)


        vapd_list = point_cloud.get_vapd_list()
        for vapd in vapd_list:

            point_cloud_vapd = PointCloud(point_cloud.get_points_vapd(vapd))
            derivations_inv = []
            delays = []
            for point in point_cloud_vapd.points:
                if point.is_valid():
                    derivations_inv.append(point.get_derivation_inv())
                    delays.append(point.get_time())

            # plot results
            plt.figure(0)
            plt.clf()
            plt.plot(np.array(derivations_inv), np.array(delays), 'x-')
            plt.ylabel('Delay Measured [ns]')
            plt.xlabel('time between two thresholds (1/derivation)')
            plt.grid(True, which="both")
            plt.savefig('data/' + self.prefix + '_derivation_vapd'+ str(vapd) +'.png')

        snrs = []
        counts = []
        for point in point_cloud.points:
            snrs.append(point.get_snr())
            counts.append(point.get_count())

        # plot results
        plt.figure(0)
        plt.clf()
        plt.plot(np.array(snrs), 'x-')
        plt.ylabel('SNR')
        plt.xlabel('measured point')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_snr.png')

        derivations_inv_fit =[]
        delays_fit=[]
        for point in point_cloud.points:
            if point.is_valid():
                derivations_inv_fit.append(point.get_derivation_inv())
                delays_fit.append(point.get_time())
        z = np.polyfit(derivations_inv_fit,delays_fit, 4)
        p_fit=np.poly1d(z)

        derivations_inv_test=np.arange(np.min(derivations_inv_fit), np.max(derivations_inv_fit), 0.05)

        dl = DataLogger('walking_calibration')
        dl.add_data("derivations_inv", derivations_inv_fit)
        dl.add_data("delays", delays_fit)

        plt.figure(0)
        plt.clf()
        vapd_list = point_cloud.get_vapd_list()
        marker_index=0
        markers = 'xo+*><^vsphd|_'
        for vapd in vapd_list:

            point_cloud_vapd = PointCloud(point_cloud.get_points_vapd(vapd))
            derivations_inv = []
            delays = []
            for point in point_cloud_vapd.points:
                if point.is_valid():
                    derivations_inv.append(point.get_derivation_inv())
                    delays.append(point.get_time())

            # plot results
            marker =  markers[marker_index]
            marker_index += 1
            plt.plot(np.array(derivations_inv), np.array(delays), marker + '')

        #fit
        plt.plot(derivations_inv_test, p_fit(derivations_inv_test), ':')

        vapd_legend=[]
        for vapd in vapd_list:
            vapd_legend.append('V_apd = '+str(vapd))
        vapd_legend.append("polynomal fit")
        plt.legend(vapd_legend)
        plt.ylabel('Delay Measured [ns]')
        plt.xlabel('time between two thresholds (1/derivation)')
        plt.grid(True, which="both")
        plt.savefig('data/' + self.prefix + '_derivation_all_vapd.png')

        self.controller.load_calibration2()

        corrected_distances = []
        for point in point_cloud.points:
            if point.is_valid():
                point.set_correction_function(self.controller.correct_delay2)
                corrected_distances.append(point.get_corrected_distance())

        self.checker.check('is_smaller_all', list(np.abs(corrected_distances-np.mean(corrected_distances))), 1,
                           'Corrected distances as expected')

        print("mean_distance: " + str(np.mean(corrected_distances)))
        print(corrected_distances)

class TestCase3d(AbstractTestCase):

    def __init__(self, id, unit_name='', testif={}, controller=None, setup=None):
        self.testif = testif
        TestCaseName = 'TestCase3d'
        super().__init__(TestCaseName, id, unit_name, controller, setup)

    def execute(self):
        AbstractTestCase.execute(self)
        registers_toffpga = self.setup.sub_unit['toffpga'].ctrl.registers
        registers_tofpcb = self.setup.sub_unit['tofpcb'].ctrl.registers
        registers_motor = self.setup.sub_unit['motorcontroller_unit'].ctrl.registers

        registers_toffpga.reg['control'].field['edge'].clear()
        registers_toffpga.reg['control'].field['trigOn'].set()
        registers_toffpga.reg['control'].field['SyncOn'].clear()


        # init tofcontrol
        tofc = self.setup.sub_unit['toffpga'].ctrl
        tofc.init()
        tofc.cal_time = 1
        tofc.measure_time=0.2
        registers_toffpga.reg['trigTestPeriod'].write(4)
        registers_tofpcb.reg['pwm_comp_level_1'].write(133)
        vapd=120
        registers_tofpcb.reg['pwm_v_adj_apd'].write(vapd)
        tofc.calibrate()
        print("calibrated")
        time.sleep(5)

        # init motor
        # set zero
        motc = self.setup.sub_unit['motorcontroller_unit'].ctrl
        motc.set_zero_pos()
        motc.set_step_resolution_1o16()
        motc.enable_motors()
        time.sleep(0.1)
        registers_motor.reg['target_speed'].write(1024)

        time.sleep(0.1)

        point_list = []

        for azimuth in np.arange(0, 1, 0.005):
            for index, elevation in enumerate(np.arange(0.2, -0.5, -0.005)):  # np.arange(0, 0.9, 0.005):
                print("azimuth: " + str(azimuth))
                if index == 0: # anti backlash
                    motc.goto_pos([azimuth, elevation+0.02])
                    while motc.is_running():
                        pass
                    motc.goto_pos([azimuth, elevation])
                    while motc.is_running():
                        pass

                motc.goto_pos([azimuth, elevation])
                #while motc.is_running():
                #    pass
                point = self.controller.get_point_measurement()
                point["azimuth"] = azimuth
                point["elevation"] = elevation
                point["vapd"] = vapd
                point_list.append(point)

        self.data_logger.add_data('point_list', list(point_list))

        motc.goto_motor_pos([0, 0])
        while motc.is_running():
            pass
        motc.disable_motors()

    def evaluate(self):
        AbstractTestCase.evaluate(self)
        self.checker.write_to_file('data/' + self.prefix + '_logger.dat')

        # post processing
        point_list = self.data_logger.get_data("point_list")

        self.controller.load_calibration2()

        # pack into class
        point_cloud = PointCloud()
        for idx,point in enumerate(point_list):
            if idx<len(point_list):

                az = point["azimuth"]
                el = point["elevation"]
                if el>-1/4 and el <0:
                    backlash = 6 / 360
                    el_corrected = el + 2*backlash
                    #p1 = PointMeasured(point["delays"], az, el, point["vapd"], point["snrs"])
                    p1 = PointMeasured(point["delays"], az, el_corrected, point["vapd"], point["snrs"])
                    p1.set_correction_function(self.controller.correct_delay2)
                    point_cloud.add_point(p1)


        import pptk

        filtered_cloud = PointCloud(point_cloud.get_points_azimuth(0.02))
        v= pptk.viewer(point_cloud.get_cartesian_list())
        v.set(point_size=0.0025, lookat=(0,0,0))





