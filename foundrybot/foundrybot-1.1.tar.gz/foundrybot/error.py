import sys

class FoundrybotError(Exception):
    def __init__(self, message=None, type='validation_error'):
        super(FoundrybotError, self).__init__(message)

        self._message = message
        self.type = type
