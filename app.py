import time
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

import dearpygui.dearpygui as dpg


class Connection:
    def __init__(self, ADDR, listbox_id):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(ADDR)
        self.msgs = []
        self.listbox_id = listbox_id

    def send(self, msg):
        self.client_socket.send(bytes(msg, "utf8"))

    def receive(self):
        while True:
            try:
                print('recv1')
                msg = self.client_socket.recv(1024).decode("utf8")
                print('recv')
                self.msgs.append(msg)
                dpg.configure_item(self.listbox_id, items=self.msgs)
            except OSError as error:
                print(error)
                break
            except IOError as e:
                time.sleep(1)



class App:
    def __init__(self):
        self.cons = {}
        self.msg = {}

        dpg.create_context()
        self.welcome_window()
        dpg.show_font_manager()
        dpg.create_viewport(title='Custom Title', width=600, height=200)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

    def welcome_window(self):
        with dpg.window(tag='Primary Window'):
            dpg.add_tab_bar(label='hello work', tag='tab_bar')
            self.new_tab()
            dpg.add_tab_button(label='+', callback=self.new_tab,
                               parent='tab_bar', trailing=True)

    def new_tab(self):
        with dpg.tab(parent='tab_bar', label='Chat',
                     tag=dpg.generate_uuid()) as tab:
            tag_host_input = dpg.generate_uuid()
            tag_port_input = dpg.generate_uuid()
            dpg.add_text('Input HOST')
            dpg.add_input_text(tag=tag_host_input)
            dpg.add_text("Input PORT")
            dpg.add_input_text(tag=tag_port_input)
            dpg.add_button(label='Connect', callback=self.connection_window)
        pass

    def connection_window(self, sender, app_data):
        with dpg.value_registry():
            value_tag = dpg.generate_uuid()
            dpg.add_string_value(tag=value_tag, default_value='')
        parent = dpg.get_item_parent(sender)
        ids = dpg.get_item_children(parent, 1)
        host = dpg.get_value(ids[1])
        port = int(dpg.get_value(ids[3]))
        dpg.delete_item(children_only=True, item=parent)
        list_box_tag = dpg.generate_uuid()
        con = Connection((host, port), list_box_tag)
        self.cons[parent] = con
        dpg.add_listbox(self.cons[parent].msgs, width=-1, num_items=10, parent=parent, tag=list_box_tag)
        self.get_msg(parent, list_box_tag)
        dpg.add_input_text(width=-1, on_enter=True, callback=self.send_msg, parent=parent, source=value_tag)
        dpg.add_button(width=-1, callback=self.send_msg, parent=parent, label='Send')

    def send_msg(self, sender, app_data):
        tab = dpg.get_item_parent(sender)
        self.cons[tab].send(app_data)
        source = dpg.get_item_source(sender)
        dpg.set_value(source, value='')

    def get_msg(self, parent, tag):
        receive_thread = Thread(target=self.cons[parent].receive)
        receive_thread.start()


if __name__ == '__main__':
    app = App()
