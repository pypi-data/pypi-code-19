
import re
import logging
import inspect

from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')

def to_snake_case(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()

def parse_http_error(s):
    if ':' in s and len(s.split(' ')[0].strip()) == 3:
        status = int(s.split(' ')[0].strip())
        code = s[3:s.index(':')].strip()
        code = '{}_{}'.format(status, code).replace(' ', '_').upper()
        message = re.sub(' +', ' ', s[s.index(':') + 1:]).strip()
        return {'status': status, 'code': code, 'message': message}
    return None

class APIException(Exception):
    def __init__(self,
                 code=None,
                 status=None,
                 message=None,
                 data=None,
                 exception=None):

        self.code = code
        self.status = status
        self.message = message
        self.data = data

        if exception:
            self.code = to_snake_case(str(type(exception).__name__)).upper()
            self.status = getattr(exception, 'status', None)
            self.message = str(exception)
            self.data = getattr(exception, 'data', None)

    def format(self):
        obj = {
            'code': self.code,
            'status': self.status,
            'message': self.message,
        }

        if self.data:
            obj['data'] = self.data

        return obj

class Error(object):
    def __init__(self,
                 handle,
                 status=None,
                 message=None,
                 code=None):

        if inspect.isclass(handle) and issubclass(handle, BaseException):
            self.exception = handle
            self.code = code
        else:
            self.exception = None
            self.code = handle

        self.status = status
        self.message = message

def create_error_handler(errors={}, json_formatter=None):

    error_code_map = {}
    error_exception_map = {}

    for error in errors:
        if error.code and not error.exception:
            error_code_map[error.code] = error
        if error.exception:
            error_exception_map[error.exception] = error

    def handle_error(e):
        error = None
        e_type = type(e)

        if e_type is APIException:
            error = e
            base = error_code_map.get(error.code)

            if base:
                error.status = error.status or (base and base.status)
                error.message = error.message or (base and base.message)

        elif issubclass(e_type, HTTPException):
            e_message = str(e)
            e_parsed = parse_http_error(e_message)

            error = APIException(
                e_parsed.get('code'),
                e_parsed.get('status') or 500,
                e_parsed.get('message')
            )

        else:
            error = APIException(exception=e)
            base = error_exception_map.get(e_type)

            if not base:
                for _base in e_type.__bases__:
                    if _base in error_exception_map:
                        base = error_exception_map.get(_base)
                        break

            error.code = error.code or (base and base.code)
            error.status = error.status or (base and base.status) or 500
            error.message = error.message or (base and base.message)

        status = error.status
        if status >= 500:
            # log exception if 5xx server error
            log.exception(e)
            # remove message for consumer facing data if not on DEBUG mode
            if current_app.config.get('DEBUG') is not True:
                e.message = None

        # json formatter for data envelopes
        data = error.format()
        if callable(json_formatter):
            data = json_formatter(data, status)

        resp = jsonify(data)
        return resp, status

    return handle_error

__all__ = ['APIException', 'Error']
