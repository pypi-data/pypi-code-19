from django.apps import AppConfig

from ws4ever.backend import subscribe_message


class WS4EverConfig(AppConfig):
    name = 'ws4ever'

    def ready(self):
        subscribe_message()
