"""这是"nestrpy"模块，提供一个名为print_lol()函数，这个函数的作用
是打印列表，其中有可能包含（也可能不包含）嵌套列表"""
def print_lol(the_list,level):
    """这个函数取一个位置参数，名为the_list，这可以是任何Python列表(也可以是包含嵌套列表)。
     所指定的列表中的每个数据项会（递归地）输出到屏幕上，各数据项各占一行。
     第二个参数是level，指定打印的制表符
     movies = ["The Holy Grail","1975","Terry Jones& Terry Gilliam",91,
	        ["Graham Chapman", ["Michael Palin", "John Cleese",
				        "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
    """
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
                    for num in range(level):
                        print("\t",end='')
                    print(each_item)
            








       





