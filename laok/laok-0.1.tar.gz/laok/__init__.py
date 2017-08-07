#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017-3-17

@author: laok@laok.studio.com
@email:  1306743659@qq.com
@copyright: Apache License,Version 2.0
'''
from .io_helper import scoped_stdout
from .lktest_interaction import run as lktest_run
from .inspect_helper import detail_description
#===============================================================================
# 用于实现 自动搜索 _lktest()函数,执行交互式测试
#===============================================================================
__all__ = ['detail_description' , 'lktest_run']


def dump_description_help(obj , help_file=True):
    if obj is not None:
        if help_file:
            with scoped_stdout('help-%s.txt' % 
                               (obj.__name__ if hasattr(obj, '__name__') else "none") ):
                help(obj)   
        detail_description(obj)
