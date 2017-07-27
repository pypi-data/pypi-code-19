'''这是nester.py模块，提供了一个名称print_lol的函数，
这个函数的作用是打印列表，其中有可能有包含（也可能不包含）嵌套列表。'''
def print_lol(the_list):
        '''这个函数取一个位置参数，名为the_list，这可以是任何python列表（也可以包含嵌套列表的列表）。
        所指定的列表中每个数据项会（递归地）输出到屏幕上，各数据项各占一行。'''
        for item in the_list:
                if isinstance(item, list):
                        print_lol(item)
                else:
                        print(item)
