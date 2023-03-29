import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import mysql.connector as MariaDB
from checkbox import show_checkbox_dropdown

import os


server_connection = None
cursor = None

def print_me(sender):
    print(f"Menu Item: {sender}")

def collect_debug_values(sender, app_data, user_data):
    print(f"""
    Sender: {sender}
    App Data: {app_data}
    User Data: {user_data}
    Sender Values: {dpg.get_value(sender)}
    """)


def use_database(sender, app_data):
    
    def populate_tables(connection: MariaDB.connection_cext.CMySQLConnection):
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        table_names = [table[0] for table in cursor]
    
        dpg.configure_item(sql_tables_listbox, items=table_names)

    global server_connection
    assert type(server_connection) == MariaDB.connection_cext.CMySQLConnection
    try:
        global cursor
        cursor = server_connection.cursor()
        cursor.execute(f"USE {app_data};")
        DATABASE_NAME = f"Column Names for: {app_data}"  # TODO will improve later
        dpg.configure_item(item=sql_db_column_name_portal, default_value=DATABASE_NAME)

        populate_tables(server_connection)


    
    except AssertionError:
        print(AssertionError)




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


def grab_text(sender, app_data, user_data):  # grabs sender tag, app_data

    def execute_query(sql_cursor: MariaDB.connection_cext.CMySQLConnection, user_data):
        
        #assert type(server) == MariaDB.connection_cext.CMySQLConnection
        try:
            prompt = dpg.get_value(user_data)
            sql_cursor.execute(prompt)

            dpg.delete_item('sql-table-view', children_only=True)

            for name in cursor.column_names:
                dpg.add_table_column(label=name, parent='sql-table-view')    

            for item in cursor:  # how many rows down
                with dpg.table_row(parent='sql-table-view'):
                    for data in item:
                        dpg.add_text(data)


        #except AssertionError:
            #print(AssertionError)
        except MariaDB.Error as er:
            print('Error:', er)


    if 'sql' in sender:
        global cursor
        execute_query(cursor, user_data)  # shuttles to execute if appropriate 





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
        db_choices = dpg.add_listbox(parent='db-dropdown', num_items=10, width=200, items=db_choices_str, callback=use_database)
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
dpg.create_viewport(title='Data Explorer', width=900, height=900)




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
    sql_db_column_name_portal = dpg.add_text('Table Names:') 
    with dpg.child_window(height=400, autosize_x=True): 
        with dpg.group(horizontal=True):
            sql_tables_listbox = dpg.add_listbox(width=200, tag='column-listbox', num_items=20)  # 1 item is 17.5 px in height
            dpg.add_input_text(multiline=True, height=350, default_value='SQL Queries go here', tag='sql-box', tab_input=True) # make resizeable?
    
    with dpg.group(horizontal=True):
        with dpg.child_window(height=40, width=200):
            pass
        with dpg.child_window(height=40, autosize_x=True):
            dpg.add_button(label='Run Query', callback=grab_text, tag='sql-button', user_data='sql-box')



    with dpg.child_window():  # TABLE-MAKER
        with dpg.group():
            with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                           resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                           borders_outerV=True, borders_innerH=True, borders_outerH=True, tag='sql-table-view') as query_results_table:
                pass
                

with dpg.window(label='Dashboard'):  
    with dpg.child_window(height=400, width=400, label='Bar Charts'):
        with dpg.plot(label='Transactions By State', height=400, width=-1):
            state_list = [["NY", 11], ["FL", 21], ["CT", 31]]
            dpg.add_plot_legend()

            trans_state_x = dpg.add_plot_axis(dpg.mvXAxis, label='State', no_gridlines=True)  
            # mvXaxis, signifying X axis
            # not plot x, plot y like matplotlib or other

            dpg.set_axis_limits(trans_state_x, 9, 33)

            dpg.set_axis_ticks(trans_state_x, state_list)

            trans_state_y = dpg.add_plot_axis(dpg.mvYAxis, label='Number of Transactions')

            dpg.set_axis_limits_auto(trans_state_y)




cnxpool = MariaDB.pooling.MySQLConnectionPool(pool_name= "mypool", pool_size= 3, database='db_capstone', user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'))
cnx_1 = cnxpool.get_connection()
cnx_cur = cnx_1.cursor()
cnx_cur.execute("""
SELECT DISTINCT(cust_state)
FROM cdw_sapp_customer
ORDER BY 1;
""")
states = [state[0] for state in cnx_cur]

show_checkbox_dropdown(3, states)


# def change_text(sender, app_data):
#     dpg.set_value("text item", f"Mouse Button ID: {app_data}")

# # def visible_call(sender, app_data):
# #     print("I'm visible")

# with dpg.item_handler_registry(tag="widget handler") as handler:
#     dpg.add_item_clicked_handler(callback=change_text)
#     # dpg.add_item_visible_handler(callback=visible_call)
#     dpg.add_item_active_handler

# with dpg.window(width=500, height=300):
#     dpg.add_text("Click me with any mouse button", tag="text item")
#     dpg.add_text("Close window with arrow to change visible state printing to console", tag="text item 2")

# # bind item handler registry to item
# dpg.bind_item_handler_registry("text item", "widget handler")
# dpg.bind_item_handler_registry("text item 2", "widget handler")





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
    