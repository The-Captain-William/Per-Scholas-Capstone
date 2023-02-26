


from capstone_classes import TransactionMenu
from capstone_functions import *

transaction_menu = TransactionMenu()

welcome_screen()  # WELCOME
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

    elif main_menu_selection.strip() == "q": # USER QUITS PROGRAM
        main_menu_loop = False
        transaction_menu_loop = False
        customer_menu_loop = False
        print("Goodbye!")
        exit()
# =============================================================================== MAIN MENU LOOP END




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
                    transaction_menu.query_two
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

