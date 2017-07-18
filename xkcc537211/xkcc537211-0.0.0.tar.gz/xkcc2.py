# coding:utf-8
"""这是"xkcc.py"模块，提供了一个名为print_lol()的函数，用来打印列表，其中包含或不包含嵌套列表。"""
def print_lol(the_list,level):
	""" 这个函数有一个位置参数，名为“the_list”,这可以是任何python列表（包含或不包含嵌套列表），所提供的列表中各个数据项会（递归地）打印到屏幕上，而且各占一行。"""
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each_item)
	
