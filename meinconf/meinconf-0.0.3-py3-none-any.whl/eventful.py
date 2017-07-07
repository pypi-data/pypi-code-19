import functools

import attr
import uninhibited

from .config import Config


@attr.s(repr=False)
class EventfulConfig(Config):
    """Glue to make configuration dynamic by sending events when keys change.
    """

    on_change = attr.ib(default=attr.Factory(uninhibited.Event))
    on_key_change = attr.ib(default=attr.Factory(uninhibited.Dispatch))

    def __setitem__(self, key, value):
        super(EventfulConfig, self).__setitem__(key, value)
        self.on_change(key, value)
        self.on_key_change.fire(key, key, value)

    def register_key_callback(self, key, handler=None):
        if handler is None:
            return functools.partial(self.register_key_callback, key)

        self.on_key_change[key] += handler

        # Call handler now if we already have this key
        if key in self:
            handler(key, self[key])

        return handler
