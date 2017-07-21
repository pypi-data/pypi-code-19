""":mod:`util` module contains utility functions for :mod:`latest` package.


"""

from os import linesep as ls
import os.path
import json


def is_scalar(obj):
    return isinstance(obj, (bool, int, float, complex, str))


def is_vector(obj):
    return isinstance(obj, (set, frozenset, tuple, list)) and (not is_scalar(obj))


def is_tensor(obj):
    return (not is_scalar(obj)) and (not is_vector(obj))


def path(location):
    return os.path.abspath(os.path.expanduser(location))


def select(data, path, sep='/'):
    out = data
    if path:
        for key in path.strip(sep).split(sep):
            out = out[key]
    return out


def getopt(parser, section, key, default):
    try:
        if hasattr(parser, '__getitem__'):
            return parser[section][key]
        else:
            return parser.get(section, key)
    except:
        return default


def get_supported_data_fmts():
    return ('json', 'yaml', 'yml',)


def guess_data_fmt(filename, default):
    guess = os.path.splitext(filename)[-1].strip('.').lower()
    return guess if guess in get_supported_data_fmts() else default


def load_json(filename):
    with open(filename, 'r') as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise ValueError('Error parsing json data file:' + ls + str(e))


def load_yaml(filename):
    with open(filename, 'r') as f:
        try:
            import yaml
            return yaml.load(f)
        except ImportError as e:
            raise ImportError(str(e) + ls + 'You need to install pyyaml!' + ls + 'Try:' + ls + '   $ pip install pyyaml')
        except yaml.YAMLError as e:
            raise ValueError('Error parsing yaml data file!' + ls + str(e))


def load_data(filename, data_fmt, default_data_fmt):

    data_fmt = data_fmt.lower() if data_fmt is not None else guess_data_fmt(filename, default_data_fmt)

    if data_fmt in ('json',):
        return load_json(filename)
    elif data_fmt in ('yaml', 'yml',):
        return load_yaml(filename)
    else:
        raise ValueError(data_fmt + ' format not supported!')

    return





