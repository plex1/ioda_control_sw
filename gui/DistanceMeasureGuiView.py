import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class DistanceMeasureGuiView(Gtk.Window):

    def __init__(self):

        self.measure_distance_callback = None
        self.calibrate_callback = None
        self.label_module_name = None
        self.module_name = "-"

    def set_module_name(self, name="-"):
        self.module_name = name

    def compose_window(self):

        Gtk.Window.__init__(self, title="TestEnv GUI - "+self.module_name)
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        label = Gtk.Label()
        self.label_module_name = label
        label.set_justify(Gtk.Justification.LEFT)
        self.grid.attach(label, 0, 0, 1, 1)


        hbox = Gtk.Box(spacing=6)
        self.grid.attach(hbox, 0, 1, 6, 1)

        label = Gtk.Label()
        label.set_text("Function:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)


        button = Gtk.Button.new_with_label("Calibrate")
        button.connect("clicked", self.on_click_calibrate)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Measure Distance")
        button.connect("clicked", self.on_click_measure_distance)
        hbox.pack_start(button, True, True, 0)



        hbox = Gtk.Box(spacing=6)
        self.grid.attach(hbox, 0, 12, 6, 1)

        label = Gtk.Label()
        self.result_label = label
        label.set_text("Results:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)

        self.label_module_name.set_text("Test Env GUI for Module: \n" + self.module_name)

        self.show_all()

    def on_click_measure_distance(self, button):
        [d, der] = self.measure_distance_callback()
        self.result_label.set_text("Result: "+ str(d)+"m ,derivatoin="+str(der))


    def register_measure_distance_callback(self, cb):
        self.measure_distance_callback = cb

    def on_click_calibrate(self, button):
        self.calibrate_callback()

    def register_calibrate_callback(self, cb):
        self.calibrate_callback = cb

    def run_gui(self):

        self.compose_window()
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

        #Gtk.main()

    def run_gtk(self):
        Gtk.main()

def main():


    gv = DistanceMeasureGuiView()
    gv.self.set_module_name("measure")
    gv.run_gui("Measure")
    Gtk.main()


if __name__ == "__main__":
    main()


