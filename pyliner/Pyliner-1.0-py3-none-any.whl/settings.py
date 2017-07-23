# -*- coding: utf-8 -*-

"""Formatting symbols for parsing phrases"""
SENTINEL = "%SENTINEL%"  # Temporary substitute for replacements
ESCAPE_CHAR = "\\"

OPEN_CHOOSE = "<"  # Must be a single char
CLOSE_CHOOSE = ">"  # Must be a single char
SPLIT_CHOOSE = "|"

OPEN_OMIT = "{"  # single char
CLOSE_OMIT = "}"  #single char

OPEN_UPPER = r"\[upper]"
CLOSE_UPPER = r"\[/upper]"

OPEN_LOWER = r"\[lower]"
CLOSE_LOWER = r"\[/lower]"

OPEN_SENTENCE = r"\[sencase]"
CLOSE_SENTENCE = r"\[/sencase]"

OPEN_STARTCASE = r"\[startcase]"
CLOSE_STARTCASE = r"\[/startcase]"
