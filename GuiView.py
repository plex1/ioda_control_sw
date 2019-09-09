import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GuiView(Gtk.Window):

    def __init__(self):

        self.parameter_list = None
        self.read_param_callback = None
        self.write_param_callback = None

    def compose_window(self):

        Gtk.Window.__init__(self, title="TestEnv GUI")
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        label = Gtk.Label()
        label.set_text("Test Env GUI for Module: \n -")
        label.set_justify(Gtk.Justification.LEFT)
        self.grid.attach(label, 0, 0, 1, 1)

        #Creating the ListStore model
        self.parameter_liststore = Gtk.ListStore(str, str, str, str, str)
        #for parameter_ref in parameter_list:
         #   self.parameter_liststore.append(list(parameter_ref))


        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView(self.parameter_liststore) #new_with_model(self.parameter_liststore)
        for i, column_title in enumerate(["R/W", "Address", "Parameter Name", "Value", "Data Type"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        # #creating buttons to filter by programming language, and setting up their events
        # self.buttons = list()
        # for prog_language in ["Java", "C", "C++", "Python", "None"]:
        #     button = Gtk.Button(prog_language)
        #     self.buttons.append(button)
        #     button.connect("clicked", self.on_selection_button_clicked)


        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 1, 6, 8)
            # self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
            # for i, button in enumerate(self.buttons[1:]):
            #     self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)


        hbox = Gtk.Box(spacing=6)
        self.grid.attach(hbox, 0, 11, 6, 1)

        label = Gtk.Label()
        label.set_text("Address:")
        label.set_justify(Gtk.Justification.RIGHT)
        hbox.pack_start(label, True, True, 0)

        name_store = Gtk.ListStore('guint', str)
        for parameter_ref in self.parameter_list:
            name_store.append([parameter_ref[0], parameter_ref[1]])

        name_combo = Gtk.ComboBox.new_with_model_and_entry(name_store)
        #name_combo.connect("changed", self.on_name_combo_changed)
        name_combo.set_entry_text_column(1)
        hbox.pack_start(name_combo, True, True, 0)
        self.name_combo = name_combo

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

        button = Gtk.Button.new_with_label("Write")
        button.connect("clicked", self.on_click_write_param)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_label("Read All")
        button.connect("clicked", self.on_click_read_all_param)
        hbox.pack_start(button, True, True, 0)

        self.show_all()

    def get_entered_data(self):
        return int(self.data_entry.get_text())

    def get_sel_addr(self):
        # find add in parameter list
        combo = self.name_combo
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            addr = model[tree_iter][0]
            print("Selected: addr=%s" % addr)
        else:
            addr = None

        return addr

    def on_click_read_param(self, button):

        addr = self.get_sel_addr()
        # search addr in parameter list
        entry = next((item for item in self.parameter_list if item[0] == addr), None)

        if entry is not None:
            # run read_param
            name = entry[1]
            format = entry[2]
            val = self.read_param_callback(name)
            elem = ("R", hex(addr), name, hex(val), format)
            print(elem)
            self.parameter_liststore.insert(0, list(elem))

    def on_click_write_param(self, button):
        addr = self.get_sel_addr()
        # search addr in parameter list
        entry = next((item for item in self.parameter_list if item[0] == addr), None)

        if entry is not None:
            #run write param
            name = entry[1]
            format = entry[2]
            val = self.get_entered_data()
            ret = self.write_param_callback(name, val)
            elem = ("W", hex(addr), name, hex(val), format)
            print(elem)
            self.parameter_liststore.insert(0, list(elem))


    def on_click_read_all_param(self, button):
        self.parameter_liststore.clear()

    def register_read_param_callback(self, cb):
        self.read_param_callback = cb

    def register_write_param_callback(self, cb):
        self.write_param_callback = cb

    def set_parameter_list(self, parameter_list):
        self.parameter_list = parameter_list


    def run_gui(self):

        self.compose_window()


        #win = TreeViewFilterWindow(parameter_list)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()






def main():

    # list of test cases
    # list of tuples
    parameter_list = [(0x0, "Parameter 1", "BOOLEAN"),
                      (0x1, "Parameter 2", "UNIT16"),
                      (0x2, "Parameter 3", "UNIT16"),
                      (0x3, "Parameter 4", "UNIT16")]

    gv = GuiView(parameter_list)
    gv.run_gui()


if __name__ == "__main__":
    main()


# import gi
#
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk
#
#
# class Handler:
#     def onDestroy(self, *args):
#         Gtk.main_quit()
#
#     def onButtonPressed(self, button):
#         print("Hello World!")
#
#
# builder = Gtk.Builder()
# builder.add_from_file("./gui/testerGui.glade")
# builder.connect_signals(Handler())
#
# window = builder.get_object("window1")
# window.show_all()
#
# Gtk.main()
