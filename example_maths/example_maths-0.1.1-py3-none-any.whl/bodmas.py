'''bodmas functions'''

from os import path

from markdown import markdown


class Error(Exception):
    '''base class for exceptions'''
    pass

class ArgumentError(Error):
    '''handle for incorrect function arguments'''
    pass


def add(float_one, float_two):
    '''returns the sum of the arguments provided'''
    try:
        add_sum = float_one + float_two
    except TypeError:
        raise ArgumentError("one or both arguments are non-numeric variables")
    else:
        function_text = open(path.join(path.dirname(__file__), "data/function.txt"), "r").read()
        return markdown(function_text + str(add_sum))
