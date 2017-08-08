"""this is my first python module to print list data """
def print_lst(lst,level=0,space=False):
    for item in lst:
        if isinstance(item,list):
            print_lst(item,level+1,space)
        else:
            if space:
                for i in range(level):
                    print ("\t",end='')
            print (item)







