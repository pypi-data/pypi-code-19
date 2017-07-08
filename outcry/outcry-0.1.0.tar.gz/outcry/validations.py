import re
import math
from outcry.exceptions import OutcryValueError


class Validator(object):
    error = "Default validator error message"
    def __init__(self, fn, error):
        self._fn = fn
        self._error = error

    @property
    def error(self):
        return self._error

    def validate(self, value):
        valid = self._fn(value)
        if not valid:
            raise OutcryValueError("{0}, {1}".format(self._error, value)) 
        return True
        

def isStr():
    return Validator(lambda x: type(x) is str, "Value is not a string: ")


def isInt():
    return Validator(lambda x: type(x) is int, "Value is not a int: ")


def isList():
    return Validator(lambda y: type(y) is list, "Value is not a list: ")


def isEmail():
    pattern = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    return Validator(pattern.match, "Email is not valid:")


def isUrl():
    pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    return Validator(pattern.match, "Url is not valid: ")


def isLength(minimum=0, maximum=math.inf):
    return Validator(lambda x: len(x) > minimum and len(x) < maximum)
