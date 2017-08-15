import logging

from quark_utilities import temporal_helpers

from quark_utilities import mongol

logger = logging.getLogger("quark_utilities.event_hub")
hub = None

def init_event_hub(app, event_store=None):
    global hub
    hub = EventHub(app)

class Event(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class DefaultEventStore(mongol.Repository):
    pass

class EventHub(object):

    def __init__(self, app):
        self._app = app
        self._handlers = {}
        self._event_store = None
        self._app.on_start(self._init_event_store)

    async def _init_event_store(self, app):
        if app.settings.get("save_events", False):
            logger.info("Creating event store.")
            db = await app.di.get("db")
            self._event_store = DefaultEventStore(db["events"])

    def subscribe(self, event_type):
        if event_type and event_type not in self._handlers:
            self._handlers[event_type] = set()

        def wrapper(f):
            self._handlers[event_type].add(f)
            return f

        return wrapper

    async def dispatch(self, event):
        logger.info("Event arrived <{}>".format(str(type(event))))

        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            await handler(event)

        if self._event_store:
            data = {
                "type": event.__class__.__name__,
            }

            data.update(event.__dict__)
            data["created_at"] = temporal_helpers.utc_now()
            await self._event_store.save(data)




