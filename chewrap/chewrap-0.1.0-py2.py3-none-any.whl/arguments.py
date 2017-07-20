"""Utilities for accessing the argument data for CheWrap.

All of CheWrap's possible arguments are stored in ../data/arguments.json.
chewrap.arguments provides interfaces for accessing this data.
"""

import json
import os

# We cache the parsed arguments in a module variable to avoid having to parse
# JSON & open files every time a function from this module is called.
_parsed_arguments = None


def _make_parsed_arguments():
    """Parses & caches the global JSON representation of the arguments."""

    global _parsed_arguments

    file_dir = os.path.dirname(__file__)
    with open(os.path.join(file_dir, 'arguments.json')) as f:
        _parsed_arguments = json.load(f)


def get_arguments():
    """Returns the parsed JSON representation of the arguments."""

    if _parsed_arguments is None:
        _make_parsed_arguments()

    return _parsed_arguments


def get_environment_vars():
    """Returns a list containing all the arguments which change environment
    variables."""

    args = get_arguments()
    environment_vars = []

    for key, val in args.items():
        if val['type'] == 'env':
            environment_vars.append(key)

    return environment_vars


def get_bind_mounts():
    """Returns a list containing all the arguments which change bind mounts."""

    args = get_arguments()
    bind_mounts = []

    for key, val in args.items():
        if val['type'] == 'bindmount':
            bind_mounts.append(key)

    return bind_mounts


def sort_args_key(string):
    """Strips hyphens from the left & replaces other hyphens with underscores.

    Used in conjunction with Python's 'sorted' function to sort arguments.
    """

    string = string.lstrip('-')
    string = string.replace('-', '_')
    return string
