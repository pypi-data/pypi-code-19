#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['env', 'cbfTail', 'cbfHead']

import jinja2
from . import tplesp, tpledf, tplcbf


__templates = {
    'edf': tpledf.edfStr,
    'esp': tplesp.esperantoStr,
    'cbf': tplcbf.cbfStr,
}

env = jinja2.Environment(loader=jinja2.DictLoader(__templates), newline_sequence='\r\n')
cbfTail = tplcbf.cbfTail
cbfHead = tplcbf.cbfHead
