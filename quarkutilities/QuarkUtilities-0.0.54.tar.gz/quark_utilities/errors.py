import json
import traceback

import logging
from functools import singledispatch

from quark_utilities import responser
from quark_utilities.json_helpers import bson_to_json

from flasky.errors import FError, FWarning

logger = logging.getLogger('error_handler')

def register_error_handler(app):

    @app.error_handler()
    async def handle_exc(handler, e, method_definition):
        _handle_exc(e, handler, method_definition=method_definition)

@singledispatch
def _handle_exc(e, handler, method_definition, **kwargs):
    logger.exception(msg="Unhandled exception occured....")

    handler.write(json.dumps(
        {
            "error": {
                "code": "errors.internalError",
                "message": str(e),
                "context": {
                    "stacktrace": traceback.format_exc()
                }
            }
        }
    ))
    handler.set_status(500)
    handler.set_header("Content-Type", "application/json")

@_handle_exc.register(FError)
def handle_ferror(e, handler, **kwargs):
    logger.exception(msg='Internal error occured...')

    handler.write(json.dumps(
        {
            "error": {
                "code": e.err_code,
                "message": e.err_msg,
                "context": e.context,
            }
        }, default=bson_to_json))

    handler.set_status(e.status_code)
    handler.set_header("Content-Type", "application/json")

@_handle_exc.register(FWarning)
def handle_fwarning(e, handler, **kwargs):
    logger.exception(msg='Internal error occured...')

    handler.write(json.dumps(
        {
            "warning": {
                "code": e.err_code,
                "message": e.err_msg,
                "context": e.context,
            }
        }, default=bson_to_json))

    handler.set_status(e.status_code)
    handler.set_header("Content-Type", "application/json")

class QError(Exception):

    def __init__(self, err_msg, err_code=None, status_code=500,
                 context=None, reason=None):
        super(QError, self).__init__(err_msg)
        self.err_code = err_code or "errors.internalError"
        self.err_msg = err_msg or "Internal error occured please contact your admin"
        self.status_code = status_code
        self.context = context or {}
        self.reason = reason


def handle_exc(handler, err):
    responser.to_response(
        handler,
        500,
        documents= {
        "error": {
            "code": "errors.internalError",
            "message": str(err),
            "context": {
                "stacktrace": traceback.format_exc()
            }
        }
    })



def handle_q_error(handler, err):
    responser.to_response(
        handler,
        err.status_code,
        documents={
            "error": {
                "code": err.err_code,
                "message": err.err_msg,
                "context": err.context,
            }
        }
    )


def handle_error(handler, err, method_def):
    if type(err) == QError:
        handle_q_error(handler, err)
    else:
        handle_exc(handler, err)

    logger.exception('Error occured')


class QErrorHandler(object):

    def handle(self, handler, err):
       responser.to_response(
           handler,
           err.status_code,
           documents={
                    "error": {
                        "code": err.err_code,
                        "message": err.err_msg,
                        "context": err.context,
                }
            }
       )

