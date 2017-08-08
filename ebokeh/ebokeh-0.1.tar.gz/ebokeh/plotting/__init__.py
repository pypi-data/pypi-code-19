#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@email:   quantpy@qq.com
@file:    __init__.py.py
@time:    2017-08-07 17:51
"""


from __future__ import division, print_function, unicode_literals
from bokeh.plotting import *
from .figure import glyph_wrapper

__glyphs__ = ['asterisk', 'circle', 'circle_cross', 'circle_x', 'cross', 'diamond', 'diamond_cross', 'hbar', 'vbar',
              'ellipse',
              'oval', 'patch',
              'line',
              # 'quard',
              'ray', 'rect', 'square', 'square_cross', 'square_x', 'triangle',
              # 'wedge',
              'x',
              'scatter']


class _Figure(Figure): pass


class Figure(_Figure):

    __subtype__ = 'Figure_'
    __view_model__ = 'Plot'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


for g in __glyphs__:
    setattr(Figure, g, glyph_wrapper(g)(getattr(Figure, g)))


del g


def figure(**kwargs):
    return Figure(**kwargs)
