import abc


class ConfigBackend(abc.ABC):

    def __index__(self):
        pass

    @abc.abstractmethod
    def get_settings(self, name): ...
