"""this is comment"""
def print_lol(the_list,level):
	for item in the_list:
		if isinstance(item,list):
		# this is alse a comment
			print_lol(item,level+1)
		else:
			for tab_stop in range:
				print('\t',end='')
			print(item)