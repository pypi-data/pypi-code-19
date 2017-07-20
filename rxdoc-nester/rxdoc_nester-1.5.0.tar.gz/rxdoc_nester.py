'''Simple recursive function that takes a list (which may or may not 
    contain one or more levels of nested lists) as an argument and will 
    print each individual element of all levels of a nested list'''

import sys
    
def print_lol(the_list, indent = False, level = 0, save_loc = sys.stdout):
	'''will check to see if an item is a list and if so process
		each item in that list so that the end result is a line by line
		printout of all items of all nested levels of the parent list.
		Indent parameter allows the printed list to show nested levels
		and is set to off by default.  The level of indent can be 
		changed to customize list output use a negative level to ignore
		1 or more levels of nesting in your printout or a positive 
		number to increase all indented levels'''	
		
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level + 1, save_loc)
		else:
			if indent == True:
				for tab_stop in range(level):
					print("\t", end="", file = save_loc)
				print(each_item, file = save_loc)
			else:
				print(each_item, file = save_loc)
				
	save_loc.close()
