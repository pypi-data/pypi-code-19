"""这是一个打印嵌套列表的函数，可以

把列表做为参数传递进去，然后挨项打印

出来。"""

def print_lol(the_list,level):
    """the_list是要打印项目的列表,numoftab是打印的空格数"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
