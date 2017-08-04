
# exer P29
"""
 My moudle to exercise Python Head First
"""
def print_lol(the_list):
	'''
	to print the nested list elments.
	'''
	for items in the_list:
		if isinstance(items,list):
			print_lol(items)
		else:
			print(items)
