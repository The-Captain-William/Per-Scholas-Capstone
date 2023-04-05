import dearpygui.dearpygui as dpg
from classes import Login, QueryPortal
from connection_class import ConnectionHandler
from mysql.connector import Error as DBError
from dearpygui import demo


if __name__ == "__main__":
    from os import getenv
    db_user = getenv('DB_USER')
    db_password = getenv('DB_PASSWORD')
else:
    db_user = ''
    db_password = ''

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=200)
dpg.setup_dearpygui()



login = Login(container_tag='db_login')
query_portal = QueryPortal(container_tag='portal')

connection = None

demo.show_demo()
def event_handler(sender, app_data, user_data):
    
    if user_data == 'login':
        login.grab_credentials()

        try:
            global connection
            connection = ConnectionHandler(
                pool_name='DataExplorer',
                host=login.login_address,
                user=login.login_user,
                password=login.login_password,
                )
            

            connection.create_connection('default')
            connection.cur('default')
            login.confirm_login(True)
            show_db = 'SHOW databases;'
            connection.cur_execute('default', show_db, headers=False)
            dpg.configure_item(query_portal.sql_databases_listbox, items=[item[0] for item in connection['default'][show_db]])
            dpg.configure_item('query-button', enabled=True)
            
            
        except DBError as e:
            with dpg.window(label='Error'):
                dpg.add_text(f"Error, {e}")
                dpg.add_button(label='close', callback= lambda: dpg.configure_item(dpg.last_container(), show=False))
                login.confirm_login(False)
                dpg.configure_item(query_portal.tag, show=False)
                dpg.configure_item('query-button', enabled=False)

    if user_data == 'sql-box':
        collect_query = dpg.get_value(query_portal.sql_query_box)
        try:
            connection.cur('default')
            connection.cur_execute('default', collect_query)
            query_portal.display_query_results(connection['default'][collect_query])
            connection.pop('default', collect_query)

        except DBError as e:
            with dpg.window(label='Error', no_title_bar=True):
                dpg.add_text(f"Error, {e}")
                dpg.add_button(label='OK', callback=lambda: dpg.configure_item(dpg.last_container(), show=False))

    if user_data == 'sql-db-listbox':  # all databases
        global selected_database
        selected_database = dpg.get_value(query_portal.sql_databases_listbox)
        connection.set_database(selected_database, 'default')
        dpg.configure_item(query_portal.db_selected, default_value=f"Current Database:\n{selected_database}")

        show_tables = 'SHOW tables;'
        connection.cur('default')
        connection.cur_execute('default', show_tables, database=selected_database, headers=False)
        dpg.configure_item(query_portal.sql_tables_listbox, items=[item[0] for item in connection['default'][show_tables]])


    if user_data == 'sql-table-listbox':  # tables of the database
        global selected_table
        selected_table = dpg.get_value(query_portal.sql_tables_listbox)
        
        show_columns = f'DESCRIBE {selected_table}'
        connection.cur('default')
        connection.cur_execute('default', show_columns, database=selected_database)
        query_portal.display_query_results(connection['default'][show_columns])





dpg.create_viewport(title='Data Explorer', width=2000, height=1200)


with dpg.viewport_menu_bar():
    login.display(default_login=db_user, default_pass=db_password, external_callback=event_handler)
    query_portal.display(external_callback=event_handler)

    dpg.add_button(label='Query Portal', callback=query_portal.show, tag='query-button')





dpg.show_viewport()


dpg.start_dearpygui()

dpg.destroy_context()

try:
    connection.close_connection()
except AttributeError:
    pass
