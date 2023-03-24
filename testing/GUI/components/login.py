import dearpygui.dearpygui as dpg
import mysql.connector as MariaDB



dpg.create_context()

server_connection = None
print(server_connection)

def login(sender, app_data, user_data):
    login_value = dpg.get_value(login_box)
    password_value = dpg.get_value(pw_box)
    host_value = dpg.get_value(host_box)
    try:
        global server_connection
        server_connection = MariaDB.connect(
        host=host_value,  
        user=login_value,
        password=password_value
        #database=''  # db optional
    )
    
    except MariaDB.Error as err:
        print(f"{err}")


# login window
with dpg.window(label='Login information: ',width=400, tag='login-window') as login_window:
    login_box = dpg.add_input_text(label='Server Login Name', tag='login_box')
    pw_box = dpg.add_input_text(label='Server Password', tag='pw_box')
    host_box = dpg.add_input_text(label='Host', tag='host_box', default_value='localhost')
    login_button = dpg.add_button(label='Login', callback=login)



server_window = dpg.push_container_stack(dpg.add_window(label="Server"))

dpg.push_container_stack(dpg.add_menu_bar())

dpg.push_container_stack(dpg.add_menu(label="Databases",tag='db-menu'))
dpg.add_menu_item(label="Dark")
dpg.add_menu_item(label="Light")
dpg.pop_container_stack()


#dpg.show_debug().
dpg.show_item_registry()
dpg.show_style_editor()
dpg.create_viewport(title='Server Connector')  
dpg.setup_dearpygui()  
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

print(server_connection)

try:
    server_connection.close()

except Exception as e :
    print(f"{e.__class__, e}")
    

