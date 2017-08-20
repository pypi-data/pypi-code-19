#这是“nester.py”模块，提供了一个名为print_lol()的函数，这个函数的作用是打印列表，其中可能包含（也可能不包含）嵌套列表。
def print_lol( item, indent = False, level = 0, address = sys.stdout ):
	#这个函数选取一个位置参数，名为“item”，这可以使任何python列表（也可以是包含嵌套列表的列表）。所指定的列表中 的每一个数据项会（递归地）输出到屏幕上，各数据各占一行。
	for each_item in item:
		if isinstance( each_item, list ):
			print_lol( each_item, indent, level + 1, address )
		else:
			if indent:
				for i in range( level ):
					print( '\t', end = '', file = address )
			print( each_item, file = address )