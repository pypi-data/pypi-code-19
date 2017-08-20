class LoopiaError(Exception):
    _exceptions = {}

    code = None
    message = None

    def __init__(self, response=None):
        super(LoopiaError, self).__init__(self.message)
        self.response = response

    @classmethod
    def register(cls, exception):
        if exception.code in cls._exceptions:
            raise ValueError("'{}' already exists".format(exception.code))

        cls._exceptions[exception.code] = exception
        return exception

    @classmethod
    def from_code(cls, code, response=None):
        if code not in cls._exceptions:
            code = None

        return cls._exceptions[code](response)


@LoopiaError.register
class UnknownError(LoopiaError):
    code = None
    message = "Unknown error"


@LoopiaError.register
class AuthError(LoopiaError):
    code = "AUTH_ERROR"
    message = u"Wrong username or password"


@LoopiaError.register
class DomainOccupiedError(LoopiaError):
    code = "DOMAIN_OCCUPIED"
    message = u"Domain is not available for registration"


@LoopiaError.register
class RateLimitedError(LoopiaError):
    code = "RATE_LIMITED"
    message = u"Maximum number of requests over time reached"


@LoopiaError.register
class BadIndataError(LoopiaError):
    code = "BAD_INDATA"
    message = u"Invalid parameters"


@LoopiaError.register
class InsufficientFundsError(LoopiaError):
    code = "INSUFFICIENT_FUNDS"
    message = u"Not enough funds to complete the task"
