#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function
import math


def floor(number):
    return int(math.floor(number))


def ceil(number):
    return int(math.ceil(number))


def overlap_size(va, vb, ua, ub):
    """
    Calculate overlap size of intervals (va, vb) and (ua, ub)
    """
    alen = abs(va - vb)
    blen = abs(ua - ub)
    wide = max(va, vb, ua, ub) - min(va, vb, ua, ub)
    return alen + blen - wide
