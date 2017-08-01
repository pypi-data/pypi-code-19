# -*- coding=utf-8 -*-

import inspect
import sys
from datetime import *


def class_function_name():
    return inspect.stack()[1][3]

def get_func_info():
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    return '%s, %s, %s, %s, ' % (str(datetime.now()), f.f_code.co_filename, f.f_code.co_name, str(f.f_lineno))


def trans(s):
    return "b'%s'" % ''.join('\\x%.2x' % x for x in s)
