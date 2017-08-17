# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Matcher module
"""

import re

from .utils import is_unicode


def anywhere(pattern):
    """ Faster version of partial 'in'
    """
    def _anywhere(value):
        """ Faster version of partial 'in'
        """
        return pattern in value
    return _anywhere


def starts_with(pattern):
    """ Faster version of partial 'startswith'
    """
    def _starts_with(value):
        """ Faster version of partial 'startswith'
        """
        return value.startswith(pattern)
    return _starts_with


def ends_with(pattern):
    """ Faster version of partial 'endswith'
    """
    def _ends_with(value):
        """ Faster version of partial 'endswith'
        """
        return value.endswith(pattern)
    return _ends_with


def equals(pattern):
    """ Faster version of partial '=='
    """
    def _equals(value):
        """ Faster version of partial '=='
        """
        return pattern == value
    return _equals


MATCHERS = {
    'anywhere': anywhere,
    'starts_with': starts_with,
    'ends_with': ends_with,
    'equals': equals
}


class Matcher(object):
    """ Fast regex-like matcher
    """

    def __init__(self, patterns):
        self.patterns = patterns
        self.insensitives_string_patterns = []
        self.sensitives_string_patterns = []
        self.regex_patterns = []

        self._prepare(patterns)

    def _prepare(self, patterns):
        """ Prepare all the patterns
        """
        for pattern in patterns:

            pattern_type = pattern['type']
            value = pattern['value']
            case_sensitive = pattern.get('case_sensitive', False)

            if pattern_type == 'string':
                pattern_options = pattern.get('options')

                # Get the match function name, defaulting to anywhere
                if not pattern_options:
                    match_name = 'anywhere'
                else:
                    match_name = pattern_options[0]

                if match_name not in MATCHERS.keys():
                    raise ValueError('Unknown match function {}'.format(match_name))

                # Lower the value in case of case insensitive match or
                # for not lower case pattern, it would never match
                if case_sensitive is False:
                    value = value.lower()

                match = MATCHERS[match_name](value)

                if case_sensitive is False:
                    self.insensitives_string_patterns.append(match)
                else:
                    self.sensitives_string_patterns.append(match)

            elif pattern_type == 'regexp':
                if case_sensitive:
                    flags = 0
                else:
                    flags = re.IGNORECASE

                if 'multiline' in pattern.get('options', []):
                    flags = re.MULTILINE | flags

                self.regex_patterns.append(re.compile(value, flags))
            else:
                raise ValueError('Unknown pattern type %s', pattern_type)

    def match(self, value):
        """ Check if string value match one of the string or regex pattern the fastest
        way possible. Accept python 2 str, unicode and python 3 bytes and str.
        """

        # Correct encoding if possible and needed
        if not is_unicode(value):
            value = value.decode('utf-8', errors='replace')

        # Match case sensitive values
        for string_match in self.sensitives_string_patterns:
            if string_match(value):
                return True

        if self.insensitives_string_patterns:
            insensitive_value = value.lower()

            # Match case insensitive values
            for string_match in self.insensitives_string_patterns:
                if string_match(insensitive_value):
                    return True

        # Match regexes
        for pattern_regex in self.regex_patterns:
            # We need to use search here because match starts at the beginning
            # of the string
            if pattern_regex.search(value) is not None:
                return True

        return False
