import os
import sys

class Anon:
    def __init__ (self, *dict_args, **dict_kwargs):
        self.__dict__.update(dict(*dict_args, **dict_kwargs))

class UnavailableException (Exception):
    pass

class ContractException (UnavailableException):
    pass

# http://stackoverflow.com/questions/6086976/how-to-get-a-complete-exception-stack-trace-in-python
def format_exc (additional=0, as_list=False):
    import traceback
    exception_list = traceback.format_stack()[:-(2+additional)]
    ertype, ervalue, tb = sys.exc_info()
    exception_list.extend(traceback.format_tb(tb))
    exception_list.extend(traceback.format_exception_only(ertype, ervalue))
    exception_list.insert(0, "Traceback (most recent call last):\n")
    exception_str = "".join(exception_list)
    if as_list:
        return exception_str.split(os.linesep)[:-1]
    else:
        return exception_str
