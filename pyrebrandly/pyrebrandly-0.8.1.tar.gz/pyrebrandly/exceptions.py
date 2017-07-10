class RebrandlyError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
class Error(RebrandlyError):
    """
    Base Error
    """
    pass
class APIError(Error):
    """
    Base API Error
    """
    pass
class BadRequestError(APIError):
    """
    Invalid JSON Request

    Code: 400
    """
    pass
class NotAuthorizedError(APIError):
    """
    Authorization credentials invalid

    oAuth Token expired etc.

    Code: 401
    """
    pass

class AlreadyExistsError(APIError):
    """
    Link etc. Already Exists

    Code: 403
    """
    pass

class InvalidFormatError(APIError):
    """
    Invalid input format

    Missing body

    Limits threshold reached

    Code: 403
    """
    pass

class NotFoundError(APIError):
    """
    Resource/Endpoint not found

    Code: 404
    """
    pass

class InternalServerError(APIError):
    """
    API Endpoint Server Error

    Code: 500
    """
    pass

class BadGatewayError(APIError):
    """
    Failure in Rebrandly's upstream providers

    Code: 502
    """
    pass

class APIUnavailableError(APIError):
    """
    API endpoint under maintenance

    Code: 503
    """
    pass
class APITimeoutError(APIError):
    """
    API Operation Timeout

    Code: 504
    """
    pass