#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Utilities for json2sql package."""

import io

import yaml

from mosql.util import raw as mosql_raw

from .errors import ClauseError
from .errors import InputError
from .errors import Json2SqlInternalError
from .errors import ParsingInputError


def load_input(definition):
    """Load and parse input if needed.

    :param definition: definition to use as an input (file, serialized JSON/YAML or dict)
    :return: loaded input
    :raises json2sql.ParsingInputError: when parsing fails
    """
    if isinstance(definition, (str, io.TextIOWrapper)):
        try:
            definition = yaml.safe_load(definition)
        except Exception as exc:
            raise ParsingInputError("Unable to parse input: %s" % str(exc))

    return definition


def any2sql(func, definition_dict=None, **definition_kwargs):
    """Handle general to SQL conversion.

    :param func: function to be called on the given definition
    :param definition_dict: statement definition in dict
    :param definition_kwargs: statement definition as kwargs
    :return: raw SQL statement
    """
    if definition_dict and definition_kwargs:
        raise InputError("Cannot process dict and kwargs input at the same time")

    definition = load_input(definition_dict or definition_kwargs)

    if definition.get('returning', '') == '*':
        definition['returning'] = mosql_raw('*')

    try:
        result = func(**definition)
    except (TypeError, AttributeError) as exc:
        raise ClauseError("Clause definition error: %s" % str(exc))
    except Exception as exc:
        raise Json2SqlInternalError("Unhandled error: %s" % str(exc))

    return result
