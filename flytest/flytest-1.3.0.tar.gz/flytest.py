"""这是一个“flytest.py”模块"""
def print_lol(the_list,indent=False,level=0):
    """函数说明"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
		    if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
            
