import dearpygui.dearpygui as dpg
from types import FunctionType
from typing import Optional, Union
from connection_class import ConnectionHandler
from mysql.connector import Error as DBError
from contextlib import contextmanager


class GenericContainerContext:
    def __init__(self, container_tag: str, *args, **kwargs):
            self.kwargs = kwargs
            self.args = args
            self.list = []
            self.tag = container_tag

    def setup(self, connection: ConnectionHandler):
        """
        Set up the window with a connection and display databases available.
        """
        self.connection = connection
        self.connection.create_connection(self.tag)
        self.connection.cur(self.tag)

    @staticmethod
    def _collect_items(list: list):
        """
        queries return as a list of tuples (x, y);
        this will parse tuples and grab the first item.
        Works well if you know your query returns a single column
        """
        return [item[0] for item in list]


    # dropdown filter
    def _create_dropdown_filter(self, collection: list, parent_window: str | int, callback: Optional[FunctionType] = None):
        """
        Will create a dropdown filter given a parent window, the parent window being the filter set.
        """
        for item in collection:
            dpg.add_selectable(label=item, callback=callback, parent=parent_window, filter_key=item, user_data=item)

    def toggle(self):
        """
        Displays the window on or off
        """
        state = dpg.get_item_state(self.tag)['visible']  # get item state returns dict, dict ['visible'] returns bool
        dpg.configure_item(self.tag, show=not state)  # negate bool

    def _window_query_results(self, results: list, parent: str | int):
        """
        Displays query results for a window
        """
        self.contents = results
        dpg.delete_item(parent, children_only=True)

        for column_name in results[0]: # initiate headers
            dpg.add_table_column(label=column_name, parent=parent, width_stretch=False)
        
        for row in results[1:]:  # initiate results
            with dpg.table_row(parent=parent):
                for value in row:
                        dpg.add_text(value, wrap=300)


class Login(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)

    def grab_credentials(self):
        self.__user_box = dpg.get_value('user_box')
        self.__pw_box = dpg.get_value('pw_box')
        self.__login_address = dpg.get_value('host_box')
        
    
    def window(self, default_login: str, default_pass: str, external_callback: FunctionType):
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

    def toggle(self):
        return super().toggle()

    def confirm_login(self, response):
        if response is True:
            response = 'Login Succesful!'
        else:
            response = ''
        dpg.configure_item(self.login_response_tag, default_value=response)



