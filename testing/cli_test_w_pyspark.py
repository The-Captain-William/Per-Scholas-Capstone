import pyspark.sql
from pyspark.sql import SparkSession
from super_secret_password import PASSWORD

# PYSPARK INITALIZE
session = SparkSession.builder.appName('CLI User Interface').getOrCreate()

# TODO make a password saver or something

DATABASE_VALUES= {"url": "jdbc:mysql://localhost:3306/creditcard_capstone",
                "table":["CDW_SAPP_BRANCH", "CDW_SAPP_CREDIT_CARD", "CDW_SAPP_CUSTOMER"],
                "mode":"overwrite",
                "properties":{"user":"root", "password":PASSWORD, "driver":"com.mysql.cj.jdbc.Driver"}}




# Functional Requirements 2.2
# 1) Used to check the existing account details of a customer.
# 2) Used to modify the existing account details of a customer.
# 3) Used to generate a monthly bill for a credit card number for a given month and year.
# 4) Used to display the transactions made by a customer between two dates. Order by year, month, and day in descending order.

# TODO
# get menu up, menu switchingexi
# bare-bones

# FUNCTIONS

def enumerate_list(list):
    enumerated_list = enumerate(list)
    return_string = "\n".join(f"{choice[0] + 1} - {choice[1]}" for choice in enumerated_list)
    return_string += "\n"
    return return_string


def prompt_check(list_of_choices):  # return t/f

    """
    generic string needs to be "text {var}", 
    where var is equal to a selection of choices
    """
    SELECT_CHOICE_PROMPT = "Please Select a Screen by Selecting the corresponding number, or press q to quit:\n"
    YOU_HAVE_SELECTED = "\nYou Have Selected:\n{selection}\n"

    print(SELECT_CHOICE_PROMPT)
    selection = input("> ")

    if selection.lower().strip() == "q":
        return False  # quit

    try:
        selection = int(selection.lower().strip())
        selection -= 1

        # DEBUGGING 
        #print(selection) 

        if -1 < selection < len(list_of_choices):
            print(YOU_HAVE_SELECTED.format(selection=list_of_choices[selection]))
            return list_of_choices[selection]  # return choices to select
        else:
            pass
    except ValueError:
        pass

    return True  # return true to loop





LOGO = "--logo here--"
WELCOME = "Welcome to -- "

# CONTAINERS FOR SQL QUERIES

transaction_container_query = {"zipcode":"",
                                "type":"",
                                "state":"",
                                "branches":""}






# GENERIC PROMPTS

YOU_HAVE_SELECTED_DOUBLE = "\nYou Have Selected {selection}, is that Correct?\n"
GOODBYE = "Thank you for using, Goodbye!"
NEWLINE = "\n"

# CHOICES LIST

CHOICES_MAIN = ["Transaction Screen", "Customer Screen"]
CHOICES_TRANSACTION = ["display the transactions made by customers living in a given zip code for a given month and year".title(),
                       "display the number and total values of transactions for a given type".title(),
                       "display the number and total values of transactions for branches in a given state".title()]

# ON PROGRAM STARTUP 


# on start
print(LOGO, "\n")
print(WELCOME, "\n")

# initialize and preload selections
main_menu_palatable = enumerate_list(CHOICES_MAIN)  # enumerate list of choices
transaction_menu_palatable = enumerate_list(CHOICES_TRANSACTION)


# START
loop = True

# NOTE:
# I'm taking advantage of the fact that python is dynamically typed, and I can switch 
# from a boolean to a string

while loop:
    main_menu = True
    while main_menu is True: 
        # MAIN MENU

        
        print(main_menu_palatable)  # will print pre-loaded choices
        main_menu = prompt_check(list_of_choices=CHOICES_MAIN)  # will return boolean or string based on list of choices
        
        if main_menu == False:  # in first / last screen, if q on this then program closes
            loop = False

    # TRANSACTION MENU
    if main_menu == CHOICES_MAIN[0]:  # transaction
        transaction_menu = True

        while transaction_menu is True:
            print(transaction_menu_palatable)
            transaction_menu = prompt_check(list_of_choices=CHOICES_TRANSACTION)

            if transaction_menu == CHOICES_TRANSACTION[0]:
                # zipcode, # month, # year
                print("Please enter a zipcode, a month, and a year")
                print("Please note, only 2018 is currently a valid year")

                # TODO 'q' to exit
                    
  
                # TODO data validation

                print("Zipcode:")
                transaction_container_query["zipcode"] = input("> ").strip()
                
                print(NEWLINE)
                
                print("Month (first three letters):")
                transaction_container_query["month"] = input(">")
                print(NEWLINE)

                print("Year:")
                transaction_container_query["year"] = input(">")
                print(NEWLINE)


                # TODO 'are you sure?' check

                sql_transaction_db = session.read.jdbc(
                url=DATABASE_VALUES["url"],
                table=DATABASE_VALUES["table"][1],
                properties=DATABASE_VALUES["properties"])
                # DEBUG
                #print(transaction_container_query)

    









#
# Functional Requirements 2.1
# 1)    Used to display the transactions made by customers living in a given zip code for a given month and year. Order by day in descending order.
# 2)    Used to display the number and total values of transactions for a given type.
# 3)    Used to display the number and total values of transactions for branches in a given state.






print(GOODBYE)
session.stop()



