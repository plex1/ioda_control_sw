import time
import numpy as np

from TestEnv.TestEnvStructure import BaseController
from Gepin.Gepin import BaseGepinRegisters
from TestEnv.TestEnvLog import DataLogger


class IodaControl(BaseController, BaseGepinRegisters):

    def __init__(self, testif, sub_units = [], parameters={}):

        BaseController.__init__(self, testif, sub_units, parameters)
        #csr_def = csr_tofpcb()
        #BaseGepinRegisters.__init__(self, csr_def, testif['gepin_tofpcb'], parameters)

        self.debug = 0

    def write_back_test(self):
        # tofpcb
        # motor
        # toffpga


        txdata = 0x1234
        self.registers.reg['var4'].write(txdata)
        rxdata = self.registers.reg['var4'].read()
        print("back: " + hex(rxdata))
        if txdata == rxdata:
            return True
        else:
            return False

    def get_point_measurement(self):

        registers_toffpga = self.sub_units['toffpga'].ctrl.registers
        registers_tofpcb = self.sub_units['tofpcb'].ctrl.registers

        delays_measured = []
        snrs_measured = []

        threshold_set = range(129, 133, 3)
        for threshold in threshold_set:
            # set delay
            registers_tofpcb.reg['pwm_comp_level1'].write(threshold)
            time.sleep(0.1)

            # time measurement
            [delay_meas1, snr1] = self.sub_units['toffpga'].ctrl.measure_delay_snr()
            print(str(delay_meas1))
            delays_measured.append(delay_meas1)
            snrs_measured.append(snr1)

        point_measured={}
        point_measured['delays'] = delays_measured
        point_measured['snrs'] = snrs_measured
        return point_measured

    def get_time(self, point_measured):
        return point_measured["delays"][0]

    def get_derivation_inv(self, point_measured):
        return point_measured["delays"][1]-point_measured["delays"][0]

    def load_calibration(self):
        id = '20200114-220532'
        unit_name="ioda"
        TestCaseName = "TestCaseAbsorptionCalibration"
        prefix = id + '_' + unit_name + '_' + TestCaseName
        self.data_logger = DataLogger(prefix)

        absorption_index = self.data_logger.get_data("absorption_index")
        absorption_delays = self.data_logger.get_data("absorption_delays")
        lockin1_filt_measured = self.data_logger.get_data("lockin1_filt_measured")
        lockin_1_peak_measured = self.data_logger.get_data("lockin_1_peak_measured")

        derivations_inv = []
        for i in absorption_index:
            derivations_inv.append(absorption_delays[i][1] - absorption_delays[i][0])

        delays = []
        for i in absorption_index:
            delays.append(absorption_delays[i][1])

        self.xp = np.flip(np.array(derivations_inv))
        self.yp = np.flip(np.array(delays))
        self.yp = self.yp - self.yp[0]

    def correct_delay(self, time, derivation_inv):

        correction = np.interp(derivation_inv, self.xp, self.yp)
        return time - correction

    def load_calibration2(self):

        dl = DataLogger('walking_calibration')
        derivations_inv = dl.get_data_latest("derivations_inv")
        delays = dl.get_data_latest("delays")

        z = np.polyfit(derivations_inv, delays, 4)
        f_fit = np.poly1d(z)
        self.f_fit = f_fit

    def correct_delay2(self, time, derivation_inv):
        correction = self.f_fit(derivation_inv)
        return time - correction
        #return time-126



class PointMeasured:

    def __init__(self, delays, azimuth=None, elevation=None, vapd=0, snrs=None):
        self.delays = delays
        self.azimuth = azimuth
        self.elevation = elevation
        self.vapd = vapd
        self.f_correct=None
        self.snrs=snrs

        self.min_distance = 0.3
        self.max_distance = 6

    def set_correction_function(self, f1):
        self.f_correct=f1

    def get_time(self):
        return self.delays[0]

    def get_derivation_inv(self):
        return self.delays[1] - self.delays[0]

    def get_corrected_time(self):
        return self.f_correct(self.get_time(), self.get_derivation_inv())

    def get_corrected_distance(self):
        c=0.149895
        d0=0.099
        d01=0.035
        quarz_offset=1
        return self.get_corrected_time() * c * quarz_offset + d0 + d01

    def get_cartesian(self):
        r = self.get_corrected_distance()
        elevation=self.elevation*2*np.pi
        inclination = np.pi/2-elevation
        azimuth=self.azimuth*2*np.pi
        x = r * np.sin(inclination) * np.cos(azimuth) #- 0.05*np.sin(azimuth)
        y = -r * np.sin(inclination) * np.sin(azimuth) #+ 0.05*np.cos(azimuth)
        z = -r * np.cos(inclination)
        return [x,y,z]

    def get_distance(self):
        xyz = self.get_cartesian()
        return np.sqrt(xyz[0]**2+xyz[1]**2+xyz[2]**2)

    def get_snr(self):
        return self.snrs[1][1]

    def get_snr0(self):
        return self.snrs[0][1]

    def get_count(self):
        return self.snrs[1][0]

    def is_valid(self):
        min_count = 20000
        min_snr = 200

        if self.get_count() > min_count and self.get_snr0() > min_snr and self.get_derivation_inv()<1.1:
            return True
        else:
            return False

    def is_in_ragne(self):

        if self.min_distance < self.get_distance() < self.max_distance:
            return True
        else:
            return False


class PointCloud:

    def __init__(self, points=[]):
        self.points = points
        self.max_distance = 6

    def add_point(self, point):
        self.points.append(point)

    def get_max_distance(self):
        max_dist=0
        for point in self.points:
            d = point.get_distance()
            if d > max_dist:
                max_dist = d

    def get_vapd_list(self):
        vapd_list=[]
        for point in self.points:
            if not (point.vapd in vapd_list):
                vapd_list.append(point.vapd)
        return vapd_list

    def get_points_vapd(self, vapd):
        point_list = []
        for point in self.points:
            if point.vapd==vapd:
                point_list.append(point)
        return point_list

    def get_points_azimuth(self, azimuth):
        point_list = []
        for point in self.points:
            if point.azimuth == azimuth:
                point_list.append(point)
        return point_list

    def get_cartesian_list(self):
        point_cloud_cartesian = []
        for point in self.points:
            if point.is_valid():
                point_cloud_cartesian.append(point.get_cartesian())
        return point_cloud_cartesian

    def get_number_of_points(self):
        return len(self.points)

