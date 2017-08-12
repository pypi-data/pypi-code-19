#累了累了
def print_lol(the_list):
#没错，就是这样
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)

