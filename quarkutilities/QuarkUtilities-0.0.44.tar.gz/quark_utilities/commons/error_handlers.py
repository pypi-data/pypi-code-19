import json
import logging

from quark_utilities import json_helpers

from quark_utilities import mongol

from flasky.errors import FlaskyTornError
from quark_utilities.json_schema import JSONSchemaValidationError
from quark_utilities.jwt_security import AgentIsNotAuthorized
from quark_utilities.mongol import FlaskyDuplicateKeyError, IDMismatchError

logger = logging.getLogger("error.handlers")


class InfrastructureError(FlaskyTornError):

    def __init__(self, message=None):
        super().__init__(status_code=500, message=message)


def set_commons(handler, err):
    handler.set_status(err.status_code)
    handler.set_header("Content-Type", "application/json")


def init_error_handlers(app, settings):

    @app.error_handler(AgentIsNotAuthorized)
    async def handle_auth_error(handler, err, method_definition):
        handler.write({
            "error": {
                "code": err.err_code,
                "errors": [err.message],
                "required_permission": err.required_permission,
            }
        })
        set_commons(handler, err)

    @app.error_handler(FlaskyDuplicateKeyError)
    async def handle_duplicate_key_err(handler, err, method_definition):
        handler.write(json.dumps({
            "error": {
                "code": err.err_code,
                "errors": [err.message],
                "collection": err.collection_name,
                "key": err.key
            }
        }, default=json_helpers.bson_to_json))
        set_commons(handler, err)

    @app.error_handler(mongol.RecordNotExistsError)
    async def handle_record_exist_error(handler, err, method_definition):
        handler.write({
            "error": {
                "code": err.err_code,
                "errors": [err.message],
                "key": err.record_id,
                "collection": err.record_type
            }
        })
        set_commons(handler, err)

    @app.error_handler(JSONSchemaValidationError)
    async def handle_json_schema_error(handler, err, method_definition):
        handler.write({
            "error": {
                "code": "errors.parameterRequired",
                "errors": [err.message],
                "schema": method_definition.get("json_schema", {})
            }
        })
        set_commons(handler, err)

    @app.error_handler(IDMismatchError)
    async def handle_id_mismatch_err(handler, err, method_definition):
        handler.write({
            "error": {
                "code": "errors.badRequest",
                "message": "Given ID<{}> and Payload ID<{}> is different.".format(
                    err.given_id, err.data_id),
            }
        })

    @app.error_handler()
    async def handle_errors(handler, err, method_definition):
        logging.exception("Internal error occured")
        if isinstance(FlaskyTornError, err):
            handler.write({
                'error': {
                    'message': err.message,
                    'errors': []
                }
            })
            handler.set_status(err.status_code)