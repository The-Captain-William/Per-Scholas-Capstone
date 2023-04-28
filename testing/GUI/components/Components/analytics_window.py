import dearpygui.dearpygui as dpg
from typing import Optional, Union
from types import FunctionType
import numpy as np
from Components.generic_container import GenericContainerContext, ConnectionHandler, DBError
from sorting_functions import capture_min_max

class SaapPortal(GenericContainerContext):

    def __init__(self, container_tag: str, *args, **kwargs):
        super().__init__(container_tag, *args, **kwargs)
        
        #### WHICH BUTTON OF EACH WINDOW IS CURRENTLY SELECTED ####
        self.zipcode_list_selection = None 
        self.currently_selected_state = None
        self.type_list_selection = None
        self.zip_list_selection = None
        self.zipcode_state_list_selection = None
        self.reporting = "Edit Mode"

        self.edit_customer_button_array = {}
        # sender:row_index

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

        self.months_eng = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        


    def __setup(self, connection: ConnectionHandler):
        return super().setup(connection)
    


    def setup(self, connection: ConnectionHandler):
        self.__setup(connection=connection)
        setup_dict = {
            self.zip_filter_set:'SELECT DISTINCT(cust_zip) FROM cdw_sapp_customer;',
            self.state_filter_set:'SELECT DISTINCT(branch_state) FROM cdw_sapp_branch ORDER BY 1;'
        }



        for key, value in setup_dict.items():
            connection.cur_execute(self.tag, value, headers=False, database='db_capstone')
            data = self._collect_items(connection[self.tag][value])
            self._create_dropdown_filter(collection=data,parent_window=key)
        #self.create_transaction_piechart()

        #self.create_transaction_piechart()

        self.set_company_linegraph(2018)
        self.month_day_transaction_bucket(2018)

    def get_company_transaction_volume_year(self, year):
        query = f"""
            SELECT *, 
                CONCAT( '$', FORMAT(`Total Transaction per Month`, 2)) AS `Formatted Values`
            FROM (
            SELECT 
                ROUND(SUM(transaction_value), 2) AS `Total Transaction per Month`,
                MONTH(timeid) AS `Month`
            FROM cdw_sapp_credit_card
            WHERE YEAR(timeid) = '{year}'
            GROUP BY `Month`) t                                        
        """
        # sum, month, formatted(sum)
        
        self.connection.cur_execute(self.tag, query, database='db_capstone')
        data = self.connection[self.tag][query][1:]
        
        total_value = [value[0] for value in data]
        month = [value[1] for value in data]
        formatted_value = [value[2] for value in data]

        return total_value, month, formatted_value



    def set_company_linegraph(self, year):
        dpg.delete_item(self.company_plot, children_only=True)
        dpg.configure_item(self.company_plot, label='Total Transaction Volume Per Month')


        total_value, month, formatted_value = self.get_company_transaction_volume_year(year)
        x_ticks_monthly = [[self.months_eng[index][:3], month[index]] for index in range(0, 12)]
        
        ymin = min(total_value) * 0.99
        ymax = max(total_value) * 1.099

        x_axis_company = dpg.add_plot_axis(dpg.mvXAxis, label='Month', parent=self.company_plot)
        y_axis_company = dpg.add_plot_axis(dpg.mvYAxis, label='Total Transaction Volume per Month', parent=self.company_plot)
        
        dpg.add_line_series(parent=y_axis_company, x=month, y=total_value)
        dpg.set_axis_ticks(x_axis_company, x_ticks_monthly)
        dpg.set_axis_limits(x_axis_company, 1, 12)
        dpg.set_axis_limits(y_axis_company, ymin, ymax)
        
        

    def month_day_transaction_bucket(self, year):
        """
        Returns sql query with:
        Month Number (1, 2, 3 etc)
        Total transaction value Per Day
        Day of the month (number)
        Total transaction value Per Month
        date (MM-DD) represented as a float (ie 1.01, 1.02 represents January First, January Second) 
        """
        query = f"""
                SELECT
                -- month, total, day, trans/month, month/day
                    *, 
                    TRUNCATE(`Month` + (`Day`/100), 2) AS `Month / Day`
                FROM (
                SELECT
                    ROUND(SUM(transaction_value), 2) AS `Total`, 
                    MONTH(timeid) AS `Month`,
                    DAY(timeid) AS `Day`
                FROM saap_customer_report
                WHERE timeid BETWEEN '{year}-01-01' AND '{year}-12-30'
                GROUP BY `Month`, `Day` ) m
                JOIN (
                SELECT 
                    ROUND(SUM(transaction_value), 2) `Monthly Transaction Value`,
                    MONTH(timeid) AS `Month`
                FROM saap_customer_report
                WHERE timeid BETWEEN '{year}-01-01' AND '{year}-12-30'
                GROUP BY `Month`
                ) t 
                USING(`Month`)
        """

        self.connection.cur_execute(self.tag, query, database='db_capstone')
        # grab value

        value_per_day = [value[1] for value in self.connection[self.tag][query][1:]]
        type = [value[1] for value in self.connection[self.tag][query][1:]]
        time = [value[4] for value in self.connection[self.tag][query][1:]]
        ticks = [[f"{str(tick).replace('.', '/')}", tick] for tick in time]

        month = [value[1] for value in self.connection[self.tag][query][1:]]


        midpoint_date = [(114 + num)/100 for num in range(0, 1200, 100)]
        x_ticks_monthly = [[self.months_eng[midpoint_date.index(value)][:3], value] for value in midpoint_date]

        opens = [value_per_day[index] for index in range(0, (28 * 12) , 28)]  # 0 b/c list starts at zero, don't forget
        closes = [value_per_day[index] for index in range(27, (28 * 12) , 28)]  # 27 b/c starting from zeroth index
        low, high = capture_min_max(value_per_day, 28, 12)

        
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, parent=self.candle_company_plot, label='Month')
        dpg.set_axis_limits(dpg.last_item(), 0.5, 13)
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, parent=self.candle_company_plot, label='Daily Volume')
        #dpg.set_axis_limits(dpg.last_item(), min(low) * 0.99, max(high) * 1.099)
        dpg.add_candle_series(parent=y_axis,
                    dates=midpoint_date,
                    opens=opens,
                    closes=closes,
                    lows=low,
                    highs=high)
        #dpg.fit_axis_data(y_axis)
        dpg.set_axis_ticks(x_axis, x_ticks_monthly)



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
        
        dpg.configure_item(self.plot_zip_linechart,
                           x=self.state_vs_total_transactions_x,
                           y=zipcode_transaction_value)
        
        print(zipcode_transaction_value)
        dpg.set_axis_limits(self.plot_y_axis_zip_timeseries,
                            min(zipcode_transaction_value) * 0.99,
                            max(zipcode_transaction_value) * 1.099)


        self._window_query_results(self.connection[self.tag][query], parent=self.query_transaction_value_per_type_given_zip)

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


    # def create_transaction_piechart(self):
    #     self.transaction_types_pie_series_data = []
    #     self.transaction_types_pie_series_strings = []

    #     transaction_types_sum = """
    #     SELECT 
	# 	transaction_type AS `Transaction Type`,
	# 	FORMAT(sum(transaction_value), 2) AS `Formatted Values`,
	# 	ROUND(sum(transaction_value), 2) AS `Rounded Series Values`
		
    #     FROM cdw_sapp_credit_card
    #     GROUP BY 1
    #     """

    #     self.connection.cur_execute(self.tag, transaction_types_sum, database="db_capstone")

    #     self.transaction_types_pie_series_strings = [value[0] for value in self.connection[self.tag][transaction_types_sum][1:]]
    #     self.transaction_types_pie_series_data = [value[2] for value in self.connection[self.tag][transaction_types_sum][1:]]

    #     print(self.transaction_types_pie_series_strings)
    #     print("")
    #     print(self.transaction_types_pie_series_data)
    #     dpg.configure_item(self.transaction_types_piechart, values=self.transaction_types_pie_series_data, labels=self.transaction_types_pie_series_strings)
        
    #     self._window_query_results(self.connection[self.tag][transaction_types_sum], self.query_transactions_per_type)


    def window(self):


    # main window

        with dpg.window(label='Business Analytics'):
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
                                with dpg.tab(label='Company-Wide Breakdown'):
                                    dpg.add_text('Display the number and total values of transactions for a given type.')
                                    dpg.add_separator()





                                                                                    
                                    with dpg.group(): 
                                        with dpg.plot(height=400, width=1490) as self.company_plot:
                                            pass
                                        

                                    

                                            

                                    with dpg.group():
                                        with dpg.group(horizontal=True):

                                            with dpg.plot(height=400, width=400) as self.candle_company_plot_granular:
                                                pass

                                            with dpg.plot(height=400, width=1090) as self.candle_company_plot:
                                                pass
                                            dpg.add_button(label='Daily Transaction Volume for Month')
                                            with dpg.popup(parent=dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                                                dpg.add_listbox(items=[month for month in self.months_eng])

                                                
                                                                                                


                                    with dpg.child_window(border=False):
                                        dpg.add_spacer(height=15)
                                        with dpg.group(horizontal=True):
                                            dpg.add_text('View Transaction History')
                                            
                                            dpg.add_text('Year:')
                                            with dpg.group():                                                          
                                                dpg.add_listbox(items=[2018], num_items=1, width=200) 
                                            with dpg.tooltip(dpg.last_item()):
                                                dpg.add_text('This dataset contains data from 2018 only')    

                                            

                                    
                                    # with dpg.group(horizontal=True):  # second group (buttons)
                                        
                                    #     with dpg.group(horizontal=True):
                                            
                                    #         dpg.add_text('Between')
                                            
                                    #         self.__start_date = dpg.add_button(label='start', width=100)
                                    #         with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                                    #             dpg.add_listbox(width=90, num_items=3, items=['test' for _ in range(10)], callback=lambda s, a, u:dpg.configure_item(self.__start_date, label=a))
                                            
                                    #         dpg.add_text('and')
                                            
                                    #         self.__stop_date = dpg.add_button(label='stop', width=100)
                                    #         with dpg.popup(dpg.last_item(), mousebutton=dpg.mvMouseButton_Left):
                                                
                                    #             dpg.add_listbox(width=90, num_items=3, items=['test' for _ in range(10)], callback=lambda s, a, u: dpg.configure_item(self.__stop_date, label=a))
                                        
                                    #     def clear_dates():
                                    #         for _ in range(2):
                                    #             dpg.configure_item(self.__start_date, label='start')
                                    #             dpg.configure_item(self.__stop_date, label='end')
                                        
                                    #     with dpg.group():    
                                    #         dpg.add_button(label='Search', width=160)
                                    #         dpg.add_button(label='Clear', width=160, callback=clear_dates)
                                    



                                
                                    #     # Transaction 2 Plot
                                    #     with dpg.plot(width=480, height=450, no_mouse_pos=True):
                                    #         dpg.add_plot_legend()
                                            
                                    #         # x axis
                                    #         self.transaction_types_x_axis = dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True)
                                            
                                            
                                    #         # axis limits
                                    #         #dpg.set_axis_limits(self.transaction_types_x_axis, 0, 1)
                                    #         #dpg.set_axis_limits()
                                            
                                    #         # plot, pie chart ⭐
                                    #         with dpg.plot_axis(dpg.mvYAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True) as self.transaction_types_y_axis:
                                    #             self.transaction_types_piechart = dpg.add_pie_series(0.5, 0.5, 0.5, 
                                    #                                                                  self.transaction_types_pie_series_data, 
                                    #                                                                  self.transaction_types_pie_series_strings,
                                    #                                                                  format='%0.2f')


                                    #     with dpg.group():
                                    #         dpg.add_text('Transaction Types:')
                                    #         dpg.add_input_text(width=200, callback=lambda s, a:dpg.set_value(self.tansaction_filter_sets, a))  # decided to make everything a filter, its cleaner
                                    #         with dpg.tooltip(dpg.last_item()):
                                    #             dpg.add_text('Filter list')
                                    #         with dpg.child_window(width=200, height=160) as self.transaction_types:
                                    #             with dpg.filter_set() as self.tansaction_filter_sets:
                                    #                 pass
                                            

                                    # dpg.add_button(label=f'Show Data', width= 200, callback=lambda: dpg.configure_item(self.transaction_popout_window, show=True, pos=dpg.get_mouse_pos()))
                                    # with dpg.window(label='Transaction Type Data for 2018', show=False, height=214, width=419) as self.transaction_popout_window:
                                    #     with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                    #                 resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                    #                 borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transactions_per_type:
                                    #                 pass     

                                # Transactions 3: Transactions for branches by state
                                with dpg.tab(label='Transactions by State'):
                                    with dpg.group(horizontal=True):
                                        with dpg.group():  # company, state, region time series
                                            
                                            # company
                                            with dpg.plot(label='Company Transaction Volume for Year', anti_aliased=True) as self.plot_state_vs_company_transactions:
                                                # x axis
                                                self.plot_x_axis_company = dpg.add_plot_axis(dpg.mvXAxis, label='Month')

                                                # plot, line, x and y series dataset

                                                # state vs company, y axis and plot
                                                self.plot_y_axis_company = dpg.add_plot_axis(dpg.mvYAxis, label='Total Transaction Value')

                                                # limits
                                                dpg.set_axis_limits(self.plot_x_axis_company, 1, 12)
                                                dpg.set_axis_limits(self.plot_y_axis_company, 0, 1000)

                                                # ticks
                                                self.x_ticks = [[f"{str(num)}", num] for num in range(1, 13)]
                                                dpg.set_axis_ticks(self.plot_x_axis_company, self.x_ticks)
                                                
                                                self.plot_company_linechart = dpg.add_line_series(self.state_vs_total_transactions_x,
                                                                                                        self.total_transactions_year,
                                                                                                        parent=self.plot_y_axis_company
                                                )
                                                    

                                            # state
                                            with dpg.plot(label='State Transaction Volume for Year', anti_aliased=True) as self.plot_state_vs_company_transactions_2:
                                                self.plot_x_axis_state = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                                

                                                self.plot_y_axis_state = dpg.add_plot_axis(dpg.mvYAxis, label='Total Transaction Value')

                                                self.plot_state_linechart = dpg.add_line_series(self.state_vs_total_transactions_x,
                                                                                                self.state_transactions_year,
                                                                                                parent=self.plot_y_axis_state

                                                )
                                                
                                                dpg.set_axis_limits(self.plot_x_axis_state, 1, 12)
                                                dpg.set_axis_ticks(self.plot_x_axis_state, self.x_ticks)
                                            
                                            # zip/region
                                            with dpg.plot(label='Zip Transaction Volume for Year', anti_aliased=True) as self.plot_zip_timeseries:
                                                self.plot_x_axis_zip_timeseries = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                                

                                                self.plot_y_axis_zip_timeseries = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Value')

                                                self.plot_zip_linechart = dpg.add_line_series(x=self.state_vs_total_transactions_x,
                                                                                                y=[],
                                                                                                parent=self.plot_y_axis_zip_timeseries)
                                                # NOTE: refactor
                                                                                                                                                                                                                                
                                                dpg.set_axis_limits(self.plot_x_axis_zip_timeseries, 1, 12)
                                                dpg.set_axis_ticks(self.plot_x_axis_zip_timeseries, self.x_ticks)

                                            

                                        with dpg.group(): # state report, state pie chart, region count/vol
                                            # state report 
                                            with dpg.child_window(width=400, height=300, border=False):
                                                dpg.add_text("State Report")
                                                dpg.add_separator()
                                                self.report_text = dpg.add_text(wrap=400)

                                            # state transaction type pie chart
                                            with dpg.plot(label='State Transaction Volume by Type', no_mouse_pos=True, anti_aliased=True, equal_aspects=True) as self.piechart_transaction_value_per_type_given_state:
                                                dpg.add_plot_legend()
            
                                                # x axis
                                                self.piechart_state_x_axis = dpg.add_plot_axis(dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True)

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
                                                with dpg.plot(label='Transaction Count and Volume', anti_aliased=True) as self.plot_state_vs_company_transactions_2:
                                                    
                                                    dpg.add_plot_legend()


                                                    self.plot_x_axis_zip = dpg.add_plot_axis(dpg.mvXAxis, label='Month')
                                                    
                                                    self.plot_y_axis_zip = dpg.add_plot_axis(dpg.mvYAxis, label='Transaction Value')

                                                    dpg.set_axis_limits(self.plot_x_axis_zip, 1, 24)
                                                    #dpg.set_axis_ticks(self.plot_x_axis_zip, self.x_ticks)
                                            

                                            



                                        with dpg.group():  # region report, state contribution, region contribtion
                                            with dpg.child_window(width=400, height=300, border=False):
                                                dpg.add_text("Region Report")
                                                dpg.add_separator()
                                                self.region_report_text = dpg.add_text(wrap=200)
                                            
                                            
                                            with dpg.group() as self.piechart_report_group:
                                                with dpg.plot(label='State Transactions as a Percent of Total Transactions', no_mouse_pos=True, anti_aliased=True, equal_aspects=True):
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

                                        with dpg.group():  # state dropdown, region dropdown

                                            with dpg.child_window(indent=40, border=False):
                                        
                                                with dpg.group():
                                                    with dpg.group():
                                                        dpg.add_spacer()
                                                        dpg.add_text('Transactions by State:')
                                                        dpg.add_input_text(width=200, callback=lambda s, a:dpg.set_value(self.state_filter_set, a))
                                                        with dpg.tooltip(dpg.last_item()):
                                                            dpg.add_text('Filter list')
                                                        with dpg.child_window(width=200, height=160) as self.transaction_types:
                                                            with dpg.filter_set() as self.state_filter_set:
                                                                pass
                                        
                                                    dpg.add_button(label='Show State Data', width=200, callback=lambda: dpg.configure_item(self.state_popout_window, show=True, pos=dpg.get_mouse_pos()))                                    

                                                with dpg.group():
                                                    dpg.add_spacer()
                                                    dpg.add_text('Zip codes:')
                                                    dpg.add_input_text(width=200, callback=lambda s, a: dpg.set_value(self.zip_state_filter_set, a))
                                                    with dpg.tooltip(dpg.last_item()):
                                                        dpg.add_text('Filter list')
                                                    # will populate with zip codes
                                                    with dpg.group():
                                                        with dpg.child_window(width=200, height=160) as self.zipcodes_by_state:
                                                            with dpg.filter_set() as self.zip_state_filter_set:
                                                                pass
                                                        dpg.add_button(label='Show Region Data', width=200, callback=lambda: dpg.configure_item(self.state_zip_popout_window, show=True, pos=dpg.get_mouse_pos()))
                                                    
                                                with dpg.group():  # custom calendar b/c I don't need dates as granular as days for this data                                                            
                                                    dpg.add_spacer()
                                                    dpg.add_text('Year:')
                                                    date_data = dpg.add_listbox(items=[2018], num_items=2, width=200)                                                                                
                                                    with dpg.tooltip(date_data):
                                                        dpg.add_text('This dataset contains data from 2018 only')



                                
                                

                                
                                # SQL TABLES

                                    # Region
                                    with dpg.window(label='Transactions by Region Breakdown', show=False, width=566, height=329) as self.state_zip_popout_window:
                                        with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                    resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                    borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transaction_value_per_type_given_zip:
                                                    pass  
                                        
                                    # # tbd
                                    # with dpg.window(label='Transactions by State Breakdown', show=False, width=475, height=214) as self.state_popout_window:
                                    #     with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                    #                 resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                    #                 borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transaction_value_per_type_given_state:
                                    #                 pass          


                                    # State
                                    with dpg.window(label='Transactions by State Breakdown', show=False, width=475, height=214) as self.state_popout_window:
                                        with dpg.table(header_row=True, policy=dpg.mvTable_SizingFixedFit, row_background=True, reorderable=True,
                                                    resizable=True, no_host_extendX=True, hideable=True, borders_innerV=True, delay_search=True,
                                                    borders_outerV=True, borders_innerH=True, borders_outerH=True) as self.query_transaction_value_per_type_given_state:
                                                    pass  
