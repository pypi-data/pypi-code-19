from abc import ABCMeta
from abc import abstractmethod


class AbstractEventSubscriber(object, metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get_subscribed_events():
        pass
