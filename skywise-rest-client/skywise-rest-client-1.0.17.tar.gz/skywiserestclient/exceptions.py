class PySkyWiseException(Exception):
    pass


class NotYetImplementedException(PySkyWiseException):
    pass


class DateTimeOutOfBounds(PySkyWiseException):
    pass


class MissingParametersException(PySkyWiseException):
    pass
