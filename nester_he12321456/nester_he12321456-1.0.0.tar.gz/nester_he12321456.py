#!/usr/bin/python3

#嵌套查询列表中的数据项

#自定义的函数名称为ll
def ll(lists):
      #代码组
	for each_item in lists:
		if isinstance(each_item,list):
			ll(each_item)
		else:
			print(each_item)
