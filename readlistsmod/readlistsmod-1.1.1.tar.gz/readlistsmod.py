# -*- coding:utf-8 -*-
'''
这是readlistmod.py模块，
它提供了一个read_my_list()的函数，
本函数可以打印列表，并且
可以打印嵌套列表。
第二个参数用了标注遇到嵌套列表时，插入的tab个数。默认为0.
'''
def read_my_list(clist,level=0):
    '''
    "clist"参数，可以是一个列表，也可以是一个嵌套的列表
    此函数可以在屏幕上打印每个列表的数据项，包括嵌套列表中的数据项。
    并且每个数据项会递归的显示在屏幕上，每个数据项各自占一行。
    '''
    for each_item in clist :
        if isinstance(each_item,list):
            #如遇嵌套列表，则缩进一个TAB,因此level+1
            read_my_list(each_item,level+1)
        else:
            for tab_num in range(level):
                print('\t',end='')
            print(each_item)
