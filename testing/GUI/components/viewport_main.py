import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import mysql.connector as MariaDB

import os


server_connection = None

def print_me(sender):
    print(f"Menu Item: {sender}")

def connect_to_database(sender, app_data, user_data):
    print(sender)
    print(app_data)
    print(user_data)
    print(dpg.get_value(sender))

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


        get_databases()

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




def get_databases():  # WHEN USER REFRESHES OR LOGS IN
    # if using nested funcs, put them up top


    def clean_database_list():
            dpg.delete_item('db-dropdown', children_only=True)


    def append_databases_to_window(cursor):  # nested function, will get name of every server
        db_choices_str = [str(db_choice[0]) for db_choice in cursor]  # TODO rename this lol
        db_choices = dpg.add_listbox(parent='db-dropdown', num_items=10, width=200, items=db_choices_str, callback=connect_to_database)
        # dpg.add selectable adds selectable straight away, but returns a list of tag ID's
        return db_choices


    global server_connection
    
    try:
        assert type(server_connection) == MariaDB.connection_cext.CMySQLConnection
        cursor = server_connection.cursor()
        show_me_the_money = "SHOW databases"
        cursor.execute(show_me_the_money)
        
        clean_database_list()

        append_databases_to_window(cursor)  #  I need this list for selections later

        #for item_tag in db_choices:
            #dpg.configure_item(item_tag, callback=select_one, user_data=db_choices)  
            # will add a callback to every database name, through its item ID
            # user data sent is the list containing all current tag ID's
 
    except AssertionError:
        print("You need to connect to a database first")
    

        


dpg.create_context()
dpg.create_viewport(title='Data Explorer', width=600, height=200)




with dpg.viewport_menu_bar():  # VIEWPORT
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save", callback=print_me)
        dpg.add_menu_item(label="Save As", callback=print_me)

    with dpg.menu(label='Login Infomation'):
        login_box = dpg.add_input_text(label='Server Login Name', default_value=os.getenv('DB_USER'), tag='login_box')
        pw_box = dpg.add_input_text(label='Server Password', password=True, default_value=os.getenv('DB_PASSWORD'), tag='pw_box')
        host_box = dpg.add_input_text(label='Host', default_value='localhost', tag='host_box' )
        login_button = dpg.add_button(label='Login', callback=login)


    with dpg.menu(label='Select Database') as db_dropdown:  # TODO replace w/ selection style and print out of db name
        with dpg.tree_node(label='Current Database', tag='db-dropdown'):
            dpg.add_text('Connect to a Server', tag='no-server')


    with dpg.menu(label="Widget Items"):
        dpg.add_checkbox(label="Pick Me", callback=print_me)
        dpg.add_button(label="Press Me", callback=print_me)
        dpg.add_color_picker(label="Color Me", callback=print_me)

    dpg.add_menu_item(label="Help", callback=print_me)
    dpg.add_menu_item(label="Refresh", callback=get_databases)



with dpg.window(label='SQL Query Portal'): # SQL PROMPT
    dpg.add_text('Column Names')
    dpg.add_listbox(width=200, tag='column-listbox')


demo.show_demo()


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

print(server_connection)

try:
    server_connection.close()
except Exception as e :
    print(f"{e.__class__, e}")
    