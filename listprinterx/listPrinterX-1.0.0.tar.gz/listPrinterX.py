"""this is my first python module to print list data """
def print_lst(lst):
    print ("start:")
    for item in lst:
        if isinstance(item,list):
            print_lst(item)
        else:
            print (item)
    print ("end:")

# print ("OVER")




