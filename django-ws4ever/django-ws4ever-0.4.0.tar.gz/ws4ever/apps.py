from django.apps import AppConfig

from ws4ever.backend import get_backend


class WS4EverConfig(AppConfig):
    name = 'ws4ever'

    def ready(self):
        get_backend()
