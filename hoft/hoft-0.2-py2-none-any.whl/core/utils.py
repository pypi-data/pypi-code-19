#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# HOFT utils.
# @module hoft.core.utils
# @version 0.1
# @copyright (c) 2017-present Francis Horsman.

from collections import namedtuple

PositionalError = namedtuple('PositionalError', ('error', 'index', 'value', 'func_name', 'func'))

KeywordError = namedtuple('KeywordError', ('error', 'value', 'func_name', 'func'))

IGNORE = None

__all__ = [
]


def get_func_name(f):
    try:
        return f.func_name
    except Exception as e:  # NOQA
        # Unable to determine target function validator:
        return None


def raise_exc(exc, on_error=None, errors=None, fail_fast=False, force=False):
    if fail_fast or force:
        if on_error is not None:
            if isinstance(on_error, Exception):
                # Raise the custom exception if required:
                raise on_error(exc, errors)
            elif callable(on_error):
                # Call the user-defined function as required, it is up to it to raise an exception.
                on_error(exc, errors)
        else:
            # Add the errors to the exception and raise it:
            exc._errors_ = errors
            raise exc


def conditionally_raise_exc(exc, on_error=None, errors=None, fail_fast=False):
    raise_exc(
        exc=exc,
        on_error=on_error,
        errors=errors,
        fail_fast=fail_fast,
        force=False,
    )
