import dearpygui.dearpygui as dpg
from types import FunctionType
from connection_class import ConnectionHandler
from mysql.connector import cursor

class GenericContainerContext:
    def __init__(self, container_tag: str, *args, **kwargs):
            self.kwargs = kwargs
            self.args = args
            self.list = []
            self.tag = container_tag

    def show(self):
        state = dpg.get_item_state(self.tag)['visible']  # get item state returns bool
        dpg.configure_item(self.tag, show=not state)  # negate bool


class Login(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)

    def grab_credentials(self):
        self.__user_box = dpg.get_value('user_box')
        self.__pw_box = dpg.get_value('pw_box')
        self.__login_address = dpg.get_value('host_box')
        
    
    def display(self, default_login: str, default_pass: str, external_callback: FunctionType):
        with dpg.menu(label='Login Information', tag=self.tag):
            dpg.add_input_text(label='Server Login Name', default_value=default_login, tag='user_box')
            dpg.add_input_text(label='Server Password', password=True, default_value=default_pass, tag='pw_box')
            dpg.add_input_text(label='Host', default_value='localhost', tag='host_box' )
            with dpg.group(horizontal=True):
                dpg.add_button(label='Login', callback=external_callback, user_data='login', tag='login-confirm')
                self.login_response_tag = 'login-confirmation'
                dpg.add_text(tag=self.login_response_tag)

    @property
    def login_user(self):
        return self.__user_box
    
    @property
    def login_password(self):
        return self.__pw_box

    @property
    def login_address(self):
        return self.__login_address

    def show(self):
        return super().show()

    def confirm_login(self, response):
        if response is True:
            response = 'Login Succesful!'
        else:
            response = ''
        dpg.configure_item(self.login_response_tag, default_value=response)



class QueryPortal(GenericContainerContext):
    
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)

    @staticmethod
    def sql_save(sender, app_data, user_data):  # app_data, user_data is data of sql box 
        from time import sleep
        with open(file=app_data['file_path_name'], mode='w') as sql_file:
            sql_file.write(dpg.get_value(user_data))
        with dpg.window():
            dpg.add_text(f"File {app_data['file_name']} Saved")
            dpg.add_button(label='ok', callback=lambda:dpg.configure_item(dpg.last_container(), show=False))
        sleep(2)    
        dpg.configure_item(dpg.last_container(), show=False)

    @staticmethod
    def csv_save(sender, app_data, user_data):
        import csv
        pass




    def get_connection(self, connection: ConnectionHandler):
        self.connection = connection
        self.connection.add_connection(self.tag)
        

    def run_query(self, app_data, user_data):
        self.query = dpg.get_value('sql-box')
        self.connection.cur(self.tag)
        self.connection.cur_execute(self.tag, self.query)
        #print(self.connection[self.tag][self.query])


    def display(self, external_callback: FunctionType):
        with dpg.window(label='SQL Query Portal', show=True, tag=self.tag, height=600, width=800): # SQL PROMPT
            with dpg.child_window(height=400, autosize_x=True):
                with dpg.group(horizontal=True):
                    with dpg.tab_bar():
                        with dpg.tab(label='All Databases'):
                            self.sql_databases_listbox = dpg.add_listbox(width=200, tag='db-listbox', num_items=20, callback=external_callback, user_data='sql-db-listbox')  
                        with dpg.tab(label='Database Tables'):
                            self.sql_tables_listbox = dpg.add_listbox(width=200, tag='column-listbox', num_items=20, callback=external_callback,user_data='sql-table-listbox')  # 1 item is 17.5 px in height

                            
                    with dpg.tab_bar():
                        with dpg.tab(label='SQL Queries'):
                            self.sql_query_box = dpg.add_input_text(multiline=True, height=350, width=-1, default_value='SQL Queries go here', tag='sql-box', tab_input=True) 

            with dpg.file_dialog(label="Save query as .sql", width=300, height=400, show=False, tag='sql-save', user_data=self.sql_query_box,callback=self.sql_save): 
                dpg.add_file_extension(".sql", color=(179, 217, 255))

            with dpg.group(horizontal=True):
                self.db_selected = 'show-db'
                with dpg.child_window(height=45, width=200):
                    dpg.add_text(default_value='', tag=self.db_selected)
                with dpg.child_window(height=45, autosize_x=True):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label='Run Query', callback=external_callback, tag='sql-button', user_data='sql-box')
                        dpg.add_button(label='Export..')
                        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                            with dpg.group(horizontal=True):
                                with dpg.group():
                                    dpg.add_text('Export Query:')
                                    dpg.add_separator()
                                    dpg.add_button(label='Export SQL Query as .sql', callback=lambda: dpg.configure_item('sql-save', show=True))
                                with dpg.group():
                                    dpg.add_text('Export Data:')
                                    dpg.add_separator()                                                                
                                    dpg.add_button(label='Export Data as CSV')
                                    dpg.add_button(label='Write Data to Server as View')
            
            with dpg.child_window():  # TABLE-MAKER
                with dpg.group(tag='query-window'):
                    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                borders_outerV=True, borders_innerH=True, borders_outerH=True, tag='sql-table-view') as self.query_results_table:
                                pass


    def export_data(self):
        with dpg.window(label='Export Options:'):
            with dpg.group():
                dpg.add_text(default_value='SQL Query')
                dpg.add_button(label='Export SQL Query as .SQL')
            with dpg.group():
                dpg.add_text(default_value='Data')
                dpg.add_button(label='Export Data')


    def display_query_results(self, results: list[dict]):
        dpg.delete_item('sql-table-view', children_only=True)

        for key, val in results[0].items(): # initiate headers
            dpg.add_table_column(label=key, parent='sql-table-view', width_stretch=False)
        
        for dictionary in results:  # initiate results
            with dpg.table_row(parent='sql-table-view'):
                for value in dictionary.values():
                        dpg.add_text(value, wrap=300)



    def show(self):
        return super().show()







