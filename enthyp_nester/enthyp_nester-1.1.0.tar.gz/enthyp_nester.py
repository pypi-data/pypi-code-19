""" This is the enthyp_nester module. It provides one function named
    print_lol which prints a list (be it nested or not). """
def print_lol(the_list, level):
    """ This function takes a Python list as an argument and displays
        each data item in it (recursively) on a separate line. It also
        takes an integer argument (level), which indicates depth of nesting
        and is used to increase indentation with growing depth. """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, level + 1)
        else:
            for i in range(level):
                print("\t", end = "")
            print(item)
