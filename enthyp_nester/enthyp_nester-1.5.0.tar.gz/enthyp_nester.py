""" This is the enthyp_nester module. It provides one function named
    print_lol which prints a list (be it nested or not). """
import sys
def print_lol(the_list, indent_on = False, level = 0, destination = \
              sys.stdout):
    """ This function takes a Python list as an argument and displays
        each data item in it (recursively) on a separate line. By default,
        the output is displayed on the screen, unless destination is specified
        otherwise. If indent_on argument is True the output is indented
        according to the depth of nesting. """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent_on, level + 1, destination)
        else:
            if indent_on:
                print("\t" * level, end = "", file = destination)
            print(item, file = destination)
