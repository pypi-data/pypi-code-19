# coding: utf-8
"""
Contains the class Singleton.
"""


class Singleton(object):
    """
    Wrapper class to indicate an object should be instancied once.
    """
    def __init__(self, params):
        self.params = params
