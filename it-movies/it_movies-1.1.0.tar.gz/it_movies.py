#!/usr/bin/env python3

"""This is the "it_movies.py" module, and it provides one function called print_lol()
which prints lists that may or may not include nested lists."""


movies = ["The Holy Grail", 1975, "The Life of Brian", "The Meaning of Life", 91,
             ["Graham Chapman",
                 ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jonews"]]]




def print_lol(lol,level=0):
    """This function takes a positional argument called "lol", which
    is any Python list (of - possibly - nested lists). Each data item in the
    provided list is (recursively) printed to the screen on it's own line.
    A second argumet called "level" is used to insert tab-stops when a nested is encountered"""
    for item in lol:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(item)

