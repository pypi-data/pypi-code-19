from typing import Callable
from typing import List
from evee.abstract_event_dispatcher import AbstractEventDispatcher
from evee.abstract_event_subscriber import AbstractEventSubscriber
from evee.event import Event
from evee.exception import BadMethodCallError


class ImmutableEventDispatcher(AbstractEventDispatcher):
    def __init__(self, dispatcher: AbstractEventDispatcher):
        super().__init__()
        self.__dispatcher = dispatcher

    def dispatch(self, event_name: str, event: Event = None) -> Event:
        return self.__dispatcher.dispatch(event_name, event)

    def add_listener(self, event_name: str, listener: Callable = None, priority: int = 0):
        raise BadMethodCallError('Unmodifiable event dispatcher must not be modified.')

    def add_subscriber(self, subscriber: AbstractEventSubscriber):
        raise BadMethodCallError('Unmodifiable event dispatcher must not be modified.')

    def remove_listener(self, event_name: str, listener: Callable):
        raise BadMethodCallError('Unmodifiable event dispatcher must not be modified.')

    def remove_subscriber(self, subscriber: AbstractEventSubscriber):
        raise BadMethodCallError('Unmodifiable event dispatcher must not be modified.')

    def get_listeners(self, event_name: str = None) -> List:
        return self.__dispatcher.get_listeners(event_name)

    def get_listener_priority(self, event_name: str, listener: Callable) -> int:
        return self.__dispatcher.get_listener_priority(event_name, listener)

    def has_listeners(self, event_name: str = None) -> bool:
        return self.__dispatcher.has_listeners(event_name)
