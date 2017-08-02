#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
bar charts using d3 (maybe bokeh again some day)

See:
- http://bokeh.pydata.org/tutorial/solutions/gallery/olympics.html
- http://bokeh.pydata.org/en/latest/tutorial/topical.html
- https://gist.github.com/mbostock/7322386
"""

# TODO: http://bost.ocks.org/mike/bar/3/
# - http://alignedleft.com/tutorials/d3/making-a-bar-chart

# imports
import argparse
import json
import os
import sys
import tempita
from .manipulate import ManipulationParser
from collections import OrderedDict

__all__ = ['bar_chart', 'BarChartParser', 'main']

# template info
# TODO: own module
here = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(here, 'templates')
bar_template = os.path.join(templates, 'bar.d3.html')
with open(os.path.join(here, 'js', 'd3.v3.min.js')) as f:
    d3 = f.read()


def bar_chart(data, labels=None, title=None):
    """
    create a bar chart

    See:
    - http://bokeh.pydata.org/en/latest/tutorial/solutions/gallery/olympics.html
    """
    # TODO:  abstract this to a plot class
    if labels is None:
        labels = data

    template = tempita.Template.from_filename(bar_template)
    bar_chart = template.substitute(title=title or '',
                                    d3=d3,
                                    labels=json.dumps(labels),
                                    data=json.dumps(data))
    return bar_chart

class BarChartParser(ManipulationParser):
    """command line options parser for bar charts"""
    # TODO: upstream to PlotParser

    def __init__(self, **kwargs):
        kwargs.setdefault('description', __doc__)
        ManipulationParser.__init__(self, **kwargs)
        self.add_argument('-t', '--title', dest='title',
                          help="plot title")
        self.add_argument('-u', '--use-numbers', dest='use_numbers',
                          action='store_true', default=False,
                          help="include numbers with the labels")


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = BarChartParser()
    options = parser.parse_args(args)

    # process data
    data = parser.typed_data()

    # ensure a mapping is given
    if len(data) == 1:
        data = data[0]
        labels = None
    elif len(data) == 2:
        if options.use_numbers:
            labels = ['{} : {}'.format(label, value) for label, value in zip(*data)]
        else:
            labels = data[0]
        data = data[1]
    else:
        raise NotImplementedError('TODO')

    # generate bar chart
    options.output.write(bar_chart(data, labels=labels, title=options.title))

    if options.output != sys.stdout:
        # print URL of file
        print ('file://{}'.format(os.path.abspath(options.output.name)))


if __name__ == '__main__':
    main()
