"""Environment variable config parsing library"""

import os

from envpy import parser
from envpy.parser import (
    EnvpyError,
    MissingConfigError,
    ParsingError,
    Schema,
    ValueTypeError,
)


def get_config(config_schema, env=None):
    """Parse config from the environment against a given schema

    Args:
        config_schema:
            A dictionary mapping keys in the environment to envpy Schema
            objects describing the expected value.
        env:
            An optional dictionary used to override the environment rather
            than getting it from the os.

    Returns:
        A dictionary which maps the values pulled from the environment and
        parsed against the given schema.

    Raises:
        MissingConfigError:
            A value in the schema with no default could not be found in the
            environment.
        ParsingError:
            A value was found in the environment but could not be parsed into
            the given value type.
    """
    if env is None:
        env = os.environ

    return parser.parse_env(
        config_schema,
        env,
    )
