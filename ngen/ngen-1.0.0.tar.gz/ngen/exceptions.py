from __future__ import unicode_literals, absolute_import, print_function

class Error(Exception):
    "General error class for inheritance purposes"
    pass


class ParserError(Error):
    pass


class FieldError(ParserError, TypeError):
    pass


class ValidationError(Error):
    pass


class ImproperlyConfigured(Error):
    pass
