import importlib

from django.conf import settings


def import_module(class_name):
    tokens = class_name.split('.')
    pkg = importlib.import_module('.'.join(tokens[:-1]))
    return getattr(pkg, tokens[-1])


def get_websocket_resources():
    return [(path, import_module(handler_class))
            for path, handler_class in settings.WS4EVER['ROUTES'].items()]
