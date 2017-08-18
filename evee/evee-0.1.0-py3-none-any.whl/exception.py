class EventDispatcherError(Exception):
    pass


class LogicError(EventDispatcherError):
    pass


class BadMethodCallError(LogicError):
    pass
