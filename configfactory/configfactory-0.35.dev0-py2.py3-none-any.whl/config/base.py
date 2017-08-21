from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from configfactory.config.backends.base import ConfigBackend


def get_settings(name):
    return config_backend.get_settings(name)


class ConfigBackendProxy(LazyObject):

    default = 'configfactory.config.backends.memory.MemoryConfigBackend'

    def _setup(self):
        config_settings = getattr(
            settings,
            'CONFIG_BACKEND', {
                'class': self.default
            }
        )
        klass = import_string(config_settings['class'])
        params = config_settings.get('params', {})
        self._wrapped = klass(**params)


config_backend = ConfigBackendProxy()  # type: ConfigBackend
