"""This list_within_list.py module holds a function checkiteminlist
which prints all items in a list which may be or may not be nested
list"""

def checkiteminlist(takesalist, level=0):
	""" This function takes two inputs 
	"takesalist" which should be a list
	and "level" which should be numeric 
	for indentation for nestes list.if 
	no values is provided, it takes a 
	default value of zero for "level".The 
	list is iterated through and checked if 
	an item in the list is list, if so the 
	checkiteminlist is called recursively.
	If an item is not a list, the item is 
	printed. The iterated loop continues 
	until all items in the list is printed"""
    
	for each_item in takesalist:
		if isinstance(each_item,list):
			checkiteminlist(each_item,level+1)
		else:
			for tab_stop in range(level):
				print ("\t",end="")
			print (each_item)