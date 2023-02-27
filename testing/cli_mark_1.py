from pyspark.sql import SparkSession
from super_secret_password import PASSWORD

from capstone_classes import TransactionMenu, CustomerMenu, BootOptions
from capstone_functions import *

transaction_menu = TransactionMenu()
customer_menu = CustomerMenu()
boot_menu = BootOptions()




# =============================================================================== SPARK STUFF

spark_active = False

DATABASE_VALUES= {"url": "jdbc:mysql://localhost:3306/creditcard_capstone",
                "table":["CDW_SAPP_BRANCH", "CDW_SAPP_CREDIT_CARD", "CDW_SAPP_CUSTOMER"],
                "mode":"overwrite",
                "properties":{"user":"root", "password":PASSWORD, "driver":"com.mysql.cj.jdbc.Driver"}}


try:
    print("Loading Spark...")
    spark_sesh = SparkSession.builder.appName('CLI Spark Session').getOrCreate()
    
    print("Making Dataframes...")
    sql_branch_df = spark_sesh.read.jdbc(
    url=DATABASE_VALUES["url"],
    properties=DATABASE_VALUES["properties"],
    table=DATABASE_VALUES["table"][0]
    )

    sql_credit_df = spark_sesh.read.jdbc(
        url=DATABASE_VALUES["url"],
        properties=DATABASE_VALUES["properties"],
        table=DATABASE_VALUES["table"][1]
    )

    sql_customer_df = spark_sesh.read.jdbc(
    url=DATABASE_VALUES["url"],
    properties=DATABASE_VALUES["properties"],
    table=DATABASE_VALUES["table"][2]
    )

    print("Manipulating Tables...")
    sql_credit_customer_df = sql_customer_df.\
        join(sql_credit_df, sql_customer_df.SSN == sql_credit_df.CUST_SSN)
    
    sql_credit_customer_df = sql_credit_customer_df.drop('CUST_SSN')
    
    sql_credit_customer_df = sql_credit_customer_df.drop(sql_customer_df.CREDIT_CARD_NO)

    sql_credit_customer_df.printSchema()
    
    spark_active = True
except:
    print("Error Establishing Connection 🤷🏻‍♂️")


# =============================================================================== 

welcome_screen()  # WELCOME
boot_menu_loop = False
transaction_menu_loop = False
customer_menu_loop = False
main_menu_loop = True

# =============================================================================== MAIN MENU LOOP START
while main_menu_loop == True:
    main_menu()  # PRESENT MAIN MENU

    main_menu_selection = input("> ")  # ASK FOR CHOICE FROM MAIN MENU

    if main_menu_selection.strip() == "1": # USER ENTERS TRANSACTION MENU
        transaction_menu_loop = True
        main_menu_loop = False
        customer_menu_loop = False

    elif main_menu_selection.strip() == "2":
        customer_menu_loop = True
        main_menu_loop = False
        transaction_menu_loop = False

    elif main_menu_selection.strip() == "3":
        main_menu_loop = False
        transaction_menu_loop = False
        customer_menu_loop = False
        boot_menu_loop = True

    elif main_menu_selection.strip() == "q": # USER QUITS PROGRAM
        main_menu_loop = False
        transaction_menu_loop = False
        customer_menu_loop = False
        print("Goodbye!")
        exit()
# =============================================================================== MAIN MENU LOOP END


# =============================================================================== BOOT MENU LOOP START
    boot_menu_selection = None
    first_boot = True
    while boot_menu_loop == True and boot_menu_selection == None:
        if first_boot == True:
            boot_menu.boot_menu_options()
            first_boot = False

        boot_menu_selection = user_cursor()

        try:
            boot_menu_selection = boot_menu_selection.lower().strip()

            if boot_menu_selection == "--help":
                boot_menu.boot_menu_options()
            
                
            # elif boot_menu_selection == "--startspark":
            #     if spark_active != True:  # if not on
            #         print("test")
            #         spark_active = True
  

            elif boot_menu_selection == "--stopspark":
                if spark_active != False:  # if on
                    print("Terminating Spark..")
                    spark_sesh.stop()
                else:
                    pass

            elif boot_menu_selection == "q":
                boot_menu_loop = False
                main_menu_loop = True


        except:
            print("Invalid Operation, type --help for help")
            boot_menu_selection = None





# =============================================================================== CUSTOMER MENU LOOP START
    customer_menu_selection = None
    first_time = True
    while customer_menu_loop == True and customer_menu_selection == None:
        if first_time == True:
            print("=" * 20)
            print("Type --help for help")
            print("=" * 20)
            first_time = False
        customer_menu.present_options()



        customer_menu_selection = user_cursor().strip().lower()

        try:  # doing this just incase I get an exception thrown

            if customer_menu_selection == "--help" and customer_menu_loop == True:
                customer_menu.customer_details_menu()
                customer_menu_selection = None
                any_key()

