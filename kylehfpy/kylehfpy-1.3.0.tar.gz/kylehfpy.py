"""This is the "nester.py" module, and it provides one function
called print_lol() which prints lists that may or may not include nested lists."""
def print_lol(the_list, indent=False, level=0, destFile=sys.stdout):
        """This function takes a positional argument called "the_list", which is any
        Python list (of, possibly, nested lists). Each data item in the provided list
        is (recursively) printed to the screen on its own line.
        Second argument "level" is used to insert tab when the list is encountered"""
        for each_item in the_list:
                if isinstance(each_item, list):
                        print_lol(each_item, indent, level+1, destFile)
                else:
                        if indent:
                                for tab in range(level):
                                        print("\t", end='', file=destFile)
                        print(each_item, file=destFile)
