import copy
import json
import re
import time
from collections import OrderedDict

from django.conf import settings

from configfactory.exceptions import (
    CircularInjectError,
    InjectKeyError,
    JSONEncodeError,
)

key_re = r'[a-zA-Z][(\-|\.)a-zA-Z0-9_]*'
inject_regex = re.compile(r'(?<!\$)(\$(?:{param:(%(n)s)}))'
                          % ({'n': key_re}))


def json_dumps(obj, indent=None):
    return json.dumps(obj, indent=indent)


def json_loads(s):
    try:
        return json.loads(s, object_pairs_hook=OrderedDict)
    except Exception as e:
        raise JSONEncodeError(
            'Invalid JSON: {}.'.format(e)
        )


def merge_dicts(dict1, dict2):
    """
    Merge two dictionaries.
    """
    if not isinstance(dict2, dict):
        return dict2
    result = OrderedDict()
    for k, v in dict2.items():
        if k in result and isinstance(dict1[k], dict):
            result[k] = merge_dicts(dict1[k], v)
        else:
            result[k] = copy.deepcopy(v)
    for k, v in dict1.items():
        if k not in result:
            result[k] = copy.deepcopy(v)
    return result


def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten dictionary keys.
    """
    if not isinstance(d, dict):
        return d
    items = []
    for k, v in d.items():
        new_key = sep.join([parent_key, k]) if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return OrderedDict(items)


def inject_params(
        content: str,
        params: dict,
        calls: int=0,
        raise_exception: bool=True
):
    """
    Inject params to content.
    """

    circular_threshold = 100

    if calls > circular_threshold:
        if raise_exception:
            raise CircularInjectError(
                'Circular injections detected.'
            )
        return content

    calls += 1

    def replace_param(match):
        whole, key = match.groups()
        try:
            return str(params[key])
        except KeyError:
            if raise_exception:
                raise InjectKeyError(
                    message='Injection key `%(key)s` does not exist.' % {
                        'key': key
                    },
                    key=key
                )
            return whole

    if not inject_regex.search(content):
        return content

    content = inject_regex.sub(replace_param, content)

    if inject_regex.search(content):
        return inject_params(
            content=content,
            params=params,
            calls=calls,
            raise_exception=raise_exception
        )

    return content


def inject_dict_params(
        data: dict,
        params: dict,
        flatten: bool = False,
        raise_exception: bool = True):
    """
    Inject params to dictionary.
    """

    if flatten:
        data = flatten_dict(data)

    def inject(key, value):

        if isinstance(value, str):

            search = inject_regex.search(value)
            if not search:
                return value

            whole, param_key = search.groups()
            params_value = params.get(param_key)

            value = inject_params(
                content=value,
                params=params,
                raise_exception=raise_exception
            )

            if (
                params_value is not None
                and str(params_value) == value
            ):
                return params_value

        return value

    return traverse_dict(data, callback=inject)


def traverse_dict(obj, path=None, callback=None):
    """
    Traverse through nested dictionary.
    """

    if path is None:
        path = []

    if isinstance(obj, dict):
        value = OrderedDict([
            (key, traverse_dict(value, path + [key], callback))
            for key, value in obj.items()
        ])
    elif isinstance(obj, list):
        value = [
            traverse_dict(elem, path + [[]], callback)
            for elem in obj
        ]
    else:
        value = obj

    if callback is None:
        return value
    else:
        return callback(path, value)


def cleanse_dict(d, hidden=None, substitute=None):
    """
    Hide dictionary secured data.
    """

    ret = copy.deepcopy(d)

    for k, v in d.items():
        if isinstance(v, dict):
            ret[k] = cleanse_dict(v, hidden=hidden, substitute=substitute)
        else:
            ret[k] = cleanse_value(
                key=k,
                value=v,
                hidden=hidden,
                substitute=substitute
            )
    return ret


def cleanse_value(key, value, hidden=None, substitute=None):
    """
    Hide secured data.
    """

    if hidden is None:
        hidden = getattr(settings, 'CLEANSED_HIDDEN', '')

    if isinstance(hidden, str):
        hidden = hidden.split()

    hidden_re = re.compile('|'.join(hidden), flags=re.IGNORECASE)

    if substitute is None:
        substitute = getattr(settings, 'CLEANSED_SUBSTITUTE', '*****')

    try:
        if hidden_re.search(key):
            cleansed = substitute
        else:
            if isinstance(value, dict):
                cleansed = OrderedDict([
                    (k, cleanse_value(k, v,
                                      hidden=hidden,
                                      substitute=substitute))
                    for k, v in value.items()
                ])
            else:
                cleansed = value
    except TypeError:
        cleansed = value

    return cleansed


def current_timestamp():
    return int(round(time.time() * 1000))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def settings_val(name, default=None, allow_none=False):
    """
    Get settings value.
    """
    value = getattr(settings, name, None)
    if value is None and not allow_none:
        value = default
    return value
