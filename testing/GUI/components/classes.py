import dearpygui.dearpygui as dpg
from types import FunctionType
from typing import Optional
from connection_class import ConnectionHandler
from mysql.connector import cursor



class GenericContainerContext:
    def __init__(self, container_tag: str, *args, **kwargs):
            self.kwargs = kwargs
            self.args = args
            self.list = []
            self.tag = container_tag
            self.contents = 'test'


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
                dpg.add_button(label='Login', callback=external_callback, user_data=self.tag, tag='login-confirm')
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
    def save_file(sender, app_data, user_data, contents):  # app_data, user_data is data of sql box 
        from time import sleep


        if user_data == 'sql-box':
            with open(file=app_data['file_path_name'], mode='w') as sql_file:
                sql_file.write(dpg.get_value(user_data))
            

        elif user_data == 'query-window-csv':
            import csv
            with open(file=app_data['file_path_name'], mode='w', newline='') as query_to_csv:
                csv_file = csv.writer(query_to_csv)
                csv_file.writerows(contents)  # contents is a list of tuples
                # writing row for row in in [contents]


        with dpg.window():
            dpg.add_text(f"File {app_data['file_name']} Saved")
            dpg.add_button(label='ok', callback=lambda:dpg.configure_item(dpg.last_container(), show=False))
        
        sleep(2)    
        dpg.configure_item(dpg.last_container(), show=False)



    def get_connection(self, connection: ConnectionHandler):
        self.connection = connection
        self.connection.add_connection(self.tag)
        

    def run_query(self, app_data, user_data):
        self.query = dpg.get_value('sql-box')
        self.connection.cur(self.tag)
        self.connection.cur_execute(self.tag, self.query)
        #print(self.connection[self.tag][self.query])

    @staticmethod    
    def create_view(name):
        current_query = dpg.get_value('sql-box')
        create_view = f"CREATE VIEW {name} AS\n" + current_query
        return create_view

    def display(self, external_callback: FunctionType):
        # entire window
        with dpg.window(label='SQL Query Portal', show=True, tag=self.tag, height=600, width=800): # SQL PROMPT
            with dpg.menu_bar():
                with dpg.menu(label='Menu'):
                    dpg.add_menu_item(label='Refresh', callback=external_callback, user_data='refresh')
            
            with dpg.child_window(height=400, autosize_x=True):
                 
                # first rectangle, tabs of db and db tables
                with dpg.group(horizontal=True):
                    with dpg.tab_bar():
                        with dpg.tab(label='All Databases'):
                            self.sql_databases_listbox = dpg.add_listbox(width=200, tag='db-listbox', num_items=20, callback=external_callback, user_data='sql-db-listbox')  
                        with dpg.tab(label='Database Tables'):
                            self.sql_tables_listbox = dpg.add_listbox(width=200, tag='column-listbox', num_items=20, callback=external_callback,user_data='sql-table-listbox')  # 1 item is 17.5 px in height

                    # write queries here 
                    with dpg.tab_bar():
                        with dpg.tab(label='SQL Queries'):
                            self.sql_query_box = dpg.add_input_text(multiline=True, height=350, width=-1, default_value='SQL Queries go here', tag='sql-box', tab_input=True) 

            # hidden file browser
            with dpg.file_dialog(label="File Directory", width=300, height=400, show=False, tag='sql-save', user_data=None,callback=lambda a, s, u, contents: self.save_file(a, s, u, self.contents)): # NOTE using lambda as a closure, to get data w.r.t self and then moving to a static function
                dpg.add_file_extension(".sql", color=(179, 217, 255))
                dpg.add_file_extension(".csv", color=(255, 255, 179))

            # SQL View Maker
            with dpg.window(label='Create View from Current Query', width=300, height=100, show=False, tag='sql-push-view'):
                dpg.add_text('SQL View Name:')
                dpg.add_separator()
                dpg.add_input_text(tag='view-name')
                with dpg.group(horizontal=True):
                    dpg.add_button(label='OK', callback=lambda: external_callback(None, self.create_view(dpg.get_value('view-name')), 'create-view')) 
                    dpg.add_button(label='Cancel', callback=lambda: dpg.configure_item('sql-push-view', show=False))


            # options underneath query writer input box
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
                                    dpg.add_button(label='Export SQL Query as .sql', callback=lambda: dpg.configure_item('sql-save', show=True, user_data='sql-box', label='Export SQL Query as .sql'))   # TODO: refactor
                                with dpg.group():
                                    dpg.add_text('Export Data:')
                                    dpg.add_separator()                                                                
                                    dpg.add_button(label='Export Data as CSV', callback=lambda: dpg.configure_item('sql-save', show=True, user_data='query-window-csv', label='Save Data as .csv'))
                                    dpg.add_button(label='Write Data to Server as View', callback=lambda: dpg.configure_item('sql-push-view', show=True))
                                         
            # Table 
            with dpg.child_window():  
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


    def display_query_results(self, results: list):
        self.contents = results
        dpg.delete_item('sql-table-view', children_only=True)

        for column_name in results[0]: # initiate headers
            dpg.add_table_column(label=column_name, parent='sql-table-view', width_stretch=False)
        
        for row in results[1:]:  # initiate results
            with dpg.table_row(parent='sql-table-view'):
                for value in row:
                        dpg.add_text(value, wrap=300)

        
    def show(self):
        return super().show()



