# botlib/selector.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

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
