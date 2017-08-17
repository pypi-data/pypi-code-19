"""This is just a exercise, I am a python beginner."""
import sys
def print_lol(the_list, ident=False, level=0, fh=sys.stdout):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='',file=fh)
            print(each_item,file=fh)
