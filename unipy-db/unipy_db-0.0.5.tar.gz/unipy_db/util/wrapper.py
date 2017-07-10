# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:33:36 2017

@author: Young Ju Kim
"""


from datetime import datetime as dt
from functools import wraps

__all__ = ['time_profiler']


def time_profiler(func):

    @wraps(func)
    def profiler(*args, **kwargs):

        start_tm = dt.now()
        print("JobStart :", start_tm)

        res = func(*args, **kwargs)

        end_tm = dt.now()
        print("JobEnd   :", end_tm)

        elapsed_tm = end_tm - start_tm
        print("Elapsed  :", elapsed_tm)

        return res

    return profiler


