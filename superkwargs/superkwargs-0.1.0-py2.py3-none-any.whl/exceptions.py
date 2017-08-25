#!/usr/bin/env python
# -*- coding: utf8 -*-


class SuperkwargException(Exception):
    pass


class PositionalArgsIncludedException(SuperkwargException):
    pass


class MissingRequiredKwargException(SuperkwargException):
    pass


class InvalidKwargValueException(SuperkwargException):
    pass


class KwargValueValidationException(SuperkwargException):
    pass


class WrongKwargValueTypeException(SuperkwargException):
    pass    