# POV, you don't have time for kwargs and are just going wild with the elifs
            
            elif customer_menu_selection == "--name":
                print("Enter customer name as first-last")

                customer_menu.input_customer_name(user_cursor())
                customer_menu_selection = None
                any_key()

            
            elif customer_menu_selection == "--ssn":
                print("Enter Customer SSN (last four digits)")
                customer_menu.input_customer_SSN(user_cursor())
                customer_menu_selection = None
                any_key()


            elif customer_menu_selection == "--date":
                print("Enter date range as from-to\n(YYYYMMDD-YYYYMMDD)")
                customer_menu.input_betwix_date(user_cursor())
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--t":
                print("Enter a number for the number of rows to show for a table")
                customer_menu.table_size(user_cursor())
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--val":
                customer_menu.present_stored_user_inputs()
                customer_menu_selection = None
                any_key()
            
            elif customer_menu_selection == "--show": # ⭐
                customer_menu.table_show()
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--mod":
                customer_menu.customer_mod_menu()
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--bill":
                customer_menu.customer_bill_generator()
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--betwixt":
                customer_menu.call_betwix()
                customer_menu_selection = None
                any_key()

            elif customer_menu_selection == "--ccn":
                print("Enter a Credit Card Number: (16 nums)")

                customer_menu.input_customer_CCN(user_cursor())
                customer_menu_selection = None
                any_key()
        


                

            elif customer_menu_selection == "q": #--------------- OUTSIDE QUIT
                customer_menu_loops = False
                main_menu_loop = True

            else:
                print("Invalid, press --help for help.")
                customer_menu_selection = None
        


        except:
            print("Invalid, press --help for help.")
            customer_menu_selection = None
        







# =============================================================================== TRANSACTION MENU LOOP START
    transaction_menu_selection = None

    while transaction_menu_loop == True and transaction_menu_selection == None:

        transaction_menu.present_options()  # PRESENT TRANSACTION SUB-MENU


        transaction_menu_selection = input("> ") # PROMPT FOR WHICH SUB MENU
# ===============================================================================


        if transaction_menu_selection.strip() == "1" and transaction_menu_loop == True:  # TRANSACTION SUBMENU 1  # 1 and Trans-True; T1
            transtion_submenu_one = True

            while transtion_submenu_one == True: # ------------------------- loop T1 submenu

                transaction_menu.month_year_zip_menu()
                
                user_input = input("> ")
                user_input = user_input.lower().strip()

                if user_input == "--zip":
                    print("Enter a Valid Zip")
                    zip = transaction_menu.collect_response(user_cursor())
                    transaction_menu.input_zip(zip)
                    any_key()
                
                elif user_input == "--mon":
                    print("Enter a Valid Month (First three letters)")
                    month = transaction_menu.collect_response(user_cursor())
                    transaction_menu.input_month(month)
                    any_key()
                
                elif user_input == "--t":
                    print("Enter a Valid Number")
                    number = transaction_menu.collect_response(user_cursor())
                    transaction_menu.table_size(number)
                    any_key()

                elif user_input == "--val":
                    transaction_menu.present_stored_user_inputs()
                    any_key()

                elif user_input == "--show":
                    transaction_menu.query_one
                    any_key()

                elif user_input == "q":
                    transaction_menu_selection = None
                    transtion_submenu_one = False

                #transaction_menu_one = False







        elif transaction_menu_selection.strip() == "2" and transaction_menu_loop == True: # TRANSACTION SUBMENU 2
            transtion_submenu_two = True

            while transtion_submenu_two == True:
                transaction_menu.transaction_by_type_menu()

                user_input = user_cursor()

                if user_input == "--tran":
                    transaction_menu.input_transaction_type(user_cursor())
                    any_key()
                
                elif user_input == "--t":
                    print("Enter a Valid Number")
                    transaction_menu.table_size(user_cursor())
                    any_key()

                elif user_input == "--val":
                    transaction_menu.present_stored_user_inputs()
                    any_key()
                
                elif user_input == "--show":
                    spark_sesh.sql(transaction_menu.query_two)
                    any_key()
                
                elif user_input == "q":
                    transaction_menu_selection = None
                    transtion_submenu_two = False
        




        elif transaction_menu_selection.strip() == "3" and transaction_menu_loop == True:  # TRANSACTION SUBMENU 3
            transaction_submenu_three = True

            while transaction_submenu_three == True:
                transaction_menu.transaction_by_state_and_branch_menu()

                user_input = user_cursor()

            
                if user_input == "--tran":
                    transaction_menu.input_transaction_type(user_cursor())
                    any_key()
                
                elif user_input == "--t":
                    print("Enter a Valid Number")
                    transaction_menu.table_size(user_cursor())
                    any_key()

                elif user_input == "--val":
                    transaction_menu.present_stored_user_inputs()
                    any_key()


                elif user_input == "--branch":
                    transaction_menu.input_transaction_branch(user_cursor())
                    any_key()

                elif user_input == "--show":
                    transaction_menu.query_three
                    any_key()
                
                elif user_input == "q":
                    transaction_menu_selection = None
                    transaction_submenu_three = False

        


# ===============================================================================
        elif transaction_menu_selection.strip() == "q": 
            transaction_menu_loop = False
            main_menu_loop = True
# =============================================================================== TRANSACTION MENU LOOP END


# ===============================================================================
        else: # LOOP TRANSACTION MENU
            pass
# ===============================================================================

# main true
# cust false
# t false
# main true
    #  t
        # if t then main false && cust false

        # t1 1 && t.1
        # t2 2 && t.2
        # t3 3 && t.3
    
    # cust
        # if cust then main false && t false

        # c1
        # c3
        # c4
# 