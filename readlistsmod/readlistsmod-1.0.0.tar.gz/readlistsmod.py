# -*- coding:utf-8 -*-
'''
这是readlistmod.py模块，
它提供了一个read_my_list()的函数，
本函数可以打印列表，并且
可以打印嵌套列表。
'''
def read_my_list(clist):
    '''
    "clist"参数，可以是一个列表，也可以是一个嵌套的列表
    此函数可以在屏幕上打印每个列表的数据项，包括嵌套列表中的数据项。
    并且每个数据项会递归的显示在屏幕上，每个数据项各自占一行。
    '''
    for each_item in clist :
        if isinstance(each_item,list):
            read_my_list(each_item)
        else:
            print(each_item)
