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


def select_one(sender, app_data, user_data):  # select one slider
    for item_tag in user_data:  
        if item_tag != sender:  
            dpg.set_value(item_tag, False)
    # user_data is a list of ID's
    # if the sender data (selection we just made) is NOT the same as any value in the list we selected,
    # turn it off. 
    # unfortunately we have to iterate through every db on the list, perhaps I can optimize something in the future.


def get_databases():
    # if using nested funcs, put them up top


    def clean_database_list():
            dpg.delete_item('db-dropdown', children_only=True)


    def append_databases_to_window(cursor):  # nested function, will get name of every server
        db_choices = [
            dpg.add_selectable(label=str(db_choice[0]), parent='db-dropdown') for db_choice in cursor
        ]
        # dpg.add selectable adds selectable straight away, but returns a list of tag ID's
        print(db_choices, 'line 30')
        return db_choices


    global server_connection
    
    try:
        assert type(server_connection) == MariaDB.connection_cext.CMySQLConnection
        cursor = server_connection.cursor()
        show_me_the_money = "SHOW databases"
        cursor.execute(show_me_the_money)
        
        clean_database_list()

        db_choices = append_databases_to_window(cursor)  #  I need this list for selections later

        for item_tag in db_choices:
            dpg.configure_item(item_tag, callback=select_one, user_data=db_choices)  
            # will add a callback to every database name, through its item ID
            # user data sent is the list containing all current tag ID's
 

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



    with dpg.menu(label='Select Database') as db_dropdown:  # TODO replace w/ selection style and print out of db name
        with dpg.tree_node(label='Current Database', tag='db-dropdown'):
            dpg.add_text('None', tag='no-server')


    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)

    dpg.add_menu_item(label="Help", callback=print_me)
    dpg.add_menu_item(label="Refresh", callback=get_databases)

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
    