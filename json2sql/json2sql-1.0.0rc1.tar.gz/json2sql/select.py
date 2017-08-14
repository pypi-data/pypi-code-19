#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""SELECT SQL statement implementation."""

import os
import re

import mosql.query as mosql_query
from mosql.query import select
from mosql.util import raw as mosql_raw

from .utils import any2sql

DEFAULT_FILTER_KEY = os.getenv('JSON2SQL_FILTER_KEY', '$filter')
QUERY_REFERENCE = re.compile('[a-zA-Z_.]+')


def is_filter_query(filter_query):
    """Check if the given query is a filter query.

    :param filter_query: dictionary to be checked for filter_query
    :return: True if filter_query is considered to be expanded based on database query
    """
    return isinstance(filter_query, dict) and DEFAULT_FILTER_KEY in filter_query.keys()


def _expand_join(join_definition):
    """Expand join definition to `join' call.

    :param join_definition: join definition
    :return: expanded join definition
    """
    join_table_name = join_definition.pop('table')
    join_func = getattr(mosql_query, join_definition.pop('join_type', 'join'))
    return join_func(join_table_name, **join_definition)


def _construct_select_query(**filter_definition):
    """Return SELECT statement that will be used as a filter.

    :param filter_definition: definition of a filter that should be used for SELECT construction
    :return:
    """
    table_name = filter_definition.pop('table')
    distinct = filter_definition.pop('distinct', False)
    select_count = filter_definition.pop('count', False)

    if distinct and select_count:
        raise ValueError('SELECT (DISTINCT ...) is not supported')

    if select_count and 'select' in filter_definition:
        raise ValueError('SELECT COUNT(columns) is not supported')

    if 'joins' in filter_definition:
        join_definitions = filter_definition.pop('joins')

        if not isinstance(join_definitions, (tuple, list)):
            join_definitions = (join_definitions,)

        filter_definition['joins'] = []
        for join_def in join_definitions:
            filter_definition['joins'].append(_expand_join(join_def))

    if 'where' in filter_definition:
        for key, value in filter_definition['where'].items():
            if is_filter_query(value):
                # We can do it recursively here
                sub_query = value.pop(DEFAULT_FILTER_KEY)
                if value:
                    #_logger.warning("Ignoring sub-query parameters: %s", value)
                    raise ValueError("TBD")
                filter_definition['where'][key] = mosql_raw('( {} )'.format(_construct_select_query(**sub_query)))
            elif isinstance(value, str) and value.startswith('$') and QUERY_REFERENCE.fullmatch(value[1:]):
                # Make sure we construct correct query with escaped table name and escaped column for sub-queries
                filter_definition['where'][key] = mosql_raw('"{}"'.format('"."'.join(value[1:].split('.'))))

    raw_select = select(table_name, **filter_definition)

    if distinct:
        # Note that we want to limit replace to the current SELECT, not affect nested ones
        raw_select = raw_select.replace('SELECT', 'SELECT DISTINCT', 1)
    if select_count:
        # Note that we want to limit replace to the current SELECT, not affect nested ones
        raw_select = raw_select.replace('SELECT *', 'SELECT COUNT(*)', 1)

    return raw_select


def select2sql(definition_dict=None, **definition_kwargs):
    """Create SELECT SQL statement based on definition.

    :param definition_dict: definition of SELECT SQL statement as dictionary
    :param definition_kwargs: definition of SELECT SQL statement as kwargs
    :return: raw SQL statement
    :rtype: str
    """
    return any2sql(_construct_select_query, definition_dict, **definition_kwargs)
