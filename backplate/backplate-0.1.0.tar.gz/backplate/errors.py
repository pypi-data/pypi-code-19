
import logging

from flask import jsonify
from flask_api import status as HTTP_Statuses

log = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, code, status=None, message=None, data=None):
        self.code = code
        self.status = status
        self.message = message
        self.data = data

    def format(self):
        code = self.code
        status = self.status
        message = self.message
        data = self.data

        error_object = {
            'code': code,
            'status': status,
            'message': message,
        }

        if data:
            error_object['data'] = data

        return error_object

generics = {}
for status_string in dir(HTTP_Statuses):
    if not status_string.startswith('HTTP_'):
        continue

    status = int(status_string[5:8])
    name = status_string[9:]

    generics[status] = name \
        .replace('_', ' ') \
        .title() \
        .replace('Http', 'HTTP')

def errordef(code, status=400, message=None, exception=None):
    return {
        'code': code,
        'status': status,
        'message': message,
        'exception': exception
    }

def create_error_handler(errors={}, json_formatter=None):

    exception_code_map = {}
    for error_code in errors:
        error = errors[error_code]
        exception = error['exception']
        if exception:
            exception_code_map[exception] = error['code']

    def handle_error(e):
        # get exception status code, default 500 for unknown/generic
        status = getattr(e, 'code', 500)

        exception_type = type(e)
        if exception_type is not APIError:
            # look for exception type from bases of exception
            if exception_type not in exception_code_map:
                for base in exception_type.__bases__:
                    if base in exception_code_map:
                        exception_type = base
                        break

            # if the exception (or any of its bases) registered
            if exception_type in exception_code_map:
                exception_code = exception_code_map.get(exception_type)
                error = errors.get(exception_code)

                code = error['code']
                status = error['status']
                message = error['message'] or str(e)

                e = APIError(code, status, message)

            # default to generic exceptions
            else:
                code = None
                status = status
                message = None

                generic = generics.get(status, 'API Error')
                if generic:
                    code = '{}_{}'.format(
                        status,
                        generic.replace(' ', '_').upper()
                    )
                    message = generic
                else:
                    code = 'GENERAL_ERROR'
                    message = str(e)

                e = APIError(code, status, message)

        error = errors.get(e.code)
        if error:
            e.status = e.status or error['status']
            e.message = e.message or error['message']

        # log exception if 500 server error
        # remove message for consumer facing data
        status = e.status
        if status >= 500:
            log.exception(e)
            e.message = None

        # json formatter for data envelopes
        data = e.format()
        if callable(json_formatter):
            data = json_formatter(data, status)

        resp = jsonify(data)
        return resp, status
    return handle_error

__all__ = ['APIError', 'errordef']
