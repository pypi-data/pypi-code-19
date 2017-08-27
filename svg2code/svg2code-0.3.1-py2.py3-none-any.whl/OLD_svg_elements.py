# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import re
from math import sqrt

UNITS_RATIOS = { 
    'px': 1.0, 'pt': 1.25, 'pc': 15.0, 'mm': 3.543307, 'cm': 35.43307, 'in': 90.0 
    }
UNITS_RE = re.compile(r'(?P<num>\d+)\s*(?P<units>\w+)*')

def parseUnits(number, **kwargs):
    m = UNITS_RE.match(number.lower())

    if m is None:
        raise TypeError("'%s' is not a valid number" % number)

    num = float(m.group('num'))
    units = m.group('units') or 'px'

    if units == '%':
        width, height = kwargs.get('width'), kwargs.get('height')

        if width is not None and height is not None:
            return num * (sqrt((width ** 2) + (height ** 2)) / sqrt(2)) / 100.0
        elif width is not None:
            return num * width / 100.0
        elif height is not None:
            return num * height / 100.0
        else:
            raise TypeError("Percentages used without a viewport defined")
    elif units not in UNITS_RATIOS:
        raise TypeError("Unknow units '%s'" % units)

    return UNITS_RATIOS[units] * num

class SVGNode(object):
    def __init__(self, parent=None, **kwargs):
        super(SVGNode, self).__init__()
        self._setAttribute("fill", kwargs.get("fill"), "black", True, parent)


    def _setAttribute(self, name, value, initial, inherited=False, parent=None):
        if value is not None:
            setattr(self, name, value)
        elif inherited and parent is not None and getattr(parent, name) is not None:
            setattr(self, name, getattr(parent, name))
        else:
            setattr(self, name, initial)
