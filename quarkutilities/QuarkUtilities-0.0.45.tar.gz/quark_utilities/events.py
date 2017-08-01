import json
import logging

from concurrent.futures import ThreadPoolExecutor
from tornado import gen

from src.helpers.json_helpers import bson_to_json
from src.utils import temporal_helpers
from src.utils.db import GenericRepository

_logger = logging.getLogger("cm.events")

__HANDLERS = {}
__HANDLERS[None] = []

_executor = ThreadPoolExecutor(2)

class Event(object):
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

class EventPersister(GenericRepository):


    async def on_event(self, event):
        data = {
            "type": event.__class__.__name__
        }

        data.update(event.__dict__)

        data['sys'] = {}
        data['sys']['created_at'] = temporal_helpers.utc_now()

        await self.save(json.loads(json.dumps(data, default=bson_to_json)))

        _logger.info("Persisted event.")

@gen.coroutine
def dispatch(event):
    _e_type = type(event)

    for handler in __HANDLERS[None] or []:
        _logger.info("Handler<{}> runned for event<{}>".format(
            handler.__name__, type(event).__name__
        ))

        yield _executor.submit(handler, event)

    if _e_type not in __HANDLERS:
        return

    for handler in __HANDLERS[_e_type]:
        _logger.info("Handler<{}> runned for event<{}>".format(
            handler.__name__, type(event).__name__
        ))
        yield _executor.submit(handler, event)


def subscribe(event_type, f):
    global __HANDLERS

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




