from time import sleep

# Transaction Details Module
# 1)    Used to display the transactions made by customers living in a given zip code for a given month and year. Order by day in descending order.
# 2)    Used to display the number and total values of transactions for a given type.
# 3)    Used to display the number and total values of transactions for branches in a given state.



# Customer Details
# 1) Used to check the existing account details of a customer.
# 2) Used to modify the existing account details of a customer.
# 3) Used to generate a monthly bill for a credit card number for a given month and year.
# 4) Used to display the transactions made by a customer between two dates. Order by year, month, and day in descending order.

def main_menu():
    print("1. Transaction Details Module")
    print("2. Customer Details Module")
    print("3. Boot Options")

def trans_menu():
    print("1. Display Transactions by Month, Year, and Zip")
    print("2. Display Number and Total Values of Transactions for a Given Type")
    print("3. Display Number and Total Values of Transactions for Branches in a Given State")

def cust_menu():
    print("cust 1")
    print("cust 2")
    print("cust 3")
    print("cust 4")


# dict 
user_values = {
    "zip":'None',
    "transaction-month":'None',
    "year":'2018',
    "transaction-type":"None",
    "transaction-state":"None",
    "table-size":10
}


# one-off welcome message
print("=" * 20)
print("Welcome! Enter a number to select a menu.\nEnter 'q' to leave current menu or exit the program.")
print("=" * 20)
print("\n")

# loop init
main_menu() # NOTE no args for print 
selection = input("> ")

# MAIN MENU 
while selection != "q":


# Transaction Details Module
# 1)    Used to display the transactions made by customers living in a given zip code for a given month and year. Order by day in descending order.
# 2)    Used to display the number and total values of transactions for a given type.
# 3)    Used to display the number and total values of transactions for branches in a given state.

    if selection == "1": # TRANSACTION MENU 
        print("Transaction Menu")  # one-off
        trans_menu()
        
        selection = input("> ")

        while selection != "q":  # transaction init

            if selection == "1":
            
                print("\n")
                print("=" * 40)
                print("display the transactions made by customers living in a given zip code for a given month and year. Order by day in descending order.")
                print("PLEASE NOTE: Only 2018 currently accepted")
                print("=" * 40)
                print("\n")

                print("Options:")
                print("-" * 20)
                print("Adjust zip with '--zip'")
                print("Adjust month with '--mon")
                print("See values with --val")
                print("Adjust table size with --t")
                print("\n")

                selection = input("> ")

                if selection.lower().strip() == "--zip":
                    zip = input("Please Enter Valid Zip:\n> ")

                    try:
                        int(zip)
                        if len(zip) <= 5:
                            print("")
                            print("=" * 20)
                            print(f"Zip: {zip} Accepted")
                            print("=" * 20)
                        user_values['zip'] = zip

                    except:
                        if zip != "q":
                            print("Invalid Zip")

                        selection = '1' # SET BACK TO 1
                

                elif selection.lower().strip() == "--mon":
                    month = input("Please Enter first three letters of month name:\n> ")
                    months = ['jan', 'feb', 'mar', 'apr', 'april', 'may','jun', 'jul', 'aug', 'sep', 'nov', 'dec']

                    if month.lower().strip() in months:
                        print("")
                        print("=" * 20)
                        print(f"Month: {month.title()} Accepted")
                        print("=" * 20)
                        user_values['transaction-month'] = month.lower().strip()

                    else:
                        if month != "q":
                            print("Invalid Month")
                    

                    selection = '1'
                    
                elif selection.lower().strip() == "--val":
                    print("")
                    print("=" * 20)
                    print("Current Values:")
                    print("=" * 20)
                    print(",\n".join(f"{key[0]}: {key[1]}" for key in user_values.items()))
                    sleep(1)
                    
                    selection = '1'

                elif selection.lower().strip() == "--t":
                    number = input("Please Input a valid number for showing table rows:\n> ")
                    if int(number) > 0:
                        number = int(number)
                        print("")
                        print("=" * 20)
                        print(f"{number} Accepted")
                        print("=" * 20)
                        user_values["table-size"] = number
                    else:
                        if number != "q":
                            print("Invalid Number")

                    selection = "1"



                else:
                    if selection != "q":
                        print("Invalid")

                
            
                    






            elif selection == "2":
                print("display the number and total values of transactions for a given type.")
                selection = input("> ")
                

            elif selection == "3":
                print("display the number and total values of transactions for branches in a given state.")
                selection = input("> ")



            else:
                print("Invalid trans")
                selection = input("> ")


        trans_menu()
        selection = input("> ")
 




    elif selection == "2":
        print("Customer Menu")
        
    elif selection == "3":
        print("Connection Status")

    else:
        print("Invalid menu")

    # keep calling
    main_menu()
    selection = input("> ")





print("goodbye")

# init
# start()

# loop
    # option 1
        # 1.1
        # 1.2
        # 1.3

    # option 2
        # 2.1
        # 2.2
        # 2.3
        # 2.4

    # option 3
        # 3.1 boot


    # start()

# goodbye()
# session.close()