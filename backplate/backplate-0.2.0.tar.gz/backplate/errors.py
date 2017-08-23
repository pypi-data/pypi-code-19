
import logging

from flask import jsonify, current_app

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
                data = getattr(e, 'data', None)

                msg = str(e)
                if ':' in msg and len(msg.split(' ')[0].strip()) == 3:
                    status = int(msg.split(' ')[0].strip())
                    code = msg[3:msg.index(':')].strip()
                    code = '{}_{}'.format(
                        status,
                        code.replace(' ', '_').upper()
                    )
                    message = str(e)[msg.index(':') + 1:].strip()

                else:
                    code = str(type(e).__name__).replace(' ', '_').upper()
                    message = str(e)

                e = APIError(code, status, message, data)

        error = errors.get(e.code)
        if error:
            e.status = e.status or error['status']
            e.message = e.message or error['message']

        # log exception if 500 server error
        # remove message for consumer facing data if not on DEBUG mode
        status = e.status
        if status >= 500:
            log.exception(e)
            if current_app.config.get('DEBUG') is not True:
                e.message = None

        # json formatter for data envelopes
        data = e.format()
        if callable(json_formatter):
            data = json_formatter(data, status)

        resp = jsonify(data)
        return resp, status
    return handle_error

__all__ = ['APIError', 'errordef']
