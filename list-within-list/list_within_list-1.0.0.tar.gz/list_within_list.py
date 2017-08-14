"""This list_within_list.py module holds a function checkiteminlist
which prints all items in a list which may be or may not be nested
list"""

def checkiteminlist(takesalist):
    """ This function takes input one input 
    "takesalist" which should be a list. The 
     list is iterated through and checked if 
     an item in the list is list, if so the 
     checkiteminlist is called recursively.
     If an item is not a list, the item is 
     printed. The iterated loopo continues 
     until all items in the list is printed"""
	
    for each_item in takesalist:
        if isinstance(each_item,list):
            checkiteminlist(each_item)
        else:
            print (each_item)
