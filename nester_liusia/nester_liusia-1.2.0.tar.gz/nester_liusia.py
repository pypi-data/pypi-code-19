"""这是“nester_liusia.py”模块，
提供了一个名为print_lol()的函数，
这个函数的作用是打印列表，
其中有可能包含嵌套列表。"""
def print_lol(the_list, level=0):
    """这个函数取一个位置参数，名为"the_list"，
       这可以是任何Python列表。
       所指定的列表中的每个数据项会（递归地）输出到屏幕上，
       各数据项各占一行。"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)   
