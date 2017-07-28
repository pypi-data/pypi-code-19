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

""" functions used in code to select what objects to use. """

from .error import ENOTSET

def selector(obj, keys):
    """ determine whether obj is part of the query. """
    if not keys:
        return True
    go = False
    for key in keys:
        try:
            attr = getattr(obj, key)
        except (AttributeError, ENOTSET):
            attr = None
        if attr != None:
            go = True
        else:
            go = False
            break
    return go

def wanted(obj, want):
    """ determine if the provided obj is matching criteria. """
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
        if key in obj and value and value in str(obj[key]):
            go = True
        else:
            go = False
            break
    return go

def notwanted(obj, notwant):
    """ determine whether this object in not wanted in a query. """
    if not notwant:
        return False
    for key, value in notwant.items():
        try:
            value = obj[key]
            return True
        except:
            pass
    return False

def ignore(obj, ign):
    """ check if object needs to be ignored. """
    if not ign:
        return False
    for key, values in ign.items():
        value = getattr(obj, key, [])
        for val in values:
            if val in value:
                return True
    return False

got_uniq = []

def uniq(obj, uniqs):
    """ see if this object is uniq. """
    if not uniqs:
        return False
    for key, value in obj.items():
        if key not in got_uniq:
            got_uniq.append(key)
            return True
        else:
            return False
    return True
