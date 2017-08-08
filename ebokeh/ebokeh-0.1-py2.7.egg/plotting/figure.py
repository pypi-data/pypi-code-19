#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@email:   quantpy@qq.com
@file:    figure.py
@time:    2017-08-07 17:57
"""


from __future__ import division, print_function, unicode_literals
from functools import wraps
import pandas as pd


def parser(name, x, y, legend, args1, kwargs):
    kwargs_ = {}
    if name in ['vbar']:
        args_ = [x] + list(args1)
        kwargs_['top'] = y
    elif name in ['hbar']:
        args_ = [x] + list(args1)
        kwargs_['right'] = y
    else:
        args_ = [x, y] + list(args1)

    for k, v in kwargs.items():
        if isinstance(v, dict):
            kwargs_[k] = v.get(legend)
        else:
            kwargs_[k] = v

    if kwargs_.get('legend') is None:
        kwargs_['legend'] = legend

    return args_, kwargs_


def glyph_wrapper(name):
    def wrapper(func):
        @wraps(func)
        def _wrapper(self, *args, **kwargs):
            data = args[0]
            fn = getattr(super(self.__class__, self), name)
            if isinstance(data, (pd.Series, pd.DataFrame)) and kwargs.get('source') is None:
                data = pd.DataFrame(data)
                for col in data:
                    ss = data[col]
                    x, y, legend = ss.index, ss.values, str(ss.name)
                    args_, kwargs_ = parser(name, x, y, legend, args[1:], kwargs)
                    fn(*args_, **kwargs_)
            elif kwargs.get('source') is not None:
                x, y = args[:2]
                x = list(x) if isinstance(x, (list, tuple)) else x.split(',')
                y = list(y) if isinstance(y, (list, tuple)) else y.split(',')
                if len(x) == 1 and len(y) >= 1:
                    x_str = x[0]
                    for y_str in y:
                        args_, kwargs_ = parser(name, x_str, y_str, y_str, args[2:], kwargs)
                        if 'legend' not in kwargs:
                            legend = kwargs_.pop('legend')
                            fn(*args_, legend=legend, **kwargs_)
                        else:
                            fn(*args_, **kwargs_)
                else:
                    y_str = y[0]
                    for x_str in x:
                        args_, kwargs_ = parser(name, x_str, y_str, x_str, args[2:], kwargs)
                        if 'legend' not in kwargs:
                            legend = kwargs_.pop('legend')
                            fn(*args_, legend=legend, **kwargs_)
                        else:
                            fn(*args_, **kwargs_)

            else:
                fn(*args, **kwargs)
        return _wrapper
    return wrapper