class QueryPortal(GenericContainerContext):
    
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)


    def __save_file(self, sender, app_data, user_data, contents):  # app_data, user_data is data of sql box 
        from time import sleep


        if user_data == self.__export_sql_file_button:
            with open(file=app_data['file_path_name'], mode='w') as sql_file:
                sql_file.write(dpg.get_value(user_data))
            

        elif user_data == self.__export_csv_file_button:
            import csv
            with open(file=app_data['file_path_name'], mode='w', newline='') as query_to_csv:
                #print(app_data, app_data['file_path_name'])
                csv_file = csv.writer(query_to_csv)
                csv_file.writerows(contents)  # contents is a list of tuples
                # writing row for row in in [contents]


        with dpg.window():
            dpg.add_text(f"File {app_data['file_name']} Saved")
            dpg.add_button(label='ok', callback=lambda:dpg.configure_item(dpg.last_container(), show=False))
        
        sleep(2)    
        dpg.configure_item(dpg.last_container(), show=False)
        

    def __run_query(self, app_data, user_data): 
        self.query = dpg.get_value('sql-box')
        self.connection.cur(self.tag)
        self.connection.cur_execute(self.tag, self.query)
        #print(self.connection[self.tag][self.query])

    def __create_view(self):
        current_query = dpg.get_value(self.sql_query_box)
        name = dpg.get_value(self.__sql_view_name)
        if any(name):
            create_view = f"CREATE VIEW {name} AS\n" + current_query
            try:
                self.connection.cur_execute(self.tag, create_view, save=False)
            except DBError as e:
                self.__connection_error(e)
        else:
            e = "You need to write a name first"
            self.__connection_error(e)


    def setup(self, connection: ConnectionHandler):
        """
        Set up the window with a connection and display databases available.
        """
        self.connection = connection
        self.connection.create_connection(self.tag)
        self.connection.cur(self.tag)
        self.connection.cur_execute(self.tag, 'SHOW DATABASES;', headers=False)
        # set up list box
        dpg.configure_item(self.sql_databases_listbox, items=[item[0] for item in connection[self.tag]['SHOW DATABASES;']])

    def refresh(self):
        dpg.configure_item(self.sql_databases_listbox, items=[])
        self.setup(self.connection)
        dpg.configure_item(self.sql_tables_listbox, items=[])
        if self.current_database is not None:
            try:
                self.__get_db_tables(sender=None, app_data=self.current_database)
            except:
                pass


    def __connection_error(self, e):
        with dpg.window(label='Error'):
            dpg.add_text(f"Error, {e}")
            dpg.add_button(label='close', callback= lambda: dpg.configure_item(dpg.last_container(), show=False))



    def __get_db_tables(self, sender, app_data):
        """
        Clicking the database name will select that database and show the tables in that database.
        """
        try:
            self.current_database = app_data
            self.connection.cur_execute(self.tag, 'SHOW TABLES;', database=app_data, headers=False)
            dpg.configure_item(self.__db_selected, default_value=f'Current Database:\n{app_data}')
            collection = self._collect_items(self.connection[self.tag]['SHOW TABLES;'])
            dpg.configure_item(self.sql_tables_listbox, items=collection)
        except DBError as e:
            self.__connection_error(e)

    def __get_table_columns(self, sender, app_data):
        """
        Will describe a given tables column names and datatypes, sends to the query window. 
        """

        query = F"DESCRIBE {app_data}"
        self.connection.cur_execute(self.tag, query)
        self._window_query_results(self.connection[self.tag][query], parent=self.query_results_table)

    def __run_query(self, sender, app_data, user_data):
        if sender == self.__run_query_button:
            query = dpg.get_value(self.sql_query_box)
        
        try:
            data = self.connection.cur_execute(self.tag, query, save=False, headers=True)
            self._window_query_results(data, parent=self.query_results_table)
        except DBError as e:
            self.__connection_error(e)





    def window(self):
        # entire window
        with dpg.window(label='SQL Query Portal', show=False, tag=self.tag, height=600, width=800): # SQL PROMPT
            with dpg.menu_bar():
                with dpg.menu(label='Menu'):
                    dpg.add_menu_item(label='Refresh', callback=self.refresh)
            
            with dpg.child_window(height=400, autosize_x=True):
                 
                # first rectangle, tabs of db and db tableself.placeholder
                with dpg.group(horizontal=True):
                    with dpg.tab_bar():
                        with dpg.tab(label='All Databases'):
                            self.sql_databases_listbox = dpg.add_listbox(width=200, num_items=20, callback=self.__get_db_tables)  
                        with dpg.tab(label='Database Tables'):
                            self.sql_tables_listbox = dpg.add_listbox(width=200, num_items=20, callback=self.__get_table_columns)  # 1 item is 17.5 px in height

                    # write queries here 
                    with dpg.tab_bar():
                        with dpg.tab(label='SQL Queries'):
                            self.sql_query_box = dpg.add_input_text(multiline=True, height=350, width=-1, default_value='SQL Queries go here', tab_input=True) 




            # options underneath query writer input box
            with dpg.group(horizontal=True):
                with dpg.child_window(height=45, width=200):
                    self.__db_selected = dpg.add_text(default_value='')
                with dpg.child_window(height=45, autosize_x=True):
                    with dpg.group(horizontal=True):
                        self.__run_query_button = dpg.add_button(label='Run Query', callback=self.__run_query, tag='sql-button')
                        dpg.add_button(label='Export..')
                        with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                            with dpg.group(horizontal=True):
                                with dpg.group():
                                    dpg.add_text('Export Query:')
                                    dpg.add_separator()
                                    self.__export_sql_file_button = dpg.add_button(label='Export SQL Query as .sql', callback=lambda: dpg.configure_item(self.__sql_save, show=True, label='Export SQL Query as .sql', user_data=self.__export_sql_file_button))   # TODO: refactor
                                with dpg.group():
                                    dpg.add_text('Export Data:')
                                    dpg.add_separator()                                                                
                                    self.__export_csv_file_button = dpg.add_button(label='Export Data as CSV', callback=lambda: dpg.configure_item(self.__sql_save, show=True, label='Save Data as .csv', user_data=self.__export_csv_file_button))
                                    self.__export_sql_view_button = dpg.add_button(label='Write Data to Server as View', callback=lambda: dpg.configure_item(self.__sql_push_view, show=True))

            # hidden file browser
            with dpg.file_dialog(label="File Directory", width=300, height=400, show=False, user_data=None,callback=lambda a, s, u, contents: self.__save_file(a, s, u, self.contents)) as self.__sql_save: # NOTE using lambda as a closure, to get data w.r.t self and then moving to a static function
                dpg.add_file_extension(".sql", color=(179, 217, 255))
                dpg.add_file_extension(".csv", color=(255, 255, 179))

            # SQL View Maker
            with dpg.window(label='Create View from Current Query', width=300, height=100, show=False) as self.__sql_push_view:
                dpg.add_text('SQL View Name:')
                dpg.add_separator()
                self.__sql_view_name = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_button(label='OK', callback=self.__create_view) 
                    dpg.add_button(label='Cancel', callback=lambda: dpg.configure_item(self.__sql_push_view, show=False))              



            # Table 
            with dpg.child_window():  
                with dpg.group():
                    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                borders_outerV=True, borders_innerH=True, borders_outerH=True, tag='sql-table-view') as self.query_results_table:
                                pass


        
    def toggle(self):
        return super().toggle()


