def main_menu():
    print("1. Transaction Details Module")
    print("2. Customer Details Module")
    print("3. Boot Options")

def any_key(placeholder='Continue'):
    print(f"Press Any Key to {placeholder}")
    input("")

def welcome_screen():
    print("=" * 20)
    print("Welcome! Enter a number to select a menu.\nEnter 'q' to leave current menu or exit the program.")
    print("=" * 20)
    print("\n")

def user_cursor():
    return input("> ")

