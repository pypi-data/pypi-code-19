#!/usr/bin/env python             
# coding: utf-8
#####使用字典来对全局跨文件的变量进行访问

_global_dict = {}

def set_value(key,value):
    """ 定义一个全局变量 """
    # getValue(key,value)
    _global_dict[key] = value


def get_value(key,defValue=None):
    """ 获得一个全局变量,不存在则返回默认值 """
    try:
        return _global_dict[key]
    except KeyError:
        return defValue

def getValue(key,defValue=None):
    ret = None
    try:
       ret = get_value(key,None)
    except NameError:
        pass
    if not ret:
        ret = get_value(key,defValue)
    pass
    return ret
pass

