'''递归函数，显示嵌套列表'''
import sys
def zk_list(the_list,indent=False,level=0,fn=sys.stdout ):
    for per in the_list:
        if isinstance(per,list):
            zk_list(per,indent,level+1,fn)
        else:
            if indent:
                    for tab in range(level):
                        print("\t",end='',file=fn)
            print(per,file=fn)
