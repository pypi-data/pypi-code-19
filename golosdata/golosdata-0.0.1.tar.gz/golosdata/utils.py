import json
import re
from typing import Union

from toolz import update_in
from funcy.colls import walk_values

from golos.amount import Amount
from golos.utils import keep_in_dict, parse_time


def typify(value: Union[dict, list, set, str]):
    """ Enhance block operation with native types.

    Typify takes a blockchain operation or dict/list/value,
    and then it parses and converts string types into native data types where appropriate.
    """
    if type(value) == dict:
        return walk_values(typify, value)

    if type(value) in [list, set]:
        return list(map(typify, value))

    if type(value) == str:
        if re.match('^\d+\.\d+ (GOLOS|GBG|GESTS)$', value):
            return keep_in_dict(dict(Amount(value)), ['amount', 'asset'])

        if re.match('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$', value):
            return parse_time(value)

    return value


def json_expand(json_op):
    """ For custom_json ops. """
    if type(json_op) == dict and 'json' in json_op:
        return update_in(json_op, ['json'], json.loads)

    return json_op
