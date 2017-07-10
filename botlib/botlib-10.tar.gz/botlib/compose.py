# botlib/compose.py
#
#

import logging
import sys

def compose(o, self=None):
    from .object import Object
    if not o:
        return o
    t = type(o)
    if t in [None, bool, True, False, int, float]:
        return o
    if t in [str,]:
        ot = from_string(o)
        try:
            return ot()
        except:
            return o
    if t in [list, tuple]:
        l = []
        for item in o:
            l.append(compose(item))
        return l
    try:
        ts = o["_type"]
        t = from_string(ts)
    except KeyError:
        t = Object
    if not t:
        return t
    oo = t()
    for k, v in o.items():
        if k == "_type":
           continue
        oo[k] = compose(v)
    return oo

def from_string(s):
    from .space import kernel
    bs = s
    if s.startswith("<class"):
        s = s.split()[-1][1:-2]
    elif s.startswith("<function"):
        funcname = s.split()[1]
        try:
            return globals()[funcname]
        except:
            return None
    elif s.startswith("<module"):
        s = s.split()[1]
    elif "object" in s:
        s = s.split()[0][1:].strip()
    try:
        m, c = s.rsplit(".", 1)
    except:
        try:
            m = s.split(".")[-1]
            c = ""
        except:
            return None
    if not m:
        return None
    if "botlib.utils" in m:
        mod = m
    else:
        try:
            mod = sys.modules[m]
        except KeyError:
            try:
                mod = kernel.load_mod(m)
            except ImportError:
                return None
    o = getattr(mod, c, None)
    return o