class SaapPortal(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)
        self.zipcode_list_selection = None  # TODO refactor 
        self.state_list_selection = None


    def _select_one(self, sender: str | int, app_data, user_data, current_item: None | int):
        if current_item is None:
            pass
        else:
            if sender != current_item:
                dpg.set_value(current_item, False)
        current_item = sender
        return current_item

    

    # callback has to be tied to select one like this for now
    def zip_callback(self, sender, app_data, user_data):
        self.zipcode_list_selection = self._select_one(sender, app_data, user_data, current_item=self.zipcode_list_selection)
        


    # select_transactions_query = f"""SELECT 
	# 	COUNT(DISTINCT(transaction_id)) AS `Number of Transactions`, 
	# 	ROUND(SUM(DISTINCT(transaction_value)), 2) AS `Total Sales`,
	# 	timeid AS `Date`

    #     FROM cdw_sapp_credit_card
    #     LEFT JOIN cdw_sapp_customer ON cust_ssn = ssn
    #     WHERE cust_zip = {}
    #     GROUP BY timeid
    #     ORDER BY 3;
    # """


    def state_callback(self, sender, app_data, user_data):
        self.state_list_selection = self._select_one(sender, app_data, user_data, current_item=self.state_list_selection)
    
    # dropdown filter
    def _create_dropdown_filter(self, collection: list, parent_window: str | int, callback: Optional[FunctionType] = None):
        print(parent_window)
        for item in collection:
            dpg.add_selectable(label=item, callback=callback, parent=parent_window, filter_key=item)

    # external function
    def create_zipcodes(self, collection: list):
        self.zipcode_list = collection
        self._create_dropdown_filter(collection=collection, parent_window=self.zip_filter_set, callback=self.zip_callback)
    
    def create_states(self, collection:list):
        self.state_list = collection
        self._create_dropdown_filter(collection=collection, parent_window=self.state_filter_set, callback=self.state_callback) 





    def display(self):
        # main window
        with dpg.window(label='SaaP Bank Data-Mart Portal', height=600, width=743):
            with dpg.group():
                with dpg.child_window():
                    with dpg.tab_bar():
                        # Transactions 
                        with dpg.tab(label='Transaction Details'):
                            with dpg.group():
                                with dpg.child_window():
                                    with dpg.tab_bar():
                                        # Transactions 1: By Region
                                        with dpg.tab(label='Transactions by Region'):
                                            dpg.add_text('Display the transactions made by customers living in a given zip code for a given month and year.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                dpg.add_plot(width=480, height=450)
                                                with dpg.group():
                                                    dpg.add_text('Zip codes:')
                                                    self.__zip_input = dpg.add_input_text(width=-1, callback=lambda s, a: dpg.set_value(self.zip_filter_set, a))
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    self.__zipcodes_filter_key = None
                                                    
                                                    with dpg.child_window(width=-1, height=160) as self.zipcodes:
                                                        pass
                                                        with dpg.filter_set() as self.zip_filter_set:
                                                            pass
                                                    

                                                    dpg.add_date_picker(level=dpg.mvDatePickerLevel_Month, default_value={'month_day':1, 'year':2018, 'month':1})
                                                    dpg.add_button(label='Search', width=-1)
                                                    
                                        # Transactions 2: By Type
                                        with dpg.tab(label='Transactions by Type'):
                                            dpg.add_text('Display the number and total values of transactions for a given type.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                dpg.add_plot(width=480, height=450)
                                                with dpg.group():
                                                    dpg.add_text('Transaction Types:')
                                                    self.types = dpg.add_listbox(num_items=8, width=-1) #TODO add transaction types
                                                    dpg.add_button(label='Search', width=-1)

                                        # Transactions 3: Transactions for branches by state
                                        with dpg.tab(label='Transactions by State'):
                                            dpg.add_text('Display the number and total values of transactions for branches in a given state.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                dpg.add_plot(width=480, height=450)
                                                with dpg.group():
                                                    dpg.add_text('Transactions by State:')
                                                    dpg.add_input_text(width=-1, callback=lambda s, a:dpg.set_value(self.state_filter_set, a))
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    with dpg.child_window(width=-1, height=160) as self.transaction_types:
                                                        with dpg.filter_set() as self.state_filter_set:
                                                            pass
                                                    dpg.add_button(label='Search', width=-1)


                        # Customer Details
                        with dpg.tab(label='Customer Details'):
                            with dpg.group():
                                with dpg.child_window():
                                    with dpg.tab_bar():

                                        # Customer details 1 & 2, find and select customer 
                                        with dpg.tab(label='Customer Account Search'):
                                            dpg.add_text('Check Customer Account Details')
                                            with dpg.group(horizontal=True):

                                                # right side
                                                with dpg.child_window(width=330, height=450):
                                                    dpg.add_text('Search for customer with first & last name, or jump to customer id.', wrap=286)
                                                    dpg.add_spacer()
                                                    with dpg.group(horizontal=True):
                                                        with dpg.group():
                                                            dpg.add_text('First name')
                                                            dpg.add_input_text(tag='first-name', width=90)
                                                        with dpg.group():
                                                            dpg.add_text('Last name')
                                                            dpg.add_input_text(tag='last-name', width=90)
                                                        with dpg.group():
                                                            dpg.add_text('cust_id')
                                                            dpg.add_input_text(tag='Cust-id', width=90)
                                                    dpg.add_spacer()
                                                    dpg.add_button(label='Search', width=286)
                                                    
                                                # left side                                                    
                                                with dpg.child_window(width=330, height=450):                                                                                                                                                                      
                                                    dpg.add_text('Customer Report:')
                                                    dpg.add_text('Lifetime Value')





                                        with dpg.tab(label='Generate Customer Bill'):

                                            with dpg.child_window(width=-1, height=225):
                                                dpg.add_text('View Transaction History')
                                            with dpg.group(horizontal=True):
                                                with dpg.group(horizontal=True):
                                                    
                                                    dpg.add_text('Between')
                                                    
                                                    self.__start_date = dpg.add_button(label='start', width=100)
                                                    with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                                                        dpg.add_listbox(width=90, num_items=3, items=['test' for _ in range(10)], callback=lambda s, a, u:dpg.configure_item(self.__start_date, label=a))
                                                    
                                                    dpg.add_text('and')
                                                    
                                                    self.__stop_date = dpg.add_button(label='stop', width=100)
                                                    with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                                                        
                                                        dpg.add_listbox(width=90, num_items=3, items=['test' for _ in range(10)], callback=lambda s, a, u: dpg.configure_item(self.__stop_date, label=a))
                                                
                                                def clear_dates():
                                                    for _ in range(2):
                                                        dpg.configure_item(self.__start_date, label='start')
                                                        dpg.configure_item(self.__stop_date, label='end')
                                                
                                                with dpg.group():    
                                                    dpg.add_button(label='Search', width=160)
                                                    dpg.add_button(label='Clear', width=160, callback=clear_dates)
                
                                                pass

                                            with dpg.child_window(width=-1, height=225):
                                                dpg.add_plot(width=-1, height=225)
                                                

            with dpg.group():
                with dpg.child_window():
                    pass





