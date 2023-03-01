def main_menu():
    print("1. Transaction Details Module")
    print("2. Customer Details Module")
    print("3. Boot Options")

def any_key(placeholder='Continue'):
    print(f"Press Any Key to {placeholder}")
    input("")
    print("\n")

def welcome_screen():
    print("=" * 20)
    print("Welcome! Enter a number to select a menu.\nEnter 'q' to leave current menu or exit the program.")
    print("=" * 20)
    print("\n")

def user_cursor():
    return input("> ")

def query_concat(dictionary : dict, ssn : str):  # hardcode update for now
    ssn = (ssn, )  # I don't need to do this
    #print(type(ssn))
    columns = """
            UPDATE 
                cdw_sapp_customer
            SET 
            """
    conditions = f""" WHERE SSN LIKE('%{ssn[0]}')"""
    concat = ''
    for key in dictionary.keys():
        if dictionary[key].isalnum():  # DANGER ZONE: - I'm assuming we are not working with emails or something else!
            concat += f"{key} = '{dictionary[key]}', "
    concat = concat[:-2]
    print(concat)
    complete_query = columns + concat + conditions
    #print(complete_query)
    return complete_query
