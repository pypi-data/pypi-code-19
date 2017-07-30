import pkg_resources
from functools import lru_cache


@lru_cache(None)
def get_handlers():
    return {
        entry.name: entry.load()
        for entry in
        pkg_resources.iter_entry_points('workaround_handlers')
    }


@lru_cache(None)
def get_all_adjectives():
    return {
        adjective
        for handler in get_handlers().values()
        for adjective in handler.adjectives
    }


@lru_cache()
def get_handler(value, adjective):
    handlers = get_handlers()

    for handler in handlers.values():
        instance = handler()
        if instance.can_handle(value, adjective):
            return instance
