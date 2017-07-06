import collections

import arrow
import sqlalchemy

import chryso.schema

PARSERS = {
    'DATETIME' : lambda value: arrow.get(value).datetime
}

class QueryParams(): # pylint: disable=too-few-public-methods
    def __init__(self, filters=None, limit=None, order=None, offset=None):
        self.filters = filters if filters is not None else {}
        self.limit = limit
        self.offset = offset
        self.order = parse_order(order if order is not None else [])

def parse_order(order):
    if isinstance(order, str):
        order = [order]
    result = []
    for o in order:
        if o.startswith('-'):
            result.append(OrderArgument(o[1:], False))
        elif o.startswith('+'):
            result.append(OrderArgument(o[1:], True))
        else:
            result.append(OrderArgument(o, True))
    return result

OrderArgument = collections.namedtuple('OrderArgument', ['name', 'ascending'])
FilterArgument = collections.namedtuple('FilterArgument', ['operation', 'values'])

def _validate(column, arguments):
    parser = PARSERS.get(str(column.type))
    if not parser:
        return
    for argument in arguments:
        for value in argument.values:
            try:
                value = parser(value)
            except arrow.parser.ParserError:
                raise Exception("Unable to parse {} as datetime. Your value must be a valid ISO8601 date.".format(value))

def _conditional(column, operation, value):
    if isinstance(value, chryso.schema.BaseEnum):
        value = str(value)
    if operation == '=':
        return (column == value)
    elif operation == '>':
        return (column > value)
    elif operation == '>=':
        return (column >= value)
    elif operation == '<':
        return (column < value)
    elif operation == '<=':
        return (column <= value)
    else:
        raise ValueError("operation {} is not a valid operation. Please choose one of '=', '>', '>=', '<', or '<='".format(operation))

def _apply_filter(select, column, arguments):
    _validate(column, arguments)

    # Strings are iterable so we can't rely on our TypeError catch below
    if isinstance(arguments, str):
        return select.where(column == arguments)

    # This case happens when filter['uuid'] = []. The uuid is removed in sepiida because the user doesn't have access to the requested
    # resource.
    if not arguments:
        return select.where(column != column)

    # This case happens when the filter we are given is not a list but rather a FilterArgument itself
    if hasattr(arguments, 'operation') and hasattr(arguments, 'values'):
        arguments = [arguments]

    try:
        for argument in arguments:
            conditionals = [_conditional(column, argument.operation, value) for value in argument.values]
            select = select.where(
                sqlalchemy.or_(*conditionals)
            )
    except AttributeError:
        select = select.where(column.in_(arguments))
    except TypeError:
        return select.where(column == arguments)

    return select

def apply_filter(select, filter_):
    """
    Given a select statement from SQLAlchemy apply a filter to it. The filter should be a dictionary that maps a column
    to a list of FilterArgument. The filter arguments in that list will be logically AND together when applied to a database
    query. Within a given FilterArgument there is a 'values' property where the values are ORd together. These two operations
    allow for covering the entire logical space of queries, but you may have to be clever to do it
    """
    query = select
    for column, values in filter_.items():
        query = _apply_filter(query, column, values)
    return query

def apply_order(query, order):
    q = query
    for column, ascending in order:
        direction = column.asc() if ascending else column.desc()
        q = q.order_by(direction)
    return q

def apply_params(table, queryparams, query):
    """
    Given a table apply the queryparams to the provided query. This will return a new query that honors any
    filters, ordering, limit or offset requested by the queryparams
    """
    filter_map = map_column_names(table, queryparams.filters)
    orders = [(_get_column_by_name(table, orderarg.name), orderarg.ascending) for orderarg in queryparams.order]
    result = apply_filter(query, filter_map)
    result = apply_order(result, orders)
    result = result.offset(queryparams.offset)
    result = result.limit(queryparams.limit)
    return result

def _get_column_by_name(tables, name):
    match = None
    # Allow the user to specify either a list of tables or a single table
    try:
        iter(tables)
    except TypeError:
        tables = [tables]
    for table in tables:
        try:
            columns = table.columns
        except AttributeError:
            # This means we're dealing with an alias or a column itself
            columns = [table]
        for column in columns:
            if column.name == name:
                if match is not None:
                    raise Exception("Ambiguous column reference '{}'. It matches both {} and {}".format(name, match, column))
                else:
                    match = column
    return match

def map_column_names(tables, _filter):
    _mapped = {}
    for column_name, values in _filter.items():
        column = _get_column_by_name(tables, column_name)
        if column is None:
            raise Exception(("Unrecognized column reference '{}'."
                " None of the tables provided have a column by that name").format(column_name))
        _mapped[column] = values

    return _mapped

def remap_filter(filters, remap):
    results = filters.copy()
    for k, v in remap.items():
        try:
            results[v] = results[k]
            del results[k]
        except KeyError:
            pass
    return results

def format_filter(filters, formatter):
    return {key: formatter.get(key, lambda x: x)(value) for key, value in filters.items()}

def map_and_filter(columns, filters, query):
    """
    A helper function for combining the two steps necessary to apply query filters. This
    calls `map_column_names` with the provided columns and filters and then sends the results
    of that call to `apply_filter` so that it modifies the provided query and returns the
    modified query. The modified query will have applied the filters
    """
    filter_map = map_column_names(columns, filters)
    return apply_filter(query, filter_map)
