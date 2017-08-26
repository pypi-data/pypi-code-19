
class AuthError(Exception):
    pass

class AuthAccessError(AuthError):
    pass

class AuthValidationError(AuthError):
    pass

class AuthInvalidTokenError(AuthValidationError):
    pass

class AuthInvalidTokenPayloadError(AuthValidationError):
    pass

class AuthInvalidTokenUserError(AuthValidationError):
    pass

class AuthResolveRequestUserError(AuthValidationError):
    pass

class AuthInvalidSessionError(AuthValidationError):
    pass

__all__ = [
    'AuthError',
    'AuthAccessError',
    'AuthValidationError',
    'AuthInvalidTokenError',
    'AuthInvalidTokenPayloadError',
    'AuthInvalidTokenUserError',
    'AuthResolveRequestUserError',
    'AuthInvalidSessionError'
]
