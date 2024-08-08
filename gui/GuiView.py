import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GuiView(Gtk.Window):

    def __init__(self):

        self.parameter_list = None
        self.field_list = None
        self.read_param_callback = None
        self.read_field_param_callback = None
        self.write_param_callback = None
        self.write_field_param_callback = None
        self.label_module_name = None
        self.module_name = ""

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

        #Creating the ListStore model
        self.parameter_liststore = Gtk.ListStore(str, str, str, str, str, str)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView(self.parameter_liststore)
        for i, column_title in enumerate(["R/W", "Address", "Parameter Name", "Field Name", "Value", "Data Type"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 1, 6, 8)
        self.scrollable_treelist.add(self.treeview)


        hbox = Gtk.Box(spacing=6)
        self.grid.attach(hbox, 0, 11, 6, 1)

        label = Gtk.Label()
        label.set_text("Address:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)

        # name combo
        name_store = Gtk.ListStore('guint', str)
        for reg_name, reg in sorted(self.parameter_list.items(), key=lambda item: item[1].addr):
            name_store.append([self.parameter_list[reg_name].addr, reg_name])

        name_combo = Gtk.ComboBox.new_with_model_and_entry(name_store)
        name_combo.set_entry_text_column(1)
        hbox.pack_start(name_combo, True, True, 0)
        self.name_combo = name_combo

        label = Gtk.Label()
        label.set_text("Field:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)

        # field combo
        field_store = Gtk.ListStore('guint', str)
        field_combo = Gtk.ComboBox.new_with_model_and_entry(field_store)
        field_combo.set_entry_text_column(1)
        hbox.pack_start(field_combo, True, True, 0)
        self.field_combo = field_combo

        name_combo.connect("changed", self.on_update_name_combo)

        # red button
        button = Gtk.Button.new_with_label("Read")
        button.connect("clicked", self.on_click_read_param)
        hbox.pack_start(button, True, True, 0)

        label = Gtk.Label()
        label.set_text("Data:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)

        self.data_entry = Gtk.Entry()
        self.data_entry.set_text("111")
        hbox.pack_start(self.data_entry, True, True, 0)

        # write button
        button = Gtk.Button.new_with_label("Write")
        button.connect("clicked", self.on_click_write_param)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Clear")
        button.connect("clicked", self.on_click_clear_all_param)
        hbox.pack_start(button, True, True, 0)

        self.label_module_name.set_text("Test Env GUI for Module: \n" + self.module_name)

        self.show_all()

    def on_update_name_combo(self, combo):
        field_store = Gtk.ListStore('guint', str)
        reg_name = self.get_selected_param()['name']
        field_store.append([0, ""]) #add field = complete register
        if reg_name is not None:
            if self.field_list is not None:
                if self.field_list[reg_name].field is not None:
                    for field_name, field in sorted(self.field_list[reg_name].field.items(), key=lambda item: item[1].bit_offset):
                        field = self.field_list[reg_name].field[field_name]
                        field_store.append([field.bit_offset, field_name])

            Gtk.ComboBox.set_model(self.field_combo, field_store)

    def get_entered_data(self):
        return int(self.data_entry.get_text())

    def get_selected_param(self):
        # find add in parameter list
        combo = self.name_combo
        tree_iter = combo.get_active_iter()
        param={}
        if tree_iter is not None:
            model = combo.get_model()
            param['addr'] = model[tree_iter][0]
            param['name'] = model[tree_iter][1]
            print("Selected: addr=%s" % param['addr'])
        else:
            param['addr'] = None
            param['name'] = None

        return param

    def get_selected_field(self):
        # find add in parameter list
        combo = self.field_combo
        tree_iter = combo.get_active_iter()
        field={}
        if tree_iter is not None:
            model = combo.get_model()
            field['offset'] = model[tree_iter][0]
            field['name'] = model[tree_iter][1]
        else:
            field['offset'] = None
            field['name'] = None

        return field

    def on_click_read_param(self, button):

        addr = self.get_selected_param()['addr']
        name = self.get_selected_param()['name']
        field = self.get_selected_field()['name']


        # run read_param
        if field is not None and field is not "":
            val = self.read_field_param_callback(name, field)
        else:
            val = self.read_param_callback(name)
        format = "UINT32"
        elem = ("R", hex(addr), name, field, hex(val), format)
        print(elem)
        self.parameter_liststore.insert(0, list(elem))

    def on_click_write_param(self, button):
        addr = self.get_selected_param()['addr']
        name = self.get_selected_param()['name']
        field = self.get_selected_field()['name']

        #run write param
        format = "UINT32"
        val = self.get_entered_data()
        if field is not None and field is not "":
            ret = self.write_field_param_callback(name, field, val)
        else:
            ret = self.write_param_callback(name, val)
        elem = ("W", hex(addr), name, field, hex(val), format)
        print(elem)
        self.parameter_liststore.insert(0, list(elem))


    def on_click_clear_all_param(self, button):
        self.parameter_liststore.clear()

    def register_read_param_callback(self, cb):
        self.read_param_callback = cb

    def register_read_field_param_callback(self, cb):
        self.read_field_param_callback = cb

    def register_write_param_callback(self, cb):
        self.write_param_callback = cb

    def register_write_field_param_callback(self, cb):
        self.write_field_param_callback = cb

    def set_parameter_list(self, parameter_list):
        self.parameter_list = parameter_list

    def set_field_list(self, field_list):
        self.field_list = field_list

    def run_gui(self):
        self.compose_window()
        self.connect("destroy", Gtk.main_quit)
        self.show_all()


    def run_gtk(self):
        Gtk.main()

# example usage
def main():
    class Register:

        def __init__(self, interface, addr, name="", description=""):
            self.interface = interface
            self.addr = addr
            self.name = name
            self.description = description
            self.field = {}


    reg1 = Register(None, 0x1)
    reg2 = Register(None, 0x2)
    parameter_list = {}
    parameter_list["Register 1"] = reg1
    parameter_list["Register 2"] = reg2

    gv = GuiView()
    gv.set_parameter_list(parameter_list)
    gv.set_module_name("gui name")
    gv.run_gui()
    gv.run_gtk()


if __name__ == "__main__":
    main()


