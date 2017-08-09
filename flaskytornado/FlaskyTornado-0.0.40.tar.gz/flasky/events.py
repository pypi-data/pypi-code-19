import datetime
import json
import logging
from asyncio import futures

from concurrent.futures import ThreadPoolExecutor
from inspect import isclass

import functools

import asyncio
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import to_asyncio_future

from flasky import errors

_logger = logging.getLogger("cm.events")

__HANDLERS = {}

__GLOBAL_HANDLERS = []

_executor = ThreadPoolExecutor(2)


class Event(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)


async def dispatch(event):
    _e_type = event.__class__.__name__

    for g_handler in __GLOBAL_HANDLERS:
        _logger.info("Handler<{}> runned for event<{}>".format(
            g_handler.__name__, type(event).__name__
        ))

        asyncio.ensure_future(g_handler(event))

    if _e_type not in __HANDLERS:
        return

    for handler in __HANDLERS[_e_type]:
        _logger.info("Handler<{}> runned for event<{}>".format(
            handler.__name__, type(event).__name__
        ))

        asyncio.ensure_future(handler(event))

def subscribe_g(f):
    global __GLOBAL_HANDLERS
    __GLOBAL_HANDLERS.append(f)

def subscribe(event_type, f):
    global __HANDLERS
    if not isclass(event_type):
        raise errors.FError(
            err_code='errors.internalError',
            err_msg='Can not subscribe an instance',
            context={
                "event_type": str(event_type),
                "f": str(f)
            }
        )

    event_type = event_type.__name__
    if event_type not in __HANDLERS:
        __HANDLERS[event_type] = []

    __HANDLERS[event_type].append(f)

    _logger.info(
        "Function<{}> subscribed event<{}>."
            .format(f.__name__, event_type.__name__)
    )


def subscribe_global(f):
    global __HANDLERS
    __HANDLERS[None].append(f)




