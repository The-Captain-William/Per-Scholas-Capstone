import dearpygui.dearpygui as dpg
import mysql.connector as MariaDB



dpg.create_context()

server_connection = None
print(server_connection)

def login(sender, app_data, user_data):
    login_value = dpg.get_value(login_box)
    password_value = dpg.get_value(pw_box)
    try:
        global server_connection
        server_connection = MariaDB.connect(
        host='localhost',
        user=login_value,
        password=password_value
        #database=''  # db optional
    )
    
    except MariaDB.Error as err:
        print(f"{err}")



with dpg.window(label='Login information: ',width=400, tag='login-window'):
    login_box = dpg.add_input_text(label='Server Login Name', tag='login_box')
    pw_box = dpg.add_input_text(label='Server Password', tag='pw_box')
    login_button = dpg.add_button(label='Login', callback=login)



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
except Exception as e:
    print(f"{e}")
    

