import dearpygui.dearpygui as dpg
from Components import *
from dearpygui.demo import show_demo
#from ConnectionHandler.connection_class import ConnectionHandler


# TODO:
# create date and buttons dropdown or find a way to fix date module
# more filtering based off of dates
# graphs


if __name__ == "__main__":
    try:
        from os import getenv
        db_user = getenv('DB_USER')
        db_password = getenv('DB_PASSWORD')
    except Exception:
        db_user = ''
        db_password = ''


connection = None

login_window = Login('login window')
query_window = QueryPortal('query window')
saap_window = SaapPortal('Saap Portal')
customer_window = CustomerPortal('Customer Portal')

def viewport_buttons(enabled: bool):
    pass


def event_handler():
    try:
        login_window.grab_credentials()
        
        global connection
        connection = ConnectionHandler(
                pool_name='DataExplorer',
                host=login_window.login_address,
                user=login_window.login_user,
                password=login_window.login_password,
                )
        login_window.confirm_login(True)

        query_window.setup(connection)
        saap_window.setup(connection)
        customer_window.setup(connection)
        

        dpg.configure_item(viewport_query_button, enabled=True)

    except DBError as e:
        with dpg.window(label='Error'):
            dpg.add_text(f"Error, {e}")
            dpg.add_button(label='close', callback= lambda: dpg.configure_item(dpg.last_container(), show=False))
            login_window.confirm_login(False)
            dpg.configure_item(viewport_query_button, enabled=False)






dpg.create_context()
dpg.setup_dearpygui()

dpg.create_viewport(title='Data Explorer', width=2000, height=1200)

show_demo()

with dpg.viewport_menu_bar():
    login_window.window(default_login=db_user, default_pass=db_password, external_callback=event_handler)
    
    # package this
    viewport_query_button = dpg.add_button(label='Query Portal', callback=query_window.toggle)
    vieport_saap_button = dpg.add_button(label='Business Analytics Dashboard', callback=saap_window.toggle)
    viewport_customer_button = dpg.add_button(label='Customers Database', callback=customer_window.toggle)
    query_window.window()
    saap_window.window()
    customer_window.window()


dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()



def close(connection: ConnectionHandler):
    try:
        connection.close_connection()
    except AttributeError:
        pass

close(connection)
