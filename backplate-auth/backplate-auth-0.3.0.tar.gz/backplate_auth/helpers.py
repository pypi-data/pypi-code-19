
from backplate import Error
from backplate_auth.exceptions import (
    AuthAccessError,
    AuthValidationError,
)

backplate_auth_errordefs = [
    Error(AuthAccessError, 401, code='AUTH_INVALID_TOKEN'),
    Error(AuthValidationError, 422, code='AUTH_MALFORMED_TOKEN'),
]

__all__ = [
    backplate_auth_errordefs
]
