names=["marry","john",["tom","jack",["1",2,3]]]
#numbers=[i for i in range(5)]
duochong=[["a","b",['c','d'],'e',['g','gs',['ok','pop']]],'f']
"""这是nester.py模块，提供了一个名为print_lol()的函数，这个函数的作用打印列表，
其中有可能包含嵌套列表"""
def print_lol(the_list,indent=False,level=0):
    """这个函数取一个参数“the_list”，可以是任何python列表，包括嵌套列表，所指定的列表中所有
数据项会递归的打印到屏幕上，各数据项占一行.第二个参数"level"用来在遇到嵌套列表时插入制表符"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
