# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" functions concering stack trace. """

import traceback
import sys
import os

stop = ["python3.5",]

def get_exception(txt=""):
    from .space import cfg, exceptions
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for i in trace:
        fname = i[0]
        linenr = i[1]
        func = i[2]
        plugfile = fname[:-3].split(os.sep)
        mod = []
        for i in plugfile[::-1]:
            mod.append(i)  
            if i == "bot": break
        ownname = '.'.join(mod[::-1])
        result += "%s:%s %s | " % (ownname, linenr, func)
    del trace
    res = "%s%s: %s %s" % (result, exctype, excvalue, txt)
    if cfg.test:
        if res not in exceptions:
            exceptions.append(res)
    return res

def get_frame(depth=1, search="code"):
    result = {}
    frame = sys._getframe(depth)
    search = str(search)
    for i in dir(frame):
        if search and search not in i:
            continue
        target = getattr(frame, i)
        for j in dir(target):
            result[j] = getattr(target, j)
    return result

def get_strace(depth=1):
    result = ""
    loopframe = sys._getframe(depth)
    if not loopframe: return result
    while 1:
        try: frame = loopframe.f_back
        except AttributeError: break
        if not frame: break
        linenr = frame.f_lineno
        fn = frame.f_code.co_filename
        func = frame.f_code.co_name
        result += "%s %s:%s | " % (fn, func, linenr)
        loopframe = frame
    del loopframe
    return result[:-3]

def get_from(nr=2):
    """ return the plugin name where given frame occured. """
    frame = sys._getframe(nr)
    if not frame:
        return frame
    if not frame.f_back:
        return frame
    filename = frame.f_back.f_code.co_filename
    linenr = frame.f_back.f_lineno
    plugfile = filename.split(os.sep)
    del frame
    return ".".join(plugfile[-2:]) + ":" + str(linenr)
