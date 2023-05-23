import dearpygui.dearpygui as dpg
from Components.generic_container import GenericContainerContext, ConnectionHandler, DBError

class QueryPortal(GenericContainerContext):
    
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)


    def __save_file(self, sender, app_data, user_data):  # app_data, user_data is data of sql box 
        from time import sleep


        if user_data == self.__export_sql_file_button:
            with open(file=app_data['file_path_name'], mode='w') as sql_file:
                sql_file.write(dpg.get_value(self.sql_query_box))
            

        elif user_data == self.__export_csv_file_button:
            import csv
            with open(file=app_data['file_path_name'], mode='w', newline='') as query_to_csv:
                #print(app_data, app_data['file_path_name'])
                csv_file = csv.writer(query_to_csv)
                csv_file.writerows(self.current)  # contents is a list of tuples
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
        print(self.connection[self.tag][self.query])

    def __create_view(self):
        def close_and_refresh():
            dpg.configure_item(popup, show=False)
            self.refresh()

        current_query = dpg.get_value(self.sql_query_box)
        name = dpg.get_value(self.__sql_view_name)
        if any(name):
            create_view = f"CREATE VIEW {name} AS\n" + current_query
            try:
                self.connection.cur_execute(self.tag, create_view, save=False)
                dpg.configure_item(self.__sql_push_view, show=False)
                with dpg.window(popup=True, pos=dpg.get_mouse_pos(local=False)) as popup:
                    dpg.add_text('SQL View Saved!')
                    dpg.add_button(label='OK', callback=close_and_refresh)


            except DBError as e:
                self._connection_error(e)
        else:
            e = "You need to write a name first"
            self._connection_error(e)


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


    def _connection_error(self, e):
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
            self._connection_error(e)

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
            self.current = self.connection.cur_execute(self.tag, query, save=False, headers=True)
            self._window_query_results(self.current, parent=self.query_results_table)
        except DBError as e:
            self._connection_error(e)





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
                            self.sql_databases_listbox = dpg.add_listbox(width=250, num_items=16, callback=self.__get_db_tables)  
                        with dpg.tab(label='Database Tables'):
                            self.sql_tables_listbox = dpg.add_listbox(width=250, num_items=16, callback=self.__get_table_columns)  

                    # write queries here 
                    with dpg.tab_bar():
                        with dpg.tab(label='SQL Queries'):
                            self.sql_query_box = dpg.add_input_text(multiline=True, height=360, width=-1, default_value='SQL Queries go here', tab_input=True) 
                        def debug_dpg(item):
                            print(dpg.get_item_info(item))
                            print(dpg.get_value(item))
                        




            # options underneath query writer input box
            with dpg.group(horizontal=True):
                with dpg.child_window(height=60, width=200):
                    self.__db_selected = dpg.add_text(default_value='')
                with dpg.child_window(height=60, autosize_x=True):
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
                                    self.__export_sql_view_button = dpg.add_button(label='Write Data to Server as View', callback=lambda: dpg.configure_item(self.__sql_push_view, show=True, pos=dpg.get_mouse_pos(local=False)))

            # hidden file browser
            with dpg.file_dialog(label="File Directory", width=300, height=400, show=False, user_data=None,callback=self.__save_file) as self.__sql_save: # NOTE using lambda as a closure, to get data w.r.t self and then moving to a static function
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