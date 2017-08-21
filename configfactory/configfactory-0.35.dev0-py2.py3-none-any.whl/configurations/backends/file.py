from .base import ConfigBackend


class FileConfigBackend(ConfigBackend):

    def get_settings(self, component, environment):
        pass

    def update_settings(self, component, environment, settings):
        pass
