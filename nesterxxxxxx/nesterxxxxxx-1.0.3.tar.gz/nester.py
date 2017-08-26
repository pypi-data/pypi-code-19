"""this is comment"""
def print_lol(the_list,indent=False,level=0):
	for item in the_list:
		if isinstance(item,indent,list):
			
			print_lol(item,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print('\t',end='')
			print(item)