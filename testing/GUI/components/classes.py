import dearpygui.dearpygui as dpg
import numpy as np
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
        
        #### WHICH BUTTON OF EACH WINDOW IS CURRENTLY SELECTED ####
        self.zipcode_list_selection = None 
        self.currently_selected_state = None
        self.type_list_selection = None
        self.zip_list_selection = None
        self.zipcode_state_list_selection = None

        #### DATASET CONTAINERS #### 
        self.total_sales = [] 
        self.total_dates = []
        
        self.total_purchaes = []
        self.transaction_types_pie_series_data = []
        self.transaction_types_pie_series_strings = []

        # state vs company year line plot
        self.state_transactions_year = []
        self.total_transactions_year = []
        self.state_vs_total_transactions_x = []

        # pie chart, transaction types and values given current state
        self.transaction_value_per_type_given_state = []
        self.transaction_value_per_type_given_state_strings = []

        # data for region
        self.zips_for_region = []
        


    def __setup(self, connection: ConnectionHandler):
        return super().setup(connection)
    

    def setup(self, connection: ConnectionHandler):
        self.__setup(connection=connection)
        setup_dict = {
            self.zip_filter_set:'SELECT DISTINCT(cust_zip) FROM cdw_sapp_customer;',
            self.state_filter_set:'SELECT DISTINCT(branch_state) FROM cdw_sapp_branch ORDER BY 1;',
            self.tansaction_filter_sets:'SELECT DISTINCT(transaction_type) FROM cdw_sapp_credit_card;'
        }



        for key, value in setup_dict.items():
            connection.cur_execute(self.tag, value, headers=False, database='db_capstone')
            data = self._collect_items(connection[self.tag][value])
            self._create_dropdown_filter(collection=data,parent_window=key)
        self.create_transaction_piechart()

        self.create_transaction_piechart()

    def _create_dropdown_filter(self, collection: list, parent_window: str | int, callback: Optional[FunctionType] = None):
        if parent_window == self.zip_filter_set:
            callback = self.zip_callback
        elif parent_window == self.state_filter_set:
            callback = self.state_callback
        super()._create_dropdown_filter(collection, parent_window, callback)  # will iterate through from the parent class, then I can extend functionality
            
    


    def _select_one(self, sender: str | int, current_item: str | int, app_data: Optional[Union[str, int]] = None, user_data: Optional[Union[str, int]] = None):
        if current_item is None:
            pass
        else:
            if sender != current_item:
                try:
                    dpg.set_value(current_item, False)
                except:
                    pass
        
        current_item = sender
        return current_item

    def state_report_query(self, user_data):
        self.state_transactions_year = []
        self.total_transactions_year = []  # add this to init
        self.state_vs_total_transactions_x = []  # add this to init as well
        query_state_transaction_value = f"""
        SELECT 
            /*
            Comparing Total Monthly revenue for the company vs the state
            */
            `Total Transaction Value`, 
            `Transaction Value for State`, 
            t.Month, 
            CONCAT('$', FORMAT(`Total Transaction Value`, 2)) AS `Formatted Total`, 
            CONCAT('$', FORMAT(`Transaction Value for State`, 2)) AS `Formatted State`
        FROM 
            /*
            Sum the transaction values, 
            get the month of a given transaction, 
            from the view I created
            group by month
            make a temp table t
            */ 
            (SELECT
            round(sum(transaction_value), 2) AS `Total Transaction Value`,
            MONTH(timeid) AS Month  
            FROM saap_portal_breakdown
            GROUP BY Month) t
            /*
            sum transaction values,
            get month
            from view I created
            where customer state is user selection
            group by month s
            */
        JOIN 
            (SELECT round(sum(transaction_value), 2) AS `Transaction Value for State`,
            MONTH(timeid) AS Month
            FROM saap_portal_breakdown
            WHERE cust_state = '{user_data}'
            GROUP BY Month) s 
            ON t.Month = s.Month;
        """
        self.connection.cur_execute(self.tag, query_state_transaction_value, database='db_capstone')


        for index, row in enumerate(self.connection[self.tag][query_state_transaction_value]):
            if index != 0:
                self.total_transactions_year.insert(index, row[0])
                self.state_transactions_year.insert(index, row[1])
                self.state_vs_total_transactions_x.insert(index, row[2]) 
        
        # TODO Refactor, set up as a dict like the setup function for this class
        dpg.configure_item(self.plot_company_linechart,
                           x=self.state_vs_total_transactions_x,
                           y=self.total_transactions_year)
        
        dpg.configure_item(self.plot_state_linechart,
                           x=self.state_vs_total_transactions_x,
                            y=self.state_transactions_year)
        
        # dpg.configure_item(self.plot_state_linechart_borrowed,
        #                    x=self.state_vs_total_transactions_x,
        #                    y=self.state_transactions_year)

        ymin = min(self.total_transactions_year) 
        state_ymin = min(self.state_transactions_year) 
        state_ymax = max(self.state_transactions_year) 
        self.ymax = max(self.total_transactions_year)
        state_share = np.sum(self.state_transactions_year)
        total_share = np.sum(self.total_transactions_year)
        #state_share = sum(self.state_transactions_year)
        #total_share = sum(self.total_transactions_year)
    

        dpg.set_axis_limits(self.plot_y_axis_company, (ymin * .99), (self.ymax * 1.009))
        dpg.set_axis_limits(self.plot_y_axis_state, (state_ymin * .99), (state_ymax * 1.009))

        dpg.configure_item(self.pie_state_company, 
                           values=[state_share, total_share],
                           labels=[user_data, 'Company'])
        

        # kind of wonky code formatting but it has to be like this for now.
        # GUI does not handle carriage returns or backspaces. 
        report_string = \
        f""" 
{user_data}'s transaction volume represents {np.format_float_positional((state_share/total_share) * 100, precision=2)}% of the companies total transactions for 2018.\n
{user_data}'s transaction volume yearly low ${state_ymin:,}.\n
{user_data}'s transaction volume yearly high ${state_ymax:,}
        """

        dpg.configure_item(self.report_text, default_value=report_string,)

        self.zip_for_state_report_query(user_data)
        




    def zip_for_state_report_query(self, user_data):
        """
        This will provide a list of zips related to the selected state.
        State is selected through state_report_query 
        """
        dpg.delete_item(self.zip_state_filter_set, children_only=True)

        query_zips_for_state = f"""
        SELECT 
                *, 
                CONCAT('$', FORMAT(`Sum Transaction per Zip`, 2)) AS `Formatted Zip Sum`, 
                CONCAT('$', FORMAT(`State Transaction Revenue`, 2)) AS `Formatted State Revenue`, 
                ROUND((`Sum Transaction per Zip` / `State Transaction Revenue` ) * 100, 2) AS `Percentage of Revenue to State`
        FROM 
            /*
            custom table made of:
            customer state,
            customer zip codes,
            sum of all transaction values (per zip), *
            sum of all state revenue (select subquery),
            grouped by zip (to divide sum of all transaction values) *
            NOTE: 
            The only reason why I have this custom table is so I can have formatted tables on the outside, and perform a percentage per zip operation on these aggrigations
            */
            (SELECT
                cust_state AS `State`,
                cust_zip AS Zip,
                ROUND(sum(transaction_value), 2) AS `Sum Transaction per Zip`,
                (
                    SELECT 
                        ROUND(SUM(transaction_value), 2) 
                    FROM 
                        saap_portal_breakdown 
                        WHERE cust_state = '{user_data}') AS `State Transaction Revenue`
                        -- looking for total state revenue
                FROM saap_portal_breakdown WHERE cust_state = '{user_data}'
                GROUP BY cust_zip) t 
        ORDER BY 7 DESC;
        """
        # this is 147% faster than another join I made
        # recap:
        # 0 state 1 zip # 2 sum (per zip) # 3 sum (entire state) # 4 format of sum (per zip) # 5 format of sum (per state)  # 6 percent
        self.connection.cur_execute(self.tag, query_zips_for_state, database='db_capstone', headers=True)

        self.zips_for_region = []
        region_contribution_to_state = []


        for index, row in enumerate(self.connection[self.tag][query_zips_for_state]):
            
            if index != 0:
                self.zips_for_region.insert(index - 1, row[1])
                region_contribution_to_state.insert(index - 1, row[6])


        self._create_dropdown_filter(self.zips_for_region,
                                     parent_window=self.zip_state_filter_set,
                                     callback=self.zip_state_callback)
        
        print(region_contribution_to_state)
        dpg.configure_item(self.pie_state_region, 
                           values=region_contribution_to_state,
                           labels=self.zips_for_region)



    def state_callback(self, sender, app_data, user_data):
        # when the state button is pressed, a signal needs to go out to specify one can be
        # set to true. 

        # the button tag is an int, the label represents the state, the user_data contains
        # the state. 

        self.transaction_value_per_type_given_state = []

        # transaction type, transaction value, formatted transaction values
        def create_query(user_data):
            query = f"""SELECT
		            *, 
		            CONCAT( '$', (FORMAT(`Total Transaction Value`, 2))) AS `Formatted Values (USD)`
                FROM 
                    (SELECT 
                    transaction_type AS `Transaction Type`,
                    round(sum(transaction_value), 2) AS `Total Transaction Value` 
                    
                    FROM saap_portal_breakdown
                    WHERE cust_state = '{user_data}'
                    GROUP BY 1) t """      

            return query

        # NOTE: refactor this 
        self.currently_selected_state = self._select_one(sender, current_item=self.currently_selected_state)
        query = create_query(user_data)
        self.connection.cur_execute(self.tag, query, database='db_capstone')
        # the only variable data is the number of rows returned, where its going. 
        # repackage query, select one?

        # tuple of (type, value)
        # zeroth-index is headers 
        self.transaction_value_per_type_given_state_strings = [value[0] for value in self.connection[self.tag][query][1:]]
        self.transaction_value_per_type_given_state = [value[1] for value in self.connection[self.tag][query][1:]]

        print(self.transaction_value_per_type_given_state)
        print("")
        print(self.transaction_value_per_type_given_state_strings)

        dpg.configure_item(self.piechart_state_data,
                        values=self.transaction_value_per_type_given_state, 
                        labels=self.transaction_value_per_type_given_state_strings)
        
        dpg.configure_item(self.state_popout_window, label=f"Transactions by State Breakdown, for: {user_data}")
        
        self._window_query_results(self.connection[self.tag][query], self.query_transaction_value_per_type_given_state)

        self.state_report_query(user_data)
        

    # callback has to be tied to select one like this for now
    def zip_state_callback(self, sender, app_data, user_data):

        # per month
        
        zipcode_number_of_transactions = []
        zipcode_transaction_value = []
        zipcode_transaction_value_average = []
        zipcode_month = []
        

        query = f"""
        SELECT 
            COUNT(*) AS `Number of Transactions`, 
            ROUND(SUM(transaction_value), 2) AS `Total Sales for Month`,
            MONTH(timeid) AS `Month`,
            ROUND(avg(transaction_value), 2) AS `Average Transaction Value`
        FROM saap_portal_breakdown
        WHERE cust_zip = '{user_data}'
        GROUP BY `Month`
        ORDER BY 3;
        """

        
        self.zipcode_state_list_selection = self._select_one(sender, current_item=self.zipcode_state_list_selection)
        self.connection.cur_execute(self.tag, query, database='db_capstone')

        # 0 transaction count; 1 transaction value, 2 month, 3 average  
        for index, row in enumerate(self.connection[self.tag][query]):
            if index != 0:
                zipcode_number_of_transactions.insert(index - 1, row[0])
                zipcode_transaction_value.insert(index - 1, row[1])
                zipcode_month.insert(index - 1, row[2])
                zipcode_transaction_value_average.insert(index - 1, row[3])


        # offset 1 is placed on 1, 4, 7
        # offset 2 is placed on 2, 5, 8
        # 3, 6, 9 are empty spaces for breathing room
        month_offset_1 = [num for num in range(1, 37, 3)]
        month_offset_2 = [num for num in range(2, 37, 3)]
        

        # print(month_offset_1)
        # print(month_offset_2)
            

        dpg.delete_item(self.plot_y_axis_zip, children_only=True)
        
        # each 1 tick is actually 3 units long
        # 1[2]-3, 4[5]-6, 7[8]-9, 10[11]-12
        # month1, month2, month3, month4
        dpg.set_axis_ticks(self.plot_x_axis_zip, [[str(num), num * 3 ] for num in range(1, 13)])

        
        dpg.set_axis_limits(self.plot_y_axis_zip, 
                            0, 
                            max(zipcode_transaction_value_average) * 1.099)
        
        dpg.set_axis_limits(self.plot_x_axis_zip, 0, 36)

            
        dpg.add_bar_series(month_offset_1, 
                           zipcode_number_of_transactions, 
                           label=self.connection[self.tag][query][0][0],
                           parent=self.plot_y_axis_zip)

        
        dpg.add_bar_series(month_offset_2, 
                           zipcode_transaction_value_average, 
                           label=self.connection[self.tag][query][0][3],
                           parent=self.plot_y_axis_zip)


    # callback has to be tied to select one like this for now
    def zip_callback(self, sender, app_data, user_data):

        self.total_sales = []
        self.total_dates = []
        def create_query(user_data):
            select_transactions_query = f"""SELECT 
                COUNT(DISTINCT(transaction_id)) AS `Number of Transactions`, 
                ROUND(SUM(DISTINCT(transaction_value)), 2) AS `Total Sales`,
                MONTH(timeid) AS `Month`

                FROM cdw_sapp_credit_card
                LEFT JOIN cdw_sapp_customer ON cust_ssn = ssn
                WHERE cust_zip = {user_data}
                GROUP BY `Month`
                ORDER BY 3;
            """
            return select_transactions_query
        
        self.zipcode_list_selection = self._select_one(sender, current_item=self.zipcode_list_selection)
        query = create_query(user_data=user_data)  # need to create b/c getting zip value
        self.connection.cur_execute(self.tag, query, database='db_capstone')
        #print(self.connection[self.tag][query])


        for index in range(1, len(self.connection[self.tag][query])):  # start at 1 b/c 0 is a tuple of headers
            total_sales = self.connection[self.tag][query][index][1]  # (num of trans, sales, date)
            self.total_sales.insert(index -1, total_sales)  # insert at zero, insert, at 1, etc
            total_dates = self.connection[self.tag][query][index][2]
            self.total_dates.insert(index -1, total_dates)

        # print(type(self.total_dates[0]))
        # print(self.total_sales)
        # print(self.total_dates)

        dpg.set_value(self.sales_per_zip_plot_line, [self.total_dates, self.total_sales])
        dpg.set_axis_limits(self.sales_per_zip_plot_y_axis, 0, max(self.total_sales))
        dpg.set_item_label(self.sales_per_zip_plot_line, f'Sales in 2018 for zipcode: {user_data}')
        
        #  user data contains the zipcode number, the self zipcode is just an integer representing the button representing the zipcode
        dpg.configure_item(self.zip_popout_window,  
                            label=f"Zipcode Data for Zipcode: {dpg.get_item_user_data(self.zipcode_list_selection)}")


        self._window_query_results(self.connection[self.tag][query], self.query_transactions_per_zip)


    def create_transaction_piechart(self):
        self.transaction_types_pie_series_data = []
        self.transaction_types_pie_series_strings = []

        transaction_types_sum = """
        SELECT 
		transaction_type AS `Transaction Type`,
		FORMAT(sum(transaction_value), 2) AS `Formatted Values`,
		ROUND(sum(transaction_value), 2) AS `Rounded Series Values`
		
        FROM cdw_sapp_credit_card
        GROUP BY 1
        """

        self.connection.cur_execute(self.tag, transaction_types_sum, database="db_capstone")

        self.transaction_types_pie_series_strings = [value[0] for value in self.connection[self.tag][transaction_types_sum][1:]]
        self.transaction_types_pie_series_data = [value[2] for value in self.connection[self.tag][transaction_types_sum][1:]]

        print(self.transaction_types_pie_series_strings)
        print("")
        print(self.transaction_types_pie_series_data)
        dpg.configure_item(self.transaction_types_piechart, values=self.transaction_types_pie_series_data, labels=self.transaction_types_pie_series_strings)
        
        self._window_query_results(self.connection[self.tag][transaction_types_sum], self.query_transactions_per_type)








    




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
                                            dpg.add_text('Display the transactions made by customers living in a given zip code for a given year.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                # Transaction 1 Plot
                                                with dpg.plot(width=480, height=450, anti_aliased=True, no_mouse_pos=True) as self.sales_per_zip_plot:
                                                    # x and y axis
                                                    self.sales_per_zip_plot_x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Month")
                                                    self.sales_per_zip_plot_y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Sales Revenue in USD")
                                                    # plot, line, x and y series dataset ⭐
                                                    self.sales_per_zip_plot_line = dpg.add_line_series(self.total_dates, 
                                                                        self.total_purchaes, 
                                                                        parent=self.sales_per_zip_plot_y_axis, 
                                                                        label='Total sales Revenue per Zipcode in 2018'
                                                                        )
                                                    # axis limits
                                                    dpg.set_axis_limits(self.sales_per_zip_plot_x_axis, 1, 12)  # have to set limits this way and not direct through plot axis
                                                    # arbitrary y axis limits, to prevent panning before loaded dataset and not have 0, 1 initial y values                                               
                                                    dpg.set_axis_limits(self.sales_per_zip_plot_y_axis, 0, 1000)

                                                    # x axis tickss
                                                    ticks = [[f"{str(num)}", num] for num in range(1, 13)]
                                                    dpg.set_axis_ticks(self.sales_per_zip_plot_x_axis, ticks) 
                                            
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
                                                                                                                                                        
                                                    with dpg.group():  # custom calendar b/c I don't need dates as granular as days for this data                                                            
                                                        date_data = dpg.add_listbox(items=[2018], num_items=2, width=200) 
                                                    
                                                    with dpg.tooltip(date_data):
                                                        dpg.add_text('This dataset contains data from 2018 only')                                                                
                                                    
                                                    dpg.add_button(label=f'Show Data', width= 200, callback=lambda: dpg.configure_item(self.zip_popout_window, show=True, pos=dpg.get_mouse_pos()))
                                                    with dpg.window(show=False,label='Zipcode Data for: ') as self.zip_popout_window:
                                                            with dpg.child_window(height=300,width=300,border=False):  
                                                                with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                                            resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                                            borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_zip:
                                                                            pass   



                                                    
                                        # Transactions 2: By Type
                                        with dpg.tab(label='Transactions by Type'):
                                            dpg.add_text('Display the number and total values of transactions for a given type.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                # Transaction 2 Plot
                                                with dpg.plot(width=480, height=450, no_mouse_pos=True):
                                                    dpg.add_plot_legend()
                                                    
                                                    # x axis
                                                    self.transaction_types_x_axis = dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                                                    
                                                    
                                                    # axis limits
                                                    #dpg.set_axis_limits(self.transaction_types_x_axis, 0, 1)
                                                    #dpg.set_axis_limits()
                                                    
                                                    # plot, pie chart ⭐
                                                    with dpg.plot_axis(dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True) as self.transaction_types_y_axis:
                                                        self.transaction_types_piechart = dpg.add_pie_series(0.5, 0.5, 0.5, 
                                                                                                             self.transaction_types_pie_series_data, 
                                                                                                             self.transaction_types_pie_series_strings,
                                                                                                             format='%0.2f')


                                                with dpg.group():
                                                    dpg.add_text('Transaction Types:')
                                                    dpg.add_input_text(width=200, callback=lambda s, a:dpg.set_value(self.tansaction_filter_sets, a))  # decided to make everything a filter, its cleaner
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    with dpg.child_window(width=200, height=160) as self.transaction_types:
                                                        with dpg.filter_set() as self.tansaction_filter_sets:
                                                            pass
                                                    

                                            dpg.add_button(label=f'Show Data', width= 200, callback=lambda: dpg.configure_item(self.transaction_popout_window, show=True, pos=dpg.get_mouse_pos()))
                                            with dpg.window(label='Transaction Type Data for 2018', show=False, height=214, width=419) as self.transaction_popout_window:
                                                with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                            resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                            borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_type:
                                                            pass     

                                        # Transactions 3: Transactions for branches by state
                                        with dpg.tab(label='Transactions by State'):
                                            dpg.add_text('Display the number and total values of transactions for branches in a given state. Values in USD.')
                                            dpg.add_separator()
                                            with dpg.group(horizontal=True):
                                                with dpg.plot(width=480, height=450, no_mouse_pos=True, anti_aliased=True) as self.piechart_transaction_value_per_type_given_state:

                                                    dpg.add_plot_legend()
                                                    
                                                    # x axis
                                                    self.piechart_state_x_axis = dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True, label='Transaction Value by State')

                                                    
                                                    
                                                    # axis limits
                                                    #dpg.set_axis_limits(self.transaction_types_x_axis, 0, 1)
                                                    #dpg.set_axis_limits()
                                                    
                                                    # plot, pie chart ⭐
                                                    with dpg.plot_axis(dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True) as self.transaction_types_y_axis:
                                                        self.piechart_state_data = dpg.add_pie_series(0.5, 0.5, 0.5, 
                                                                                                            self.transaction_value_per_type_given_state, 
                                                                                                            self.transaction_value_per_type_given_state_strings,
                                                                                                            format='%0.2f')                                                    


                                                with dpg.group():
                                                    dpg.add_text('Transactions by State:')
                                                    dpg.add_input_text(width=200, callback=lambda s, a:dpg.set_value(self.state_filter_set, a))
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    with dpg.child_window(width=200, height=160) as self.transaction_types:
                                                        with dpg.filter_set() as self.state_filter_set:
                                                            pass
                                                   
                                                    with dpg.group():  # custom calendar b/c I don't need dates as granular as days for this data                                                            
                                                        date_data = dpg.add_listbox(items=[2018], num_items=2, width=200)                     
                                                    with dpg.tooltip(date_data):
                                                        dpg.add_text('This dataset contains data from 2018 only')    
                                                    
                                                    dpg.add_button(label='Show Data', width=200, callback=lambda: dpg.configure_item(self.state_popout_window, show=True, pos=dpg.get_mouse_pos()))                                    
                                                    dpg.add_button(label='State Report', width=200, callback= lambda: dpg.configure_item(self.state_report, show=True, pos=dpg.get_mouse_pos()))
                                                    dpg.add_button(label='Region Report', width=200, callback= lambda: dpg.configure_item(self.region_report, show=True, pos=dpg.get_mouse_pos()))


                                            with dpg.window(label='State Report', show=False) as self.state_report:
                                                with dpg.group(horizontal=True, parent=self.state_report):
                                                    with dpg.group():
                                                        with dpg.plot(label='Total Transactions', anti_aliased=True) as self.plot_state_vs_company_transactions:
                                                            # x axis
                                                            self.plot_x_axis_company = dpg.add_plot_axis(dpg.mvXAxis, label='Month')

                                                            # plot, line, x and y series dataset

                                                            # state vs company, y axis and plot
                                                            self.plot_y_axis_company = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Value')


                                                            self.plot_company_linechart = dpg.add_line_series(self.state_vs_total_transactions_x,
                                                                                                                    self.total_transactions_year,
                                                                                                                    parent=self.plot_y_axis_company
                                                            )
                                                            
                                                            # limits
                                                            dpg.set_axis_limits(self.plot_x_axis_company, 1, 12)
                                                            dpg.set_axis_limits(self.plot_y_axis_company, 0, 1000)

                                                            # ticks
                                                            self.x_ticks = [[f"{str(num)}", num] for num in range(1, 13)]
                                                            dpg.set_axis_ticks(self.plot_x_axis_company, self.x_ticks)

                                                        with dpg.plot(label='State Transactions', anti_aliased=True) as self.plot_state_vs_company_transactions_2:
                                                            self.plot_x_axis_state = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                                            

                                                            self.plot_y_axis_state = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Value')

                                                            self.plot_state_linechart = dpg.add_line_series(self.state_vs_total_transactions_x,
                                                                                                            self.state_transactions_year,
                                                                                                            parent=self.plot_y_axis_state

                                                            )
                                                            
                                                            dpg.set_axis_limits(self.plot_x_axis_state, 1, 12)
                                                            dpg.set_axis_ticks(self.plot_x_axis_state, self.x_ticks)


                                                    with dpg.group() as self.piechart_report_group:
                                                        with dpg.plot(label='State Transactions as a Percent of Total Transactions', anti_aliased=True, equal_aspects=True):
                                                            dpg.add_plot_legend()
                                                    
                                                            # x axis
                                                            dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                                                            
                                                            
                                                                # axis limits
                                                                #dpg.set_axis_limits(self.transaction_types_x_axis, 0, 1)
                                                                #dpg.set_axis_limits()
                                                            
                                                                # plot, pie chart ⭐
                                                            with dpg.plot_axis(dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True) as self.company_state_percent:
                                                                #state_over_company = self.state_transactions_year / self.total_transactions_year

                                                                self.pie_state_company = dpg.add_pie_series(0.5, 0.5, 0.5,
                                                                            [], 
                                                                            [],
                                                                            format='%0.2f')
                                                        dpg.add_text("State Report")
                                                        dpg.add_separator()
                                                        self.report_text = dpg.add_text(wrap=200)
                                                                            
                                                        
                                            with dpg.window(label='Region Report', show=False) as self.region_report:
                                                with dpg.group(horizontal=True):
                                                    with dpg.group():
                                                        with dpg.plot(label='Region Contribution to State Transaction', anti_aliased=True, equal_aspects=True):
                                                            dpg.add_plot_legend()
                                                    
                                                            # x axis
                                                            dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                                                            
                                                            
                                                                # axis limits
                                                                #dpg.set_axis_limits(self.transaction_types_x_axis, 0, 1)
                                                                #dpg.set_axis_limits()
                                                            
                                                                # plot, pie chart ⭐
                                                            with dpg.plot_axis(dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True) as self.region_state_percent:
                                                                #state_over_company = self.state_transactions_year / self.total_transactions_year

                                                                self.pie_state_region = dpg.add_pie_series(0.5, 0.5, 0.5,
                                                                            [], 
                                                                            [],
                                                                            format='%0.2f')


                                                    with dpg.group():
                                                        dpg.add_text('Zip codes:')
                                                        dpg.add_input_text(width=200, callback=lambda s, a: dpg.set_value(self.zip_state_filter_set, a))
                                                        with dpg.tooltip(dpg.last_item()):
                                                            dpg.add_text('Filter list')
                                                        
                                                        # will populate with zip codes
                                                        with dpg.child_window(width=200, height=160) as self.zipcodes_by_state:
                                                            with dpg.filter_set() as self.zip_state_filter_set:
                                                                pass

                                                        
                                                    dpg.add_text("Region Report")
                                                    dpg.add_separator()

                                                with dpg.group():
                                                    with dpg.plot(label='Transaction Count and Volume', anti_aliased=True) as self.plot_state_vs_company_transactions_2:
                                                        
                                                        dpg.add_plot_legend()


                                                        self.plot_x_axis_zip = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                                        
                                                        self.plot_y_axis_zip = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Value')

                                                        dpg.set_axis_limits(self.plot_x_axis_zip, 1, 24)
                                                        #dpg.set_axis_ticks(self.plot_x_axis_zip, self.x_ticks)


                                                        

                                            # Sql Table show 
                                            with dpg.window(label='Transactions by State Breakdown', show=False, width=475, height=214) as self.state_popout_window:
                                                with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                            resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                            borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transaction_value_per_type_given_state:
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
                
                                                


                                   






