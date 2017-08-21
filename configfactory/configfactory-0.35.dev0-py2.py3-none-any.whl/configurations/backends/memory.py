from .base import ConfigBackend


class MemoryConfigBackend(ConfigBackend):

    def __init__(self):
        self._storage = {}

    def get_settings(self, component, environment):
        try:
            return self._storage[component][environment]
        except KeyError:
            return {}

    def update_settings(self, component, environment, settings):
        if component not in self._storage:
            self._storage[component] = {}
        self._storage[component][environment] = settings
