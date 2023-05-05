import dearpygui.dearpygui as dpg
import numpy as np
from types import FunctionType
from typing import Optional, Union
from Components.generic_container import GenericContainerContext, ConnectionHandler, DBError

class CustomerPortal(GenericContainerContext):
    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)
        self.reporting = "Edit Mode"
        self.mouse_pos = [0, 0]

    def setup(self, connection: ConnectionHandler):
        return super().setup(connection)
    
    def _mouse_move_callback(self, sender, data):
        return super()._mouse_move_callback(sender, data)


    def customer_button(self, sender, app_data, user_data):
        if self.reporting == "Edit Mode":
            self.edit_mode(sender, app_data, user_data)
        elif self.reporting == "Report Mode":
            self.dictionary_cursor = f"{self.tag} Dictionary"
            self.connection.cur(self.dictionary_cursor, dictionary=True)
            self.report_mode(sender, app_data, user_data)


    def edit_or_report_mode(self, sender, app_data, user_data):
        self.reporting = app_data



    def report_mode(self, sender, app_data, user_data):
        # sender = ID, 
        # user_data = cust_id 
        query =f"""
            SELECT
	            DISTINCT(CONCAT(first_name, ' ', middle_name, ' ', last_name)) AS `Name`,
                CONCAT('$', ROUND(SUM(transaction_value), 2)) AS `Total Value of all Transactions`,
                COUNT(DISTINCT(branch_code)) AS `Total Number of Branches Used`,
                COUNT(transaction_id)  AS `Total Transactions`,
                CONCAT( '$', ROUND(AVG(transaction_value), 2)) AS `Average Transaction Value`,
                MAX(timeid) AS `Last Transaction`
            FROM saap_customer_report
            WHERE cust_id = {user_data};
        """

        query_last_branch = f"""
        SELECT 
            branch_code AS `Branch Code`, 
            branch_street AS `Branch Street`, 
            branch_state AS `Branch State`,
            branch_zip AS `Branch Zip`, 
            branch_phone AS `Branch Phone`
        FROM saap_customer_report
        WHERE cust_id = {user_data} AND timeid = (SELECT MAX(timeid) FROM saap_customer_report WHERE cust_id = {user_data})
        GROUP BY timeid;
        """

        query_me_the_money = f"""
        SELECT 
            MONTH(timeid) AS `Month`, ROUND(SUM(transaction_value), 2) AS `Transaction Volume Per Month`
            FROM saap_customer_report
            WHERE cust_id = {user_data}
            GROUP BY `Month`;
        """

        dpg.delete_item(self.report_group, children_only=True)
        report: dict
        last_branch: dict

        report = self.connection.cur_execute(self.dictionary_cursor, query, save=False, database='db_capstone', headers=False)[0]
        last_branch = self.connection.cur_execute(self.dictionary_cursor, query_last_branch, save=False, database='db_capstone', headers=False)[0]
        print(report)
        print(last_branch)
        print(self.connection[self.dictionary_cursor])
        
        for key, value in report.items():
            dpg.add_text(parent=self.report_group, default_value=f"{key}: {str(value)}")

        dpg.add_spacer(parent=self.report_group)
        dpg.add_text(default_value='Last used Branch:', parent=self.report_group)
        dpg.add_separator(parent=self.report_group)

        for key, value in last_branch.items():
            dpg.add_text(parent=self.report_group, default_value=f"{key}: {str(value)}")

        money_report = self.connection.cur_execute(self.tag, query_me_the_money, headers=False, save=False, database='db_capstone')
        # month, amount

        months = [value[0] for value in money_report]
        amounts = [value[1] for value in money_report]

        self.configure_plot(self.single_customer_transaction_volume_plot,
                        x=months, 
                        y1=amounts,
                        number_of_graphs=1
                    )


            
    def edit_mode(self, sender, app_data, user_data):


        row = dpg.get_item_info(sender)['parent']  # a given buttons row ID
        rows_children = dpg.get_item_children(row)[1]  # all items in a given row
        rows_in_table: list
        rows_in_table = dpg.get_item_children(self.customer_table)[1]  # collection of all row IDs in the table
        row_index_number = rows_in_table.index(row) # a given buttons row index number
        row_original_snapshot = [str(item) for item in self.connection[self.tag][self.customer_query][1:][row_index_number]] # [1:] b/c zeroth is always header
        
        # NOTE:
        # rows place in the table is the same as the index number in the original query

        blue = [32, 160, 192]
        mint_green = [46, 255, 175, 232]
        red = [255, 51, 85]
        highlight_blue = [96, 155, 197, 132]
        cust_id = user_data
        
        def change_color_button(color, button):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)
                    dpg.add_theme_color(dpg.mvThemeCol_Button, color)
            dpg.bind_item_theme(button, theme)

        def highlight_selection(item, color):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvInputText):
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12)
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, color)
                    dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 10)
            dpg.bind_item_theme(item, theme)



        # mythemeCol_Framebackground # highlighted text
        # default: 51, 51, 55, 255
        #(96,155,197,132)
        # mystylevar cell padding 6, 10
        # frame rounding 12

        if sender not in self.edit_customer_button_array:
            for index, item in enumerate(rows_children[2:]):  # [2:] b/c skip cust ID, SSN, 
                dpg.delete_item(item)  # have to delete item first, can not instantiate and configure tag ID
                if item !=rows_children[-1]:
                    dpg.add_input_text(default_value=row_original_snapshot[2:][index], parent=row, tag=item, width=-1)
                else:
                    dpg.add_text('Updating...', color=blue, parent=row, tag=item)
                highlight_selection(item, highlight_blue)
            change_color_button(red, sender)

            self.edit_customer_button_array[sender] = row_index_number


        elif sender in self.edit_customer_button_array:
            # NOTE: 
            # calling a function within a function from a popout window

            def cancel_changes():
                for index, item in enumerate(rows_children[2:]):
                    dpg.delete_item(item)
                    dpg.add_text(default_value=row_original_snapshot[2:][index], 
                                    parent=row, 
                                    tag=item)
                
                self.edit_customer_button_array.pop(sender, 0)
                
                change_color_button(mint_green, sender)
                dpg.configure_item(confirmation, show=False)

            def commit_changes():

                modified_row_values = [dpg.get_value(item) for item in rows_children[2:]]
                headers = self.connection[self.tag][self.customer_query][0]
                compiled = {}

                # group attached to popout window
                with dpg.group(parent=confirmation, before=choices):
                    with dpg.group(horizontal=True):
                        with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                            resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                            borders_outerV=True, borders_innerH=True, borders_outerH=True) as show_changes:
                                dpg.add_table_column(label="Header")
                                dpg.add_table_column(label="Old")
                                dpg.add_table_column(label="New")                           


                        for index, header in enumerate(headers[2:-1]):
                            if modified_row_values[index] != row_original_snapshot[2:][index]:
                                compiled[header] = modified_row_values[index]


                                with dpg.table_row(parent=show_changes):
                                    dpg.add_text(header, color=blue)
                                    dpg.add_text(default_value=f"{row_original_snapshot[2:][index]}")
                                    dpg.add_text(default_value=f"{modified_row_values[index]}", color=red)
                        
                def commit_changes_confirmed():
                    print(compiled)
                    query_update = f"""
                    UPDATE cdw_sapp_customer            
                    SET
                    """
                    query_columns = ", ".join(f"{header} = '{compiled[header]}'" for header in compiled)
                    last_updated = f", last_updated = NOW() "
                    where = f"WHERE cust_id = {cust_id};"
                    
                    print(query_update + query_columns + last_updated + where)
                    try:
                        self.connection.cur_execute(self.tag, query_update + query_columns + last_updated + where, database='db_capstone')
                        self.connection.cur_execute(self.tag, "COMMIT;")
                        dpg.delete_item(confirmation, children_only=True)
                        dpg.add_text('Changes Saved!', parent=confirmation)
                        dpg.add_button(label='OK', callback=lambda: dpg.configure_item(confirmation, show=False), parent=confirmation)

                    except DBError as e:
                        print(e)
                        with dpg.window(popup=True):
                            self._connection_error(e)

                    self.refresh_search_like_input()
                    self.edit_customer_button_array.pop(self, 0)
                
                
                dpg.configure_item(confirm, default_value='Are you Sure?')
                dpg.configure_item(yes, callback=commit_changes_confirmed)




            with dpg.window(popup=True, pos=dpg.get_mouse_pos(local=False)) as confirmation:  # dpg.window(popout=True) is snappier than dpg.popout
                
                confirm = dpg.add_text('Commit Changes?')
                with dpg.group(horizontal=True) as choices:
                    yes = dpg.add_button(label='Yes', callback=commit_changes)
                    dpg.add_button(label='Cancel', callback=cancel_changes)
                    dpg.add_button(label='Go back', callback=lambda: dpg.configure_item(confirmation, show=False), parent=choices)



    def refresh_search_like_input(self):
        dpg.delete_item(self.customer_table, children_only=True)
        self.search_like_input()

        
    def search_like_input(self):
        contents_firstname = dpg.get_value(self.first_name)
        contents_lastname = dpg.get_value(self.last_name)
        cust_id = dpg.get_value(self.cust_id)
        # values of empties are empty strings and not None
        # python does not consider empties to be equal to None

        if (contents_firstname !='' or contents_lastname != ''):
            dpg.set_value(self.cust_id, '')

            if (len(contents_firstname) and len(contents_lastname) !=0) and \
                (contents_firstname !=None and contents_lastname !=None):
                self.customer_query = f"""
                SELECT * FROM cdw_sapp_customer
                WHERE first_name LIKE('{contents_firstname}%') AND last_name LIKE ('{contents_lastname}%')
                LIMIT 100;
                """            
            elif (len(contents_firstname) !=0 and contents_firstname !=None):
                self.customer_query = f"""
                SELECT * FROM cdw_sapp_customer
                WHERE first_name LIKE('{contents_firstname}%')
                LIMIT 100;
                """            
            elif (len(contents_lastname) !=0 and contents_lastname !=None):
                self.customer_query = f"""
                SELECT * FROM cdw_sapp_customer
                WHERE last_name LIKE ('{contents_lastname}%')
                LIMIT 100;
                """

            
        if cust_id != '':
            dpg.set_value(self.first_name, '')
            dpg.set_value(self.last_name, '')
            dpg.delete_item(self.customer_table, children_only=True)
            
            self.customer_query = f"""
            SELECT * FROM cdw_sapp_customer
            WHERE cust_id = {cust_id}
            LIMIT 100;
            """

        try:
            self.connection.cur_execute(self.tag, self.customer_query, database='db_capstone')
            self._window_query_results(self.connection[self.tag][self.customer_query], 
                                        parent=self.customer_table, 
                                        button_column_number=0, 
                                        button_callback=self.customer_button
            )
            
            self.edit_customer_button_array = {}
        except UnboundLocalError:
            dpg.delete_item(self.customer_table, children_only=True)
        except DBError:
            dpg.delete_item(self.customer_table, children_only=True)


        if contents_firstname == '' and contents_lastname == '' and cust_id == '':
            dpg.delete_item(self.customer_table, children_only=True)

        






    def window(self):
        
        with dpg.window(label='Customer Menu', width=1506, height=975, tag=self.tag):

            with dpg.tab_bar():

                # Customer details 1 & 2, find and select customer 
                with dpg.tab(label='Customer Account Search'):
                    dpg.add_text('Check Customer Account Details')
                    with dpg.group(horizontal=True):

                        # right side
                        with dpg.group(horizontal=True):
                            with dpg.child_window(width=330, height=450):
                                dpg.add_text('Search for customer with first & last name, or jump to customer id.', wrap=286)
                                dpg.add_spacer()
                                with dpg.group(horizontal=True):
                                    with dpg.group():
                                        dpg.add_text('First name')
                                        self.first_name = dpg.add_input_text(tag='first-name', width=90)
                                    with dpg.group():
                                        dpg.add_text('Last name')
                                        self.last_name = dpg.add_input_text(tag='last-name', width=90)
                                    with dpg.group():
                                        dpg.add_text('cust_id')
                                        self.cust_id = dpg.add_input_text(tag='Cust-id', width=90)
                                dpg.add_spacer()
                                def clear():
                                    dpg.set_value(self.first_name, '')
                                    dpg.set_value(self.last_name, '')
                                    dpg.delete_item(self.customer_table, children_only=True)

                                dpg.add_button(label='Clear', width=286, callback=clear)


                            with dpg.item_handler_registry() as search_names:
                                dpg.add_item_edited_handler(callback=self.search_like_input)

                            dpg.bind_item_handler_registry(self.first_name, search_names)
                            dpg.bind_item_handler_registry(self.last_name, search_names)
                            dpg.bind_item_handler_registry(self.cust_id, search_names)




                            # middle side                                                    
                            with dpg.child_window(width=330, height=450):
                                dpg.add_text('Customer Report:')
                                dpg.add_separator()
                                with dpg.group() as self.report_group:
                                    pass
                            
                            # leftmost side
                            with dpg.child_window(width=815, height=450):
                                with dpg.plot(label='Customer 2018 Transaction History', width=800, anti_aliased=True) as self.single_customer_transaction_volume_plot:
                                    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                    y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Amount per Month (USD)')
                                
                                    dpg.set_axis_limits(x_axis, 1, 12)
                                    dpg.set_axis_limits(y_axis, 0, 2000)
                                    dpg.set_axis_ticks(x_axis, [[str(num), num] for num in range(1, 13)])
                                    dpg.add_line_series(parent=dpg.last_item(), x=[], y=[])
                                
                                # print(self.single_customer_transaction_volume_plot)
                                # print(x_axis, y_axis, series)
                                # print(dpg.get_item_children(self.single_customer_transaction_volume_plot))
                                # print(dpg.get_item_info(series)['parent'])
                                # print(dpg.get_item_children(y_axis))
                                    

                                                                                                                                                                                            

                    with dpg.group(horizontal=True):
                        dpg.add_text('Results')
                        radio = dpg.add_radio_button(("Edit Mode", "Report Mode"), callback=self.edit_or_report_mode, horizontal=True)                        

                        with dpg.item_handler_registry() as switched_modes:
                            dpg.add_item_clicked_handler(callback=self.refresh_search_like_input)
                        
                        dpg.bind_item_handler_registry(radio, switched_modes)


                    with dpg.child_window(border=False) as customer_table_window:
                        with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                    resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                    borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.customer_table:
                                    pass  
                        

                with dpg.theme() as customer_table_theme:
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15, category=dpg.mvThemeCat_Core)
                        dpg.add_theme_color(dpg.mvThemeCol_Button, value=(40, 255, 175, 232), category=dpg.mvThemeCat_Core)
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, value=(104, 255, 199, 232), category=dpg.mvThemeCat_Core)
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, value=(193, 255, 232, 232), category=dpg.mvThemeCat_Core)
                        dpg.add_theme_color(dpg.mvThemeCol_Text, value=(0, 0, 0, 255))
                
                dpg.bind_item_theme(customer_table_window, theme=customer_table_theme)
                        
                        
                        