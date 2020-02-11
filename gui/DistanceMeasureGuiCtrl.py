from gui.DistanceMeasureGuiView import DistanceMeasureGuiView
from IodaControl import IodaControl
from IodaControl import PointMeasured


class DistanceMeasureGuiCtrl:

    def __init__(self, gui_view, controller):
        self.controller = controller
        self.gui_view = gui_view

    def calibrate(self):

        self.controller.sub_units['toffpga'].ctrl.calibrate()  #tdc calibration
        self.controller.load_calibration2()  #signal intensity (steepness) calibration
        print("calibration done")

    def measure_distance(self):

        p1=self.controller.get_point_measurement()
        pm=PointMeasured(p1['delays'])
        pm.set_correction_function(self.controller.correct_delay2)
        der=pm.get_derivation_inv()
        d=pm.get_corrected_distance()
        return [d, der]

    def run_gui(self):
        self.gui_view.register_measure_distance_callback(self.measure_distance)
        self.gui_view.register_calibrate_callback(self.calibrate)
        self.gui_view.set_module_name("Measure")
        self.gui_view.run_gui()

def main():

    testif = {}
    testif['gepin'] = None
    controller = IodaControl(testif)
    gv = DistanceMeasureGuiView()
    gc = DistanceMeasureGuiCtrl(gv, controller)
    gc.run_gui()


if __name__ == "__main__":
    main()