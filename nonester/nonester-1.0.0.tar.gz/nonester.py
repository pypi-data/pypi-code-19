"""this module is targeted at printing nested lists using recursion"""
def print_lol(the_list):
    """the_list is a list,
which may or may not contain nested lists"""
    for every_item in the_list:
        if isinstance(every_item,list):
            print_lol(every_item)
        else:
            print(every_item)
            
