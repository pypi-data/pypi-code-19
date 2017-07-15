# coding=utf-8
# 这是一个从列表中提取内容的函数，其中有一个地址参数
def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)

