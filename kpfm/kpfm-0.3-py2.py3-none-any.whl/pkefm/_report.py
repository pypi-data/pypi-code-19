# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function

class HTMLReport(object):
    def __init__(self, dicts, figures, other_text):
        pass


    def string(self, sep='-'):
        lines = []
        for dname, d in dicts.items():
            lines.append(dname)
            lines.append(sep*len(dname))
            lines.append(prnDict)