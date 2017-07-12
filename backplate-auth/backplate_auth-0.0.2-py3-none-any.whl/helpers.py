
from backplate import errordef
from backplate_auth.exceptions import (
    AuthAccessError,
    AuthValidationError,
)

backplate_auth_errordefs = [
    errordef('AUTH_INVALID_TOKEN', 401, exception=AuthAccessError),
    errordef('AUTH_MALFORMED_TOKEN', 422, exception=AuthValidationError),
]

__all__ = [
    backplate_auth_errordefs
]
