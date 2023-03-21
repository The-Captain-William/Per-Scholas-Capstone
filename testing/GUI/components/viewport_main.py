import dearpygui.dearpygui as dpg
import mysql.connector as MariaDB

server_connection = None

def print_me(sender):
    print(f"Menu Item: {sender}")


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
    
        print(type(server_connection))

    except MariaDB.Error as err:
        print(f"{err}")



def get_databases():
    # if using nested funcs, put them up top

    def append_databases_to_window(cursor):  # nested function, will get name of every server
        db_choices = [
            dpg.add_selectable(label=str(db_choice[0]), parent='db-dropdown') for db_choice in cursor
        ]
        
        print(db_choices, 'line 30')
        return db_choices

    global server_connection
    
    try:
        assert type(server_connection) == MariaDB.connection_cext.CMySQLConnection
        cursor = server_connection.cursor()
        show_me_the_money = "SHOW databases"
        cursor.execute(show_me_the_money)
        
        global db_choices
        db_choices = append_databases_to_window(cursor)






    except AssertionError:
        print("You need to connect to a database first")
    
        



dpg.create_context()
dpg.create_viewport(title='Data Explorer', width=600, height=200)



with dpg.viewport_menu_bar():  # viewport
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback=print_me)
        dpg.add_menu_item(label="Save As", callback=print_me)

    with dpg.menu(label='Login Infomation'):
        login_box = dpg.add_input_text(label='Server Login Name', tag='login_box')
        pw_box = dpg.add_input_text(label='Server Password', tag='pw_box')
        host_box = dpg.add_input_text(label='Host', tag='host_box', default_value='localhost')
        login_button = dpg.add_button(label='Login', callback=login)

    with dpg.menu(label='Select Database'):
        dpg.add_menu_item(label="Refresh", callback=get_databases)
        with dpg.tree_node(label='Current Database', tag='db-dropdown'):
            dpg.add_text('None', tag='no-server')
            
            def select_one(sender, app_data, user_data):  # select one slider
                for dpg_item in user_data:  # user data reports item (, )
                    if dpg_item != sender:  # if item is NOT the sender, set the rest to false
                        dpg.set_value(dpg_item, False)
            




    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)

    dpg.add_menu_item(label="Help", callback=print_me)

dpg.show_imgui_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

print(server_connection)

try:
    server_connection.close()

except Exception as e :
    print(f"{e.__class__, e}")
    