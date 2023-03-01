class TransactionMenu:
    def __init__(self):
        self.title = "TRANSACTION MENU"

        self.user_values = {
        "zip":'None',
        "transaction-month":'None',
        "year":'2018',
        "transaction-type":"None",
        "transaction-state":"None",
        "transaction-branch":"None",
        "table-size":10
        }

        self.transaction_types = ["Bills", 
                                  "Education",
                                  "Entertainment",
                                  "Gas",
                                  "Grocery",
                                  "Healthcare",
                                  "Test"]

        self.transaction_states = [
                        "AL",
                        "AK",
                        "AZ",
                        "AR",
                        "CA",
                        "CO",
                        "CT",
                        "DE",
                        "FL",
                        "GA",
                        "HI",
                        "ID",
                        "IL",
                        "IN",
                        "IA",
                        "KS",
                        "KY",
                        "LA",
                        "ME",
                        "MD",
                        "MA",
                        "MI",
                        "MN",
                        "MS",
                        "MO",
                        "MT",
                        "NE",
                        "NV",
                        "NH",
                        "NJ",
                        "NM",
                        "NY",
                        "NC",
                        "ND",
                        "OH",
                        "OK",
                        "OR",
                        "PA",
                        "RI",
                        "SC",
                        "SD",
                        "TN",
                        "TX",
                        "UT",
                        "VT",
                        "VA",
                        "WA",
                        "WV",
                        "WI",
                        "WY"
                    ]

        self.months = ['jan', 'feb', 'mar', 'apr', 'april', 'may','jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        self.query_two = f"{self.user_values['transaction-type']}"
        
        self.query_three = f"{self.user_values['transaction-state']}"
        
    



    def query_one_return(self):
        return f"""
        SELECT 
            CUST_ZIP,
            FIRST_NAME,
            LAST_NAME,
            CREDIT_CARD_NO,
            TRANSACTION_ID, 
            TRANSACTION_TYPE, 
            TRANSACTION_VALUE, 
            TIMEID AS DATE,
            DATE_FORMAT(TIMEID, 'MMMM') AS MONTH
        FROM credit_customer_df
        WHERE 
            CUST_ZIP = {self.user_values["zip"]}
            AND 
            YEAR(TIMEID) = {self.user_values["year"]}
            AND 
            DATE_FORMAT(TIMEID, 'MMMM') LIKE("{self.user_values['transaction-month']}%")
        ORDER BY DAYOFMONTH(TIMEID)  DESC;"""

    def query_two_return(self):  # transaction types
        return f"""
        SELECT
            COUNT(TRANSACTION_TYPE) AS TOTAL_{self.user_values['transaction-type'].upper()}_TRANSACTIONS, ROUND(SUM(TRANSACTION_VALUE), 2) AS SUM
        FROM 
            credit_customer_df
        WHERE 
            TRANSACTION_TYPE = '{self.user_values['transaction-type']}'
        """

    def query_one_return_default(self):
        return f"""
        SELECT 
            CUST_ZIP,
            FIRST_NAME,
            LAST_NAME,
            CREDIT_CARD_NO,
            TRANSACTION_ID, 
            TRANSACTION_TYPE, 
            TRANSACTION_VALUE, 
            TIMEID AS DATE
        FROM credit_customer_df
        ORDER BY DAYOFMONTH(TIMEID)  DESC;
        """

    def query_one_return_all_zip(self):
        return f"""
        SELECT 
            DISTINCT(CUST_ZIP) AS CUSTOMER_ZIP_TABLE
        FROM
            credit_customer_df
        order by CUSTOMER_ZIP_TABLE;
            """
    def query_two_return_all_trans_type(self):
        return f"""
        SELECT 
            DISTINCT(TRANSACTION_TYPE) 
        FROM
            credit_customer_df
        order by TRANSACTION_TYPE;
            """

    def query_three_return_num_trans_per_state(self):
            return f"""
            SELECT
                TRANSACTION_TYPE,   
                COUNT(*) AS NUMBER_OF_TRANSACTIONS_IN_{self.user_values['transaction-state']}, 
                ROUND(SUM(TRANSACTION_VALUE), 2) AS SUM_OF_TRANSACTIONS_IN_{self.user_values['transaction-state']}              
            FROM 
                credit_customer_df
            WHERE 
                BRANCH_STATE = '{self.user_values['transaction-state']}'
            GROUP BY BRANCH_STATE, TRANSACTION_TYPE
            ORDER BY BRANCH_STATE ASC"""

    #print("1. Adjust Options for Transaction Query")

    def present_options(self):
        print("1. Display Transactions by Month, Year, and Zip")
        print("2. Display Number and Total Values of Transactions for a Given Type")
        print("3. Display Number and Total Values of Transactions for Branches in a Given State")
    
    def collect_response(self, response):  # if response then
        print(f"You Have Selected: {response}")
        return response

    def month_year_zip_menu(self):  # submenu 1
        print("\n")
        print("=" * 40)
        print("Display the Transactions Made by Customers in a given Zipcode, by Month and Year")
        print("PLEASE NOTE: Only 2018 currently accepted")
        print("=" * 40)
        print("\n")

        print("Options:")
        print("-" * 20)
        print("See zips  with --anyzip")
        print("Adjust zip with '--zip'")
        print("Adjust month with '--mon")
        print("Adjust table size with --t")
        print("See values with --val")
        print("Show Table with --show")
        print("\n")

    def transaction_by_type_menu(self):  # subemnu 2
        print("\n")
        print("=" * 40)
        print("display the number and total values of transactions for a given type.")
        print("=" * 40)
        print("\n")

        print("Options:")
        print("-" * 20)
        print("Change Transaction type with --tran")
        print("Show all Transaction types with --transhow")
        print("Adjust table size with --t")
        print("See values with --val")
        print("Show Table with --show")

        print("\n")
    

    def transaction_by_state_and_branch_menu(self):  # submenu 3
        print("=" * 20)
        print("display the number and total values of transactions for branches in a given state.".title())
        print("=" * 20)
        print("Change Branch with --state")
        #print("Change Transaction type with --tran")
        print("Adjust table size with --t")
        print("See values with --val")
        print("Show Table with --show")


    def input_transaction_type(self, tran: str):  # --tran
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
                    
        if tran.title().strip() in self.transaction_types:
            print(f"Selected Transaction Type: {tran.strip().title()}")
            self.user_values['transaction-type'] = tran.title().strip()
        else:
            if tran.lower().strip() != "q":
                print("Not a valid Transaction Type")


    def input_transaction_branch(self, tran: str):  # --tran
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
                    
        if tran.lower().strip() != "q":
            print(f"Selected State: {tran.strip().upper()}")
            self.user_values['transaction-state'] = tran.upper()


    def input_zip(self, zip):  # put other failsafes externally
        try:
            int(zip)
            if len(zip) <= 5:
                print("")
                print("=" * 20)
                print(f"Zip: {zip} Accepted")
                print("=" * 20)
            self.user_values['zip'] = zip
            return True
        except:
            print("Invalid Zip")
        return False


    def input_month(self, month):
        #month = input("Please Enter first three letters of month name:\n> ")
        if month.lower().strip() in self.months:
            print("")
            print("=" * 20)
            print(f"Month: {month.title()} Accepted")
            print("=" * 20)
            self.user_values['transaction-month'] = month.title()
            return True
        return False


    def present_stored_user_inputs(self):  # --val
        print("")
        print("=" * 20)
        print("Current Values:")
        print("=" * 20)
        print(",\n".join(f"{key[0]}: {key[1]}" for key in self.user_values.items()))
    

    def table_size(self, number):
        try:
            if int(number) > 0:
                number = int(number)
                print("")
                print("=" * 20)
                print(f"{number} Accepted")
                print("=" * 20)
                self.user_values["table-size"] = number
                return True
        except:
            print("Not a Valid Number")
            return False

    def table_show(self):
        print("=" * 20)
        print("Showing Table")
        print("=" * 20)
        input("")

class CustomerMenu(TransactionMenu):
    def __init__(self):  # w.r.t self, look into self
        super().__init__()  # w.r.t interitance, look into architype
        self.title = "CUSTOMER MENU"
        self.query_one = f"details"
        self.query_two = f"mod"
        self.query_three = f"bills"
        self.query_four = f"betwix"
        self.user_values = {
        "zip":'None',
        "transaction-month":'None',
        "year":'2018',
        "transaction-type":"None",
        "transaction-state":"None",
        "table-size":10,
        "customer-first":"None",
        "customer-last":"None",
        "customer-CCN":"None",
        "date-start":"None",
        "date-end":"None",
        "customer-SSN":"None"
        }
    
    def present_options(self):
        print("=" * 20)
        print("In this window you can:")
        print("- Check the existing account details of a customer".title()) # cust 1
        print("- Modify the existing accout details of a customer".title()) # ⭐
        print("- generate a monthly bill for a credit card number for a given month and year".title()) # cust 3
        print("- display the transactions made by a customer between two dates".title()) # cust 4
        print("=" * 20)
        print("\n")
        #. Order by year, month, and day in descending order

    def customer_help_menu(self): # cust submenu 1
        # print("\n")
        # print("=" * 40)
        # print("Check or Modify the account details of a customer, Given:\n-First Name\n-Last Name,\n-Last 4 of SSN")
        # print("=" * 40)
        # print("\n")
        print("\n")
        print("#" * 40)
        print("Options:")
        print("\n")

        print("=" * 20)
        print("Entering Values:")
        print("=" * 20)
        print("\n")

        print("Customer Details")
        print("-" * 20)

        print("Enter Customer name with --name")
        print("Enter Customer SSN (Last 4 Digits) with --ssn")
        print("Enter a Credit Card Number with --ccn")
        print("\n")

        print("Date Ranges:")
        print("-" * 20)
        print("Set a Date-Range with --date")  # TODO make decorator
        print("\n")

        print("Values and Table Size: ")
        print("-" * 20)
        print("Adjust table size with --t")
        print("See values with --val")
        print("\n")

        print("=" * 20)
        print("Actions:")
        print("=" * 20)
        print("\n")

        print("Making Queries:")
        print("-" * 20)
        print("View all Transactions between dates for a given credit-card number with --betwixt")  # will open up func w options
        print("Generate a Customer bill with --bill")  # will open up func w options
        print("Search for a customer details with --details")
        print("\n")

        print("Modifying Customer Data")
        print("-" * 20)
        print("Modify Customer details with --mod")
        print("\n")

        print("#" * 40)

    def customer_details_menu(self): # specific customer, could also make CVS style return query w/ fir, las 
        if self.user_values['customer-first'] != None and \
        self.user_values['customer-last'] != None:
            return f"""
            SELECT
                FIRST_NAME,
                LAST_NAME,
                FULL_STREET_ADDRESS,
                CUST_STATE,
                CUST_ZIP,
                CREDIT_CARD_NO,
                CUST_EMAIL,
                CUST_PHONE
            FROM 
                credit_customer_df
            WHERE 
                FIRST_NAME = '{self.user_values['customer-first']}'
            AND
                LAST_NAME =  '{self.user_values['customer-last']}'
            GROUP BY FIRST_NAME, LAST_NAME, FULL_STREET_ADDRESS,
            CUST_STATE, CUST_ZIP, CREDIT_CARD_NO, CUST_EMAIL, CUST_PHONE;
            """
        else:
            print("You need to Enter a valid customer name with --name")
            return False
        # NOTE: While group by is implicit with a bunch of stuff in SQL, 
        # pyspark shits the bed if its not explicitly stated what you want to group by


    def customer_bill_generator(self):
        print(f"""
        =====================
        Current Values:
        First Name: {self.user_values['customer-first']},
        Last Name: {self.user_values['customer-last']},
        SSN: {self.user_values['customer-SSN']},
        Transaction Year: {self.user_values['year']}
        Transaction Month: {self.user_values['transaction-month']}
        =====================
        """)

        if self.user_values['customer-first'] != "None" and \
        self.user_values['customer-last'] != "None" and \
        self.user_values['customer-SSN'] != "None" and \
        self.user_values['transaction-month'] != "None" and \
        self.user_values['year'] !="None":
            return True  # NOTE: all of this can be done a tad bit better with decators I reckon. This is all still proof-of-concept
        else:
            print("Warning: You need satisfy above values before you can create a bill.")
        
    
    def customer_bill_query(self):
        return f"""
        SELECT 
            FIRST_NAME,
            LAST_NAME,
            CREDIT_CARD_NO,
            CONCAT( '$', ROUND(SUM(TRANSACTION_VALUE), 2)) AS TOTAL,
            DATE_FORMAT(TIMEID, 'MMMM') AS FOR_MONTH_OF
        FROM 
            credit_customer_df
        WHERE 
            FIRST_NAME = '{self.user_values['customer-first']}'
        AND
            LAST_NAME =  '{self.user_values['customer-last']}'
        AND 
            SSN LIKE('%{self.user_values['customer-SSN']}') 
        AND 
            DATE_FORMAT(TIMEID, 'MMM') = '{self.user_values['transaction-month']}'
        AND 
            DATE_FORMAT(TIMEID, 'yyyy') = '2018'
        GROUP BY
            FOR_MONTH_OF, FIRST_NAME, LAST_NAME, CREDIT_CARD_NO
        """


    def customer_mod_menu(self):  # ⭐
        print(f"""
        =====================
        Current Values:
        First Name: {self.user_values['customer-first']},
        Last Name: {self.user_values['customer-last']},
        SSN: {self.user_values['customer-SSN']},
        =====================
        """)

        if self.user_values['customer-first'] != "None" and \
        self.user_values['customer-last'] != "None": #and \
        #self.user_values['customer-SSN'] != "None":
            select =   f"""
            SELECT
                FIRST_NAME,
                LAST_NAME,
                FULL_STREET_ADDRESS,
                CUST_STATE,
                CUST_ZIP,
                CREDIT_CARD_NO,
                CUST_EMAIL,
                CUST_PHONE
            FROM 
                customer_df_mod
            WHERE 
                FIRST_NAME = '{self.user_values['customer-first']}'
            AND
                LAST_NAME =  '{self.user_values['customer-last']}'
            -- AND SSN = 'LIKE(%{self.user_values['customer-SSN']})'
            """
            #print(select)
            return select
        else:
            print("Warning: You need satisfy above values before you can Modify an input")
            return False


    def input_customer_name(self, tran):  
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
        
        if tran.lower().strip() != "q":

            print(f"Selected Name: {tran.strip().title()}")
            try:
                name_list = tran.split("-")
                if len(name_list) == 2:
                    name_format = [name.title() for name in name_list]
                    self.user_values['customer-first'] = name_format[0]
                    self.user_values['customer-last'] = name_format[1]
                    return True

                #print(name_format)
            except:
                print("Invalid name")
                return False

        

    def call_betwix(self):
        print(f"""
        =====================
        Current Values:
        First Name: {self.user_values['customer-first']},
        Last Name: {self.user_values['customer-last']},
        Credit-Card Number: {self.user_values['customer-CCN']},
        Start-Date: {self.user_values['date-start']}
        End-Date: {self.user_values['date-end']}
        =====================
        """)       
        
        if self.user_values['customer-first'] != "None" and \
        self.user_values['customer-last'] != "None" and \
        self.user_values['customer-SSN'] != "None":
            return True
        
        else:
            print("Warning: You need satisfy all above values before you can call --betwixt") 
            return False  

    def input_betwix_date(self, date: str):  
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
        
        if date.lower().strip() != "q":

            print(f"Selected Date: {date}\n")
            try:
                if len(date) == 17:
                    date_list = date.split("-")
                    if len(date_list) == 2:
                        if int(date_list[0]) < int(date_list[1]):
                            self.user_values['date-start'] = date_list[0]
                            self.user_values['date-end'] = date_list[1]
                            print("")
                            print("=" * 20)
                            print(f"\tDate\n\tAccepted")
                            print("=" * 20)
            except:
                print("Invalid Date")
    

    def betwix_query(self):
        return f"""
        SELECT
            CREDIT_CARD_NO,
            CUST_CITY,
            FIRST_NAME,
            LAST_NAME,
            MIDDLE_NAME,
            TRANSACTION_ID,
            TRANSACTION_TYPE,
            TRANSACTION_VALUE,
	        TIMEID AS DATE
        FROM 
            credit_customer_df
        WHERE 
            FIRST_NAME = '{self.user_values['customer-first']}'
        AND
            LAST_NAME = '{self.user_values['customer-last']}'
        AND 
            SSN LIKE('%{self.user_values['customer-SSN']}')
        AND 
            DATE(TIMEID) BETWEEN '{self.user_values['date-start'][:4]}-{self.user_values['date-start'][4:6]}-{self.user_values['date-start'][6:]}' 
            AND '{self.user_values['date-end'][:4]}-{self.user_values['date-end'][4:6]}-{self.user_values['date-end'][6:]}'  
        ORDER BY 
            DATE_FORMAT(TIMEID, 'yyyy') DESC, 
            DATE_FORMAT(TIMEID, 'MM') DESC, 
            DATE_FORMAT(TIMEID, 'dd') DESC;
        """
    # pyspark needs values input like this (yyyy, MM, dd) w/ no percent or it shits the bed
    # pyspark also does not work if you enter just digits w/ between, needs  - - - 
    # look at all the work I have to do to get pyspark to play ball! 😠 c'mon pyspark, # dobetter

    # DOCS
    # https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html


    def input_customer_SSN(self, SSN):
        try:
            int(SSN)
            if len(SSN) == 4:
                print("")
                print("=" * 20)
                print(f"Last 4 SNN: {SSN} Accepted ")
                print("=" * 20)
                self.user_values['customer-SSN'] = SSN
                return True
            else:
                print("Invalid SSN")
                return False
        except:
            print("Invalid SSN")
        return False
    
    def input_customer_CCN(self, CCN):
        try:
            int(CCN)
            if len(CCN) == 16:
                print("")
                print("=" * 20)
                print(f"Credit Card Number:\n{CCN}\nAccepted ")
                print("=" * 20)
                self.user_values['customer-CCN'] = CCN
                return True
            else:
                print("Invalid CCN, CCN must be 16 numbers long")
            try:
                print(f"You entered one {len(CCN)} numbers long")
            except:
                pass
            return False
        except:
            print("Invalid CCN")
        return False


class BootOptions():
    def __init__(self) -> None:
        pass
    
    
    def boot_menu_options(self):
        print("""
        ===============
        Boot Menu
        ------------
        Options:
    
         --startspark to connect with pyspark
         --stopspark to stop pyspark connection

         --startsql to connect with mysql.connector (IN DEVELOPMENT)
         --stopsql to close sql connection

         'q' to exit

        ===============
        """)