"""this is my first python module to print list data """
import sys
def print_lst(lst,level=0,space=False,fn=sys.stdout):
    for item in lst:
        if isinstance(item,list):
            print_lst(item,level+1,space,fn)
        else:
            if space:
                for i in range(level):
                    print ("\t",end='',file=fn)
            print (item,file=fn)







