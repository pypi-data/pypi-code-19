def print_lol(the_list,indent=False,level=0):
    for each_print in the_list:
        if isinstance(each_print,list):
            print_lol(each_print,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_print)
