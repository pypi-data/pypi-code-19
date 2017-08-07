#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017-3-17

@author: laok@laok.studio.com
@email:  1306743659@qq.com
@copyright: Apache License,Version 2.0
'''
import sys
from contextlib import contextmanager
#===============================================================================
# 局部化 stdout
#===============================================================================
@contextmanager
def scoped_stdout(filename):
    org = sys.stdout
    try:
        with open(filename , 'w') as f:
            sys.stdout = f
            yield 
    except IOError:
        yield 
    finally:
        sys.stdout = org
