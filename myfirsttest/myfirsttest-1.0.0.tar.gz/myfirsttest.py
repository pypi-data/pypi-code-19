def func(each_item):
    for each_it in each_item:
        if isinstance(each_it,list):
            func(each_it)
        else:
            print(each_it)
            
