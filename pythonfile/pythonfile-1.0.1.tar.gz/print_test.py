def print_lol(the_list,level):
    for each_print in the_list:
        if isinstance(each_print,list):
            print_lol(each_print,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end="")
            print(each_print)
