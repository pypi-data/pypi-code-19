# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"



class TimeoutError(OSError):
    """ Timeout expired. """
    pass

class FileNotFoundError(OSError):
    """ File not found. """
    pass
