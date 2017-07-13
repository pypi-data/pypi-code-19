import json

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class WebpackStaticConfig(AppConfig):
    name = 'webpack_static'
    mapping = {}

    def ready(self):
        """
        Check settings and load webpack manifest file mappings
        """
        if not hasattr(settings, 'WEBPACK_MANIFEST_PATH'):
            raise ImproperlyConfigured('WEBPACK_MANIFEST_PATH is not set. Please set it or remove webpack_static from INSTALLED_APPS')

        with open(settings.WEBPACK_MANIFEST_PATH) as manifest:
            self.mapping = json.load(manifest)
