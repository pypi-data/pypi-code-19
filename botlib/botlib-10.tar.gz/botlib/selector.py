# lib/selector.py
#
#

""" functions used in code to select what objects to use. """

from .error import ENOTSET

def selector(object, keys):
    if not keys:
        return True
    go = False
    for key in keys:
        try:
            attr = getattr(object, key)
        except (AttributeError, ENOTSET):
            attr = None
        if attr != None:
            go = True
        else:
            go = False
            break
    return go

def wanted(object, want):
    if not want:
        return True
    if list(want.keys()) == ["start"]:
        return True
    if list(want.keys()) == ["start", "end"]:
        return True
    go = False
    for key, value in want.items():
        if not value:
            continue
        if value.startswith("-"):
            continue
        if key in ["start", "end"]:
            continue
        if key in object and value and value in str(object[key]):
            go = True
        else:
            go = False
            break
    return go

def notwanted(object, notwant):
    if not notwant:
        return False
    for key, value in notwant.items():
        try:
            value = object[key]
            return True
        except:
            pass
    return False

def ignore(object, ignore):
    if not ignore:
        return False
    for key, values in ignore.items():
        value = getattr(object, key, [])
        for val in values:
            if val in value:
                return True
    return False

got_uniq = []

def uniq(obj, uniqs):
    if not uniqs:
        return False
    for key, value in obj.items():
        if key not in got_uniq:
            got_uniq.append(key)
            return True
        else:
            return False
    return True
