import importlib

from django.conf import settings


def get_handler_class(class_name):
    tokens = class_name.split('.')
    pkg = importlib.import_module('.'.join(tokens[:-1]))
    return getattr(pkg, tokens[-1])


def get_websocket_sources():
    return [(path, get_handler_class(handler_class))
            for path, handler_class in settings.WEBSOCKET_PATHS.items()]
