# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Callbacks rules classes and helpers
"""
from functools import wraps


def call_count_wrapper(function, lifecycle, call_count_interval,
                       observation_key, callback):
    """ Wrapper around lifecycle methods that record number of calls
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        """ Record the number of calls for this callback lifecycle method.
        Buffer the number in the callback itself (self.call_counts) and record
        an observation every X times, X being the field call_count_interval of
        the rule.
        """
        current_count = callback.call_counts[lifecycle]

        if current_count + 1 == call_count_interval:
            callback.record_observation('sqreen_call_counts', observation_key,
                                        call_count_interval)
            callback.call_counts[lifecycle] = 0
        else:
            callback.call_counts[lifecycle] += 1

        return function(*args, **kwargs)

    wrapped.__wrapped__ = function

    return wrapped
