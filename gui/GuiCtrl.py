from gui.GuiView import GuiView
from TofControl import TofControl


class GuiCtrl:

    def __init__(self, gui_view, controller):
        self.controller = controller
        self.gui_view = gui_view

    def set_param_list(self, parameter_list):
        self.gui_view.set_parameter_list(parameter_list)

    def auto_set_param_list(self):
        self.set_param_list(self.extract_memory_map())

    def read_param(self, param):
        try:
            return self.controller.registers.reg[param].read()
        except:
            print("warning: register read not successful")
            return 0

    def write_param(self, param, value):
        try:
            return self.controller.registers.reg[param].write(value)
        except:
            print("warning: register write not successful")
            return 0

    def write_field_param(self, param, field, value):
        try:
            return self.controller.registers.reg[param].field[field].readModifyWrite(value)
        except:
            print("warning: register field write not successful")
            return 0

    def read_field_param(self, param, field):
        try:
            return self.controller.registers.reg[param].field[field].read()
        except:
            print("warning: register field read not successful")
            return 0

    def run_gui(self):
        self.gui_view.register_read_param_callback(self.read_param)
        self.gui_view.register_write_param_callback(self.write_param)
        self.gui_view.register_read_field_param_callback(self.read_field_param)
        self.gui_view.register_write_field_param_callback(self.write_field_param)
        self.gui_view.set_parameter_list(self.controller.registers.reg)
        self.gui_view.set_field_list(self.controller.registers.reg)
        self.gui_view.set_module_name(self.controller.registers.name)
        self.gui_view.run_gui()


    def extract_memory_map(self):
        parameter_list = [] # list of tuples
        for name, reg in sorted(self.controller.registers.reg.items(), key=lambda item: item[1].addr): # sort by addr
            addr = self.controller.registers.reg[name].addr
            parameter_list.append((addr, name, "UINT32"))
        return parameter_list


def main():

    testif = {}
    testif['gepin'] = None
    controller = TofControl(testif)
    gv = GuiView()
    gc = GuiCtrl(gv, controller)
    #gc.set_param_list(parameter_list)
    gc.run_gui()


if __name__ == "__main__":
    main()