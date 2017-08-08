#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""

@version: 0.1
@author:  quantpy
@email:   quantpy@qq.com
@file:    test.py
@time:    2017-08-08 15:11
"""

from __future__ import division, print_function, unicode_literals
import numpy as np
import pandas as pd
from ebokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool


def gen_tools():
    hover = HoverTool(tooltips=[
        ("index", "$index"),
        ("date", "@idx{%F}"),
        ("value", "$y"),
    ],

        formatters={
            "idx": "datetime",
        },

        # mode='vline'
    )

    return [hover, 'pan', 'crosshair', 'box_select', 'lasso_select', 'wheel_zoom', 'reset', 'save']


def test_df():
    tools = 'pan,hover,resize'
    df = pd.DataFrame(np.random.randn(100, 5), index=pd.date_range('20140101', periods=100),
                      columns=list('ABCDE')).cumsum()
    color = {'A': 'firebrick', 'B': 'blue', 'C': 'navy', 'D': 'green', 'E': 'black'}
    width, height = 500, 300

    p1 = figure(title='Test DataFrame for line', width=width, height=height, x_axis_type='datetime', tools=tools)
    p1.line(df, color=color)

    p2 = figure(title='Test DataFrame for circle', width=width, height=height, x_axis_type='datetime',
                x_range=p1.x_range, tools=tools)
    p2.circle(df, color=color)

    p3 = figure(title='Test DataFrame for circle', width=width, height=height, x_axis_type='datetime',
                x_range=p1.x_range, tools=tools)
    p3.diamond(df, color=color)

    p4 = figure(title='Test DataFrame for circle', width=width, height=height, x_axis_type='datetime',
                x_range=p1.x_range, tools=tools)
    p4.vbar(df, width=0.5, color=color)

    return [[p1, p2], [p3, p4]]


def test_src():
    df = pd.DataFrame(np.random.randn(100, 5), index=pd.date_range('20140101', periods=100),
                      columns=list('ABCDE')).cumsum()
    data = {k: df[k].values for k in df.columns}
    data["idx"] = df.index
    source = ColumnDataSource(data=data)
    legend = {k: k.lower() for k in df}  # required
    color = {"A": 'firebrick', 'B': 'blue', 'C': 'navy', 'D': 'green', 'E': 'black'}
    width, height = 500, 300

    p1 = figure(title='Test Source for line', width=width, height=height, x_axis_type='datetime', tools=gen_tools())
    p1.line("idx", 'A,B,C', color=color, source=source, legend=legend)

    p2 = figure(title='Test Source for circle', width=width, height=height, x_axis_type='datetime', x_range=p1.x_range,
                tools=gen_tools())
    p2.circle("idx", 'A,C,E', color=color, legend=legend, source=source)

    p3 = figure(title='Test Source for diamond', width=width, height=height, x_axis_type='datetime', x_range=p1.x_range,
                tools=gen_tools())
    p3.diamond("idx", 'A,C,B', color=color, legend=legend, source=source)

    p4 = figure(title='Test Source for vbar', width=width, height=height, x_axis_type='datetime', x_range=p1.x_range,
                tools=gen_tools())
    p4.vbar("idx", 'A,B,D', width=0.5, color=color, legend=legend, source=source)

    return [[p1, p2], [p3, p4]]


def main():
    output_file('./test_df_grid.html')
    grid_lst = test_df()
    p = gridplot(grid_lst)
    show(p)

    output_file('./test_src_grid.html')
    grid_lst = test_src()
    p = gridplot(grid_lst)
    show(p)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(repr(err))
