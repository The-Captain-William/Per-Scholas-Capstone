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

        self.transaction_types = ["type-1", "type-2"]

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

        self.months = ['jan', 'feb', 'mar', 'apr', 'april', 'may','jun', 'jul', 'aug', 'sep', 'nov', 'dec']

        self.query_one = f"{self.user_values['transaction-month']} {self.user_values['zip'] } {self.user_values['year']}"

        self.query_two = f"{self.user_values['transaction-type']}"
        
        self.query_three = f"{self.user_values['transaction-state']}"




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
        print("Adjust table size with --t")
        print("See values with --val")
        print("Show Table with --show")
        print("\n")
    

    def transaction_by_state_and_branch_menu(self):  # submenu 3
        print("display the number and total values of transactions for branches in a given state.")
        print("Change Branch with --branch")
        print("Change Transaction type with --tran")
        print("Adjust table size with --t")
        print("See values with --val")
        print("Show Table with --show")


    def input_transaction_type(self, tran):  # --tran
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
                    
        if tran.lower().strip() in self.transaction_types:
            print(f"Selected Transaction Type: {tran.strip().title()}")
        else:
            if tran.lower().strip() != "q":
                print("Not a valid Transaction Type")


    def input_transaction_branch(self, tran):  # --tran
        #transaction_type = input("Please enter a Valid Transaction Type:\n> ")
                    
        if tran.lower().strip() != "q":
            print(f"Selected Branch: {tran.strip().title()}")
            self.user_values['transaction-branch'] = tran


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
            self.user_values['transaction-month'] = month.lower().strip()
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



