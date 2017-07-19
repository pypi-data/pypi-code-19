from rest_framework import status
from rest_framework.exceptions import APIException

from ali_base_service.util.errors import get_error
from ali_base_service.util.handlers import get_error_response


class CustomValidationError(APIException):
    status_code = status.HTTP_200_OK

    def __init__(self, error_code, args=None):
        self.detail = get_error_response(get_error(error_code, args)).data
