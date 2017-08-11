import datetime
import logging
import json

from flasky import errors
from flasky.errors import FlaskyTornError
from jsonschema import Draft4Validator, FormatChecker

logger = logging.getLogger("cms_utilities.json_schema")

__all__ = ["JSONSchemaValidator"]


class JSONSchemaValidator(object):

    def __init__(self, app):
        self._app = app
        self.init_app(app)

    def init_app(self, app):
        app.before_request(self.append_validator)
        app.before_request(self.validate_schema)

    async def handle_error(self, handler, err, endpoint_def):
        handler.write(json.dumps({
                    "error": err.reason
                }))
        handler.set_status(400)

    def append_validator(self, handler, method_definition):
        if 'json_schema' not in method_definition:
            return
        schema = method_definition["json_schema"]
        setattr(handler, "validate_body", self.validator_func_factory(schema))

    def validator_func_factory(self, schema):
        def validator(handler):
            body = handler.body_as_json()
            return self.do_validation(body, schema)
        return validator

    def do_validation(self, body, schema):
        validator = Draft4Validator(
            schema,
            types={"datetime": datetime.datetime},
            format_checker=FormatChecker()
        )

        return sorted(validator.iter_errors(body), key=lambda e: e.path)

    def validate_schema(self, handler, method_definition):
        if 'json_schema' not in method_definition:
            return

        body = handler.body_as_json(throw_exc=True)

        schema = method_definition['json_schema']
        _errors = self.do_validation(body, schema)
        if _errors:
            raise errors.FError(
                err_msg="Validation error occured...",
                err_code="errors.validationError",
                status_code=400,
                context={
                    'reason': format_validation_errors(_errors)
                }
            )

def get_human_readable(error):
    path = ".".join(list(error.path))
    if not path:
        path = "root"
    return path, error.message


def format_validation_errors(errors):
    _errors = {}
    for error in errors:
        path, message = get_human_readable(error)
        _errors[path] = message
    return _errors
