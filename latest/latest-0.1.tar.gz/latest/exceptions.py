""":mod:`exceptions` module contains exceptions classes defined for :mod:`latest` package.


"""


class LatestError(Exception):
    """Base class for all :mod:`latest` exceptions."""
    pass



class CodeError(LatestError):
    """Exception raised when bad syntax code is parsed in a template."""
    pass



class ContextError(LatestError):
    """Exception raised when context dictionary doesn't match names required by a template."""
    pass

