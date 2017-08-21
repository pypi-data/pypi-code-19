import abc


class ConfigBackend(abc.ABC):

    def __index__(self):
        pass

    @abc.abstractmethod
    def get_settings(self, component, environment):
        pass

    @abc.abstractmethod
    def update_settings(self, component, environment, settings):
        pass
