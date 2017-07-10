# coding=utf-8
import json
from helpers import json_helpers, exceptions
from jsonschema import Draft4Validator, FormatChecker
import datetime
import logging


def validate_schema(schema, data):
    validator = Draft4Validator(
        schema,
        types={"datetime": datetime.datetime},
        format_checker=FormatChecker())

    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        logging.warning(errors)
        raise exceptions.QError(
            400,
            message="errors.validationError",
            errors=format_validation_errors(errors))


def check_schema(schema, data):
    validator = Draft4Validator(
        schema,
        types={"datetime": datetime.datetime},
        format_checker=FormatChecker())

    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        logging.warning(errors)
    return True if not errors else False


def format_validation_errors(errors):
    messages = [{'.'.join(str(s) for s in list(x.path)): x.message}
                for x in errors]

    return messages
