from abc import ABCMeta
from abc import abstractmethod
from typing import Callable
from typing import List
from evee.event import Event
from evee.abstract_event_subscriber import AbstractEventSubscriber


class AbstractEventDispatcher(object, metaclass=ABCMeta):

    @abstractmethod
    def dispatch(self, event_name: str, event: Event = None) -> Event:
        """
        Dispatches an event to all registered listeners.

        :param event_name: The name of the event to dispatch. The name of the event
                            is the name of the method that is invoked on listeners
        :param event:      The event to pass to the event handlers/listeners
                            If not supplied, an empty Event instance is created
        :return:           An instance of Event
        """
        pass

    @abstractmethod
    def add_listener(self, event_name: str, listener: Callable = None, priority: int = 0):
        """
        Adds an event listener that listens on the specified events.

        :param event_name: The event to listen on
        :param listener:   The listener
        :param priority:   The higher this value, the earlier an event listener
                            will be triggered in the chain (defaults to 0)
        """
        pass

    @abstractmethod
    def add_subscriber(self, subscriber: AbstractEventSubscriber):
        """
        Adds an event subscriber. The subscriber is asked for all the events he is
        interested in and added as a listener for these events.

        :param subscriber:  The subscriber
        """
        pass

    @abstractmethod
    def remove_listener(self, event_name: str, listener: Callable):
        """
        Removes an event listener from the specified events.

        :param event_name: The event to remove a listener from
        :param listener:   The listener to remove
        """
        pass

    @abstractmethod
    def remove_subscriber(self, subscriber: AbstractEventSubscriber):
        """
        Removes an event subscriber.

        :param subscriber: The subscriber
        :return:
        """
        pass

    @abstractmethod
    def get_listeners(self, event_name: str = None) -> List:
        """
        Gets the listener of a specific event or all listeners stored by
        descending priority.

        :param event_name: The name of the event
        :return:           The event listeners for the specified event, or all
                            event listeners by event name
        """
        pass

    @abstractmethod
    def get_listener_priority(self, event_name: str, listener: Callable) -> int:
        """
        Get the listener priority for a specific event.

        :param event_name: The name of the event
        :param listener:   The listener
        :return:           The event listener priority
        """
        pass

    @abstractmethod
    def has_listeners(self, event_name: str = None) -> bool:
        pass
