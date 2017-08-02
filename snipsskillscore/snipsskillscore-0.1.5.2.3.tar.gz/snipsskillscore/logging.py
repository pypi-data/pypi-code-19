# -*-: coding utf-8 -*-
""" Logging utilities. """

import inspect

LOGGING_ENABLED = True


def log(message):
    """ Print a log message.

    :param caller: the instance invoking the logger.
    :param message: the message to print.
    """

    if LOGGING_ENABLED != False:
        stack = inspect.stack()
        frame = stack[1][0]
        caller = frame.f_locals.get('self', None)
        tag = caller.__class__.__name__
        print("[{}] {}".format(tag, message))
