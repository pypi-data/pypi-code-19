"""This is just a exercise, I am a python beginner."""

def print_lol(a_list):
    for each in a_list:
        if isinstance(each,list):
            print_lol(each)
        else:
            print(each)

