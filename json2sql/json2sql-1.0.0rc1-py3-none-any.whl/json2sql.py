#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Core json2sql implementation."""

from mosql.query import delete
from mosql.query import insert
from mosql.query import replace
from mosql.query import update

from .errors import InputError
from .errors import Json2SqlError
from .errors import Json2SqlInternalError
from .errors import NoStatementError
from .errors import UnknownStatementError
from .select import select2sql
from .utils import any2sql
from .utils import load_input


def delete2sql(definition_dict=None, **definition_kwargs):
    """Create DELETE SQL statement based on definition.

    :param definition_dict: definition of DELETE SQL statement as dictionary
    :param definition_kwargs: definition of DELETE SQL statement as kwargs
    :return: raw SQL statement
    :rtype: str
    """
    return any2sql(delete, definition_dict, **definition_kwargs)


def update2sql(definition_dict=None, **definition_kwargs):
    """Create UPDATE SQL statement based on definition.

    :param definition_dict: definition of UPDATE SQL statement as dictionary
    :param definition_kwargs: definition of UPDATE SQL statement as kwargs
    :return: raw SQL statement
    :rtype: str
    """
    return any2sql(update, definition_dict, **definition_kwargs)


def insert2sql(definition_dict=None, **definition_kwargs):
    """Create INSERT SQL statement based on definition.

    :param definition_dict: definition of INSERT SQL statement as dictionary
    :param definition_kwargs: definition of INSERT SQL statement as kwargs
    :return: raw SQL statement
    :rtype: str
    """
    return any2sql(insert, definition_dict, **definition_kwargs)


def replace2sql(definition_dict=None, **definition_kwargs):
    """Create REPLACE SQL statement based on definition.

    :param definition_dict: definition of REPLACE SQL statement as dictionary
    :param definition_kwargs: definition of REPLACE SQL statement as kwargs
    :return: raw SQL statement
    :rtype: str
    """
    return any2sql(replace, definition_dict, **definition_kwargs)


def json2sql(raw_json=None, **definition):  # pylint: disable=too-many-branches
    """Convert raw dictionary, JSON/YAML to SQL statement.

    :param raw_json: raw JSON/YAML or file to convert to SQL statement
    :type raw_json: str or file
    :return: raw SQL statement
    :rtype: str
    """
    if raw_json and definition:
        raise InputError("Cannot process dict and kwargs input at the same time")

    definition = load_input(raw_json or definition)
    if not isinstance(definition, dict):
        raise UnknownStatementError("Unknown statement parsed: %s (type: %s)"
                                    % (definition, type(definition)))

    try:
        statement = definition.pop('statement', None)
        if statement is None:
            raise NoStatementError("No statement provided")

        statement = statement.lower()

        if statement == 'delete':
            return delete2sql(definition)
        elif statement == 'insert':
            return insert2sql(definition)
        elif statement == 'select':
            return select2sql(definition)
        elif statement == 'update':
            return update2sql(definition)
        elif statement == 'replace':
            return replace2sql(definition)
        else:
            raise UnknownStatementError("Unknown statement provided '%s' in definition %s"
                                        % (statement, definition))
    except Exception as exc:
        if isinstance(exc, Json2SqlError):
            raise

        raise Json2SqlInternalError("Internal json2sql error: %s" % str(exc))
