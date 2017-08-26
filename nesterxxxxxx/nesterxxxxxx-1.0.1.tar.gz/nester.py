"""this is comment"""
def print_lol(the_list):
	for item in the_list:
		if isinstance(item,list):
		# this is alse a comment
			print_lol(item)
		else:
			print(item)