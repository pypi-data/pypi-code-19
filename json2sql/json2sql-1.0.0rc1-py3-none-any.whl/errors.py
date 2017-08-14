#!/usr/bin/env python3
# ######################################################################
# Copyright (C) 2017  Fridolin Pokorny, fridolin.pokorny@gmail.com
# This file is part of json2sql package.
# ######################################################################
"""Errors raised by json2sql (Exception hierarchy)."""


class Json2SqlError(Exception):
    """Top-level error - base class for all derived error classes."""


class UnknownStatementError(Json2SqlError):
    """Unknown statement provided for expansion."""


class ClauseError(Json2SqlError):
    """Wrong clause definition provided."""


class NoStatementError(Json2SqlError):
    """No statement provided for expansion."""


class Json2SqlInternalError(Json2SqlError):
    """Library-level error that shouldn't occur."""


class ParsingInputError(Json2SqlError):
    """Error when parsing raw JSON/YAML input."""


class InputError(Json2SqlError):
    """Error when calling json2sql routines."""
