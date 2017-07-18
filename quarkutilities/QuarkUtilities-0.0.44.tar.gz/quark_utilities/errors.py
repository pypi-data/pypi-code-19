import json
import traceback

import logging

from quark_utilities import responser


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

logger = logging.getLogger('error_handler')

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

