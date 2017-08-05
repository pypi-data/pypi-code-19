
# exer P29
"""
 My moudle to exercise Python Head First
"""
def print_lol(the_list, indent=False, level=0):
	'''
	to print the nested list elments.
	'''
	for items in the_list:
		if isinstance(items,list):
			print_lol(items, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
			print(items)
