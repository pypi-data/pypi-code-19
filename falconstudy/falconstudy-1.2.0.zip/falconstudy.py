"""This is just a exercise, I am a python beginner."""

def print_lol(a_list,level=0):
    for each in a_list:
        if isinstance(each,list):
            print_lol(each,level+1)
        else:
            print(each)

