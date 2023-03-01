import mysql.connector as mariaDb
from pyspark.sql import SparkSession, types
from super_secret_password import PASSWORD
from time import sleep


from capstone_classes import TransactionMenu, CustomerMenu, BootOptions
from capstone_functions import *

transaction_menu = TransactionMenu()
customer_menu = CustomerMenu()
boot_menu = BootOptions()

#============================================================================== TODO'S START
# TODO
# ===================
# CLI TERMINAL APPLICATION & CLASSES
# ===================

# PLEASE NOTE: 
# This current version is 



# fix this giant mess lol
# ---------------------
# repackage classes 
# you get a decorator, you get a decorator, everyone gets a decorator
# eventually pull out cli interface so I can have my own custom cli library

# research
# ----------
# what are all the benefits of using types in funcs?




# TODO
# ==================================
# UPDATE CUSTOMER WINDOW 
# ==================================

# import mysql connector
# ----------
# update statement (ideally these tables should contain keys for WHERE = '')  ✅
# note - how do we deal with transaction commits if working with pgadmin? 

# craft update statement w.r.t like %SSN ✅
# ----

# present small query to user using apache spark temp table for now ✅
# ---------


# are you sure? y/n prompt ✅
# ---


# try / except 
# ---- 
# note - except : pass for now, but ideally should have custom exceptions ✅

# also it would be much more ideal to have restraints on what is accepted in sql server rather than
# using duck typing or a barrage of elifs for data validation ⭐

# ============================================================================== TODO'S END 



# =============================================================================== SPARK STUFF

# tbh I'm only just now realizing spark is too OP for the kind of manipulation I'm doing here for the front end
# but it was a great exercise nonetheless


spark_active = False

DATABASE_VALUES= {"url": "jdbc:mysql://localhost:3306/creditcard_capstone",
                "table":["CDW_SAPP_BRANCH", "CDW_SAPP_CREDIT_CARD", "CDW_SAPP_CUSTOMER"],
                "mode":"overwrite",
                "properties":{"user":"root", "password":PASSWORD, "driver":"com.mysql.cj.jdbc.Driver"}}

if __name__ =="__main__":
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
        
        sql_credit_customer_df = sql_credit_customer_df.join(sql_branch_df, sql_branch_df.BRANCH_CODE == sql_credit_customer_df.BRANCH_CODE)
        
        sql_credit_customer_df = sql_credit_customer_df.drop('CUST_SSN')
        
        sql_credit_customer_df = sql_credit_customer_df.drop(sql_customer_df.CREDIT_CARD_NO)

        #sql_credit_customer_df.printSchema()
        
        sql_credit_customer_df.createOrReplaceTempView("credit_customer_df")

        spark_active = True
    except:
        print("Error Establishing Connection 🤷🏻‍♂️")

sleep(10)
print("\n" * 100)
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

    else:
        main_menu_loop = True
        pass

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
            print(" ** For options and assistance, type --help ** ")
            print("=" * 20)
            customer_menu.present_options()
            first_time = False



        customer_menu_selection = user_cursor().strip().lower()


        if customer_menu_selection == "--help" and customer_menu_loop == True:
            customer_menu.customer_help_menu()
            first_time = True
            customer_menu_selection = None
            any_key()

