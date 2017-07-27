""" This is the enthyp_nester module. It provides one function named
    print_lol which prints a list (be it nested or not). """
def print_lol(the_list, indent_on = False, level = 0):
    """ This function takes a Python list as an argument and displays
        each data item in it (recursively) on a separate line. If indent_on
        argument is True the output is indented according to the depth of
        nesting. """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent_on, level + 1)
        else:
            if indent_on:
                for i in range(level):
                    print("\t", end = "")
            print(item)
