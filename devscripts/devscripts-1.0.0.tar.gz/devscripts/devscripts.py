#!/usr/bin/env python
# coding: utf-8
'''
Functions used while coding
'''
from time import sleep
from functools import wraps


def retry(exception_to_check, tries=5, delay=5, multiplier=2):
    '''Tries to call the wrapped function again, after an incremental delay

    :param exception_to_check: Exception(s) to check for, before retrying.
    :type exception_to_check: Exception
    :param tries: Number of time to retry before failling.
    :type tries: int
    :param delay: time in second to sleep before retrying.
    :type delay: int
    :param multiplier: multiply the delay each time the exception_to_check
        occurs.
    :type multiplier: int
    '''
    def deco_retry(func):
        '''Creates the retry decorator'''

        @wraps(func)
        def func_retry(*args, **kwargs):
            '''Actual wrapped function'''
            if multiplier >= 1 is not True:
                raise ValueError(
                    'multiplier = {}. It has to be superior to 1.'.format(
                        multiplier
                    )
                )
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as err:
                    message = "%s, retrying in %d seconds..." % (
                        str(err), mdelay)
                    print(message)
                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= multiplier
            return func(*args, **kwargs)

        return func_retry
    return deco_retry