# POV, you don't have time for kwargs and are just going wild with the elifs
        
        elif customer_menu_selection == "--name":
            print("Enter customer name as first-last")

            customer_menu.input_customer_name(user_cursor())
            customer_menu_selection = None
            any_key()

        elif customer_menu_selection == "--debug":
            select = """
                SELECT
                    DISTINCT(SSN),
                    FIRST_NAME,
                    LAST_NAME,
                    CREDIT_CARD_NO
                FROM
                    credit_customer_df
                """
            debug_df = spark_sesh.sql(select)
            debug_df.show(customer_menu.user_values['table-size'])
            customer_menu_selection = None
            any_key()

        elif customer_menu_selection == "--details":
            customer_details = customer_menu.customer_details_menu()
            if customer_details != False:
                customer_details_df = spark_sesh.sql(customer_details)
                customer_details_df.show(customer_menu.user_values['table-size'])
            else:
                pass
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

        elif customer_menu_selection == "--mon":
            print("Enter the first three letters of the month")
            customer_menu.input_month(user_cursor())
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
            customer_mod_menu_response = customer_menu.customer_mod_menu()
            if customer_mod_menu_response != False:
                customer_df_mod = sql_customer_df.createOrReplaceTempView('customer_df_mod')  # create temp view
                customer_df_mod_show = spark_sesh.sql(customer_mod_menu_response)  # show temp
                customer_df_mod_show.show(customer_menu.user_values['table-size'])

                con = mariaDb.connect(
                host = "localhost",
                user="root",
                password=PASSWORD,
                database="creditcard_capstone"
                )

                cursor = con.cursor()

            choices = {'--name':['FIRST_NAME', 'LAST_NAME'],
                    '--add':['FULL_STREET_ADDRESS', 'CUST_STATE', 'CUST_ZIP'],
                    '--email':['CUST_EMAIL'],
                    '--phone':['CUST_PHONE'],
                    '--ccn':['CREDIT_CARD_NO']}

            container = {}

            print("=" * 20)
            print('What would you like to modify?')
            print("=" * 20)

            for key, item in choices.items():
                print(f"{key}, {item}")

            selection = input().lower().strip()
            if selection in choices:  # if -- in choices dict
                mod_item = choices[selection]  # list of columns copy = choice[list of columns]


                for item in mod_item:  # for column in list2
                    print(item)
                    print(f"Enter Value for {item}, leave blank to skip")  # ! be mindful of data integrity 
                    
                    value = input().strip()  #value for column # NOTE I gotta' clean up these variables
                    

                    if value !=" " or "":
                        container[item] = value    # column : new value
            
                # checks not really worth doing until I get everything packaged into descrete units, w/ wrappers and cleaner Classes
                # container at the end of this point is filled
                
                # initialize mysql connection


            # create user selection 
            user_selection = query_concat(container, customer_menu.user_values['customer-SSN'])

            option = None
            while option == None:
                print("=" * 20)
                print(f",\n".join(f"{keyitem}: {container[keyitem]}" for keyitem in container.keys()))
                print("=" * 20)
                print("OK? y/n")

                option = user_cursor()

                if option.lower().split() == 'y' or 'n':
                    if option == 'y':
                        try:
                            cursor.execute(user_selection)
                            con.commit()
                        except:
                            print("Make sure you're using correct values")
                    else:
                        pass
                else:
                    option = None
                

                customer_menu_selection = None
                any_key()

        elif customer_menu_selection == "--bill":
            check = customer_menu.customer_bill_generator()
            if check == True:
                bill_df = spark_sesh.sql(customer_menu.customer_bill_query())
                bill_df.show(customer_menu.user_values['table-size'])
            customer_menu_selection = None
            any_key()

        elif customer_menu_selection == "--betwixt":
            status = customer_menu.call_betwix()
            if status == True:
                gib_da_table = spark_sesh.sql(customer_menu.betwix_query())
                gib_da_table.show(customer_menu.user_values['table-size'])
                any_key()
            customer_menu_selection = None

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
        


        #except:
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

                    if transaction_menu.user_values['zip'] != "None" and \
                    transaction_menu.user_values['year'] != "None" and \
                    transaction_menu.user_values['transaction-month'] != "None":
                        
                        t_1_df = spark_sesh.sql(transaction_menu.query_one_return())

                        t_1_df.show(transaction_menu.user_values['table-size'])
                    else:
                        print("""
                        WARNING - INVALID INPUT VALUES:
                        Displaying General Table Instead:
                        """)
                        t_1_df_debug = spark_sesh.sql(transaction_menu.query_one_return_default())
                        t_1_df_debug.show(transaction_menu.user_values['table-size'])
                    any_key()


                elif user_input == "--anyzip":
                    t_1_df_zip = spark_sesh.sql(transaction_menu.query_one_return_all_zip())
                    t_1_df_zip.show(transaction_menu.user_values['table-size'])
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

                if user_input == "--transhow":                        
                    show_trans_df = spark_sesh.sql(transaction_menu.query_two_return_all_trans_type())
                    transaction_menu.query_two_return_all_trans_type()
                    show_trans_df.show(7)
                    any_key()
                
                elif user_input == "--t":
                    print("Enter a Valid Number")
                    transaction_menu.table_size(user_cursor())
                    any_key()

                elif user_input == "--val":
                    transaction_menu.present_stored_user_inputs()
                    any_key()
                
                elif user_input == "--show":
                    try:
                        transaction_df = spark_sesh.sql(transaction_menu.query_two_return())
                    #spark_sesh.sql(transaction_menu.query_two_return())
                        transaction_df.show(transaction_menu.user_values['table-size'])
                        any_key()
                    except:
                        print("Error, check your values")

                    
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


                elif user_input == "--state":
                    transaction_menu.input_transaction_branch(user_cursor())
                    any_key()

                elif user_input == "--show":
                    if transaction_menu.user_values['transaction-state'] !="None":
                        
                        try:
                            transaction_3_df = spark_sesh.sql(transaction_menu.query_three_return_num_trans_per_state())
                            transaction_3_df.show(transaction_menu.user_values['table-size'])
                            any_key()
                        except:
                             pass

                    print("Error, check your state input")

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
            transaction_menu_selection = None
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