# HERE 
class SaapPortal(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)
        self.zipcode_list_selection = None 
        self.state_list_selection = None
        self.type_list_selection = None
        
        self.total_sales = [] 
        self.total_dates = []
        self.total_purchaes = []


    def __setup(self, connection: ConnectionHandler):
        return super().setup(connection)
    

    def setup(self, connection: ConnectionHandler):
        self.__setup(connection=connection)
        setup_dict = {
            self.zip_filter_set:'SELECT DISTINCT(cust_zip) FROM cdw_sapp_customer;',
            self.state_filter_set:'SELECT DISTINCT(transaction_type) FROM cdw_sapp_credit_card;',
            self.tansaction_filter_sets:'SELECT DISTINCT(branch_state) FROM cdw_sapp_branch ORDER BY 1;' 
        }

        for key, value in setup_dict.items():
            connection.cur_execute(self.tag, value, headers=False, database='db_capstone')
            data = self._collect_items(connection[self.tag][value])
            self._create_dropdown_filter(collection=data,parent_window=key)


    def _create_dropdown_filter(self, collection: list, parent_window: str | int, callback: Optional[FunctionType] = None):
        if parent_window == self.zip_filter_set:
            callback = self.zip_callback
        super()._create_dropdown_filter(collection, parent_window, callback)  # will iterate through from the parent class, then I can extend functionality
            
    


    def _select_one(self, sender: str | int, current_item: str | int, app_data: Optional[Union[str, int]] = None, user_data: Optional[Union[str, int]] = None):
        if current_item is None:
            pass
        else:
            if sender != current_item:
                dpg.set_value(current_item, False)
        current_item = sender
        return current_item

    

    # callback has to be tied to select one like this for now
    def zip_callback(self, sender, app_data, user_data):

        self.total_sales = []
        self.total_dates = []
        def create_query(user_data):
            select_transactions_query = f"""SELECT 
                COUNT(DISTINCT(transaction_id)) AS `Number of Transactions`, 
                ROUND(SUM(DISTINCT(transaction_value)), 2) AS `Total Sales`,
                MONTH(timeid) AS `Date`

                FROM cdw_sapp_credit_card
                LEFT JOIN cdw_sapp_customer ON cust_ssn = ssn
                WHERE cust_zip = {user_data}
                GROUP BY `Date`
                ORDER BY 3;
            """
            return select_transactions_query
        
        self.zipcode_list_selection = self._select_one(sender, current_item=self.zipcode_list_selection)
        query = create_query(user_data=user_data)
        self.connection.cur_execute(self.tag, query, database='db_capstone')
        print(self.connection[self.tag][query])


        for index in range(1, len(self.connection[self.tag][query]) -1):
            total_sales = self.connection[self.tag][query][index][1]
            self.total_sales.insert(index -1, total_sales)
            total_dates = self.connection[self.tag][query][index][2]
            self.total_dates.insert(index -1, total_dates)

        print(type(self.total_dates[0]))
        print(self.total_sales)
        print(self.total_dates)

        dpg.set_value(self.sales_per_zip_plot_line, [self.total_dates, self.total_sales])
        dpg.set_axis_limits(self.sales_per_zip_plot_revenue, 0, max(self.total_sales))
        dpg.set_item_label(self.sales_per_zip_plot_line, f'Sales in 2018 for zipcode: {user_data}')


        self._window_query_results(self.connection[self.tag][query], self.query_transactions_per_zip)




    




    def window(self):
        # main window
        with dpg.window(label='SaaP Bank Data-Mart Portal', height=630, width=743, tag=self.tag):
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
                                                with dpg.plot(width=480, height=450) as self.sales_per_zip_plot:
                                                    self.sales_per_zip_plot_x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Month")
                                                    dpg.set_axis_limits(dpg.last_item(), 1, 12)
                                                    ticks = [[f"{str(num)}", num] for num in range(1, 13)]
                                                    print(ticks)

                                                    dpg.set_axis_ticks(self.sales_per_zip_plot_x_axis, ticks)

                                                    self.sales_per_zip_plot_revenue = dpg.add_plot_axis(dpg.mvYAxis, label="Sales Revenue")
                                                    self.sales_per_zip_plot_line = dpg.add_area_series(self.total_dates, 
                                                                        self.total_purchaes, 
                                                                        parent=self.sales_per_zip_plot_revenue, 
                                                                        label='Total sales Revenue per Zipcode in 2018',
                                                                        fill=[[0, 225, 0]]
                                                                        )
                                                with dpg.group():
                                                    dpg.add_text('Zip codes:')
                                                    dpg.add_input_text(width=200, callback=lambda s, a: dpg.set_value(self.zip_filter_set, a))
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    
                                                    # will populate with zip codes
                                                    with dpg.child_window(width=200, height=160) as self.zipcodes:
                                                        pass
                                                        with dpg.filter_set() as self.zip_filter_set:
                                                            pass
                                                    

                                                    #dpg.add_date_picker(level=dpg.mvDatePickerLevel_Month, default_value={'year':118, 'month':0}, callback=lambda a, s, u: print(a, s, u))
                                                    
                                                
                                                    with dpg.group():  # custom calendar b/c I don't need dates as granular as days for this data                                                            
                                                        date_data = dpg.add_listbox(items=[2018], num_items=2, width=200) 
                                                        with dpg.group(horizontal=True, horizontal_spacing=0):
                                                            dpg.add_button(height=50, width=50, label='Jan', user_data=1)
                                                            dpg.add_button(height=50, width=50, label='Feb', user_data=2)
                                                            dpg.add_button(height=50, width=50, label='Mar', user_data=3)
                                                            dpg.add_button(height=50, width=50, label='Apr', user_data=4)
                                                        
                                                        with dpg.group(horizontal=True, horizontal_spacing=0):
                                                            dpg.add_button(height=50, width=50, label='May', user_data=5)
                                                            dpg.add_button(height=50, width=50, label='Jun', user_data=6)
                                                            dpg.add_button(height=50, width=50, label='Jul', user_data=7)
                                                            dpg.add_button(height=50, width=50, label='Aug', user_data=8)
                                                            
                                                        with dpg.group(horizontal=True, horizontal_spacing=0):
                                                            dpg.add_button(height=50, width=50, label='Sep', user_data=9)
                                                            dpg.add_button(height=50, width=50, label='Oct', user_data=10)
                                                            dpg.add_button(height=50, width=50, label='Nov', user_data=11)
                                                            dpg.add_button(height=50, width=50, label='Dec', user_data=12)
                                                    
                                                    with dpg.tooltip(date_data):
                                                        dpg.add_text('This dataset contains data from 2018 only')        
                                                        


                                                    
                                                    dpg.add_button(label='Search', width= 200)
                                            dpg.add_separator()
                                            with dpg.tree_node(label='Transactions per Zipcode:'):
                                                with dpg.child_window(height=400, width=-1, border=False):
                                                    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                                resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                                borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_zip:
                                                                pass     

                                                    
                                        # Transactions 2: By Type
                                        with dpg.tab(label='Transactions by Type:'):
                                            dpg.add_text('Display the number and total values of transactions for a given type.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                dpg.add_plot(width=480, height=450)
                                                with dpg.group():
                                                    dpg.add_text('Transaction Types:')
                                                    dpg.add_input_text(width=-1, callback=lambda s, a:dpg.set_value(self.tansaction_filter_sets, a))  # decided to make everything a filter, its cleaner
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    with dpg.child_window(width=-1, height=160) as self.transaction_types:
                                                        with dpg.filter_set() as self.tansaction_filter_sets:
                                                            pass

                                            with dpg.collapsing_header(label='Transactions per Type'):
                                                with dpg.child_window(height=400, width=-1):
                                                    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                                resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                                borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_type:
                                                                pass     

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

                                            with dpg.collapsing_header(label='Transactions by State, Branch:'):
                                                with dpg.child_window(height=400, width=-1):
                                                    with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                                resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                                borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_state_branch:
                                                                pass  


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
                
                                                


                                   






