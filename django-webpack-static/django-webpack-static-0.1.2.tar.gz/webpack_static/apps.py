import json
from datetime import datetime, timedelta

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class WebpackStaticConfig(AppConfig):
    name = 'webpack_static'
    mapping = {}
    manifest_reloaded_at = None

    def ready(self):
        """
        Check settings and load webpack manifest file mappings
        """
        if not hasattr(settings, 'WEBPACK_MANIFEST_PATH'):
            raise ImproperlyConfigured(
                'WEBPACK_MANIFEST_PATH is not set. Please set it or remove webpack_static from INSTALLED_APPS')

        if not hasattr(settings, 'WEBPACK_MANIFEST_RELOAD'):
            settings.WEBPACK_MANIFEST_RELOAD = timedelta(seconds=5)

        self.load_manifest()

    @property
    def manifest_needs_reloading(self):
        """
        Returns a boolean indicating if manifest file should be reloaded based on time-based conditions
        :return: True if manifest seems old, False otherwise
        """
        if self.manifest_reloaded_at is None:
            return True

        if datetime.now() > (self.manifest_reloaded_at + settings.WEBPACK_MANIFEST_RELOAD):
            return True

        return False

    def load_manifest(self):
        """
        Loads manifest file
        """
        with open(settings.WEBPACK_MANIFEST_PATH) as manifest:
            self.mapping = json.load(manifest)

        self.manifest_reloaded_at = datetime.now()

    def reload_manifest(self):
        """
        Reloads manifest file if needed
        """
        if self.manifest_needs_reloading:
            self.load_manifest()
