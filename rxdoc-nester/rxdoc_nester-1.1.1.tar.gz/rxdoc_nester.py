'''Simple recursive function that takes a list (which may or may not 
    contain one or more levels of nested lists) as an argument and will 
    print each individual element of all levels of a nested list'''
    
def print_lol(the_list, level = 0):
	'''will check to see if an item is a list and if so process
		each item in that list so that the end result is a line by line
		printout of all items of all nested levels of the parent list'''	
		
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item,level + 1)
		else:
			for tab_stop in range(level):
				print('\t', end = '')
			print(each_item)
