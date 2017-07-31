def print_lol(the_list):
    for each_print in the_list:
        if isinstance(each_print,list):
            print_lol(each_print)

        else:
            print(each_print)
