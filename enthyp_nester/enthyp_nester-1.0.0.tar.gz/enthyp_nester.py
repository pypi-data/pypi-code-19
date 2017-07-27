""" This is the enthyp_nester module. It provides one function named
    print_lol which prints a list (be it nested or not). """
def print_lol(the_list):
    """ This function takes a Python list as an argument and displays
        each data item in it (recursively) on a separate line """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)
