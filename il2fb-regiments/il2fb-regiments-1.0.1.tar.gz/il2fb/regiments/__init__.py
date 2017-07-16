# coding: utf-8

import os

import six

if six.PY2:
    from io import open

from verboselib import get_language

from il2fb.commons import SupportedLanguages
from il2fb.commons.organization import AirForces


__here__ = os.path.dirname(os.path.abspath(__file__))
__data__ = os.path.join(__here__, 'data')


def get_data_file_path(file_name):
    return os.path.join(__data__, file_name)


class Regiment(object):

    def __init__(self, air_force, code_name):
        self.air_force = air_force
        self.code_name = str(code_name)

    def __getattr__(self, name):
        if name == 'verbose_name':
            getter = self._get_verbose_name
        elif name == 'help_text':
            getter = self._get_help_text
        else:
            raise AttributeError("%r object has no attribute %r"
                                 % (self.__class__, name))

        language = get_language()
        final_name = "{0}_{1}".format(name, language)

        if hasattr(self, final_name):
            return getattr(self, final_name)

        # Check whether language code is known
        default_language = SupportedLanguages.get_default().name
        if language not in SupportedLanguages:
            language = default_language

        # Try to get value for specified language or for default language
        value = getter(language)
        if not value and language != default_language:
            value = getter(default_language)

        # Add missing attribute to the object
        setattr(self, final_name, value)
        return value

    def _get_verbose_name(self, language):
        file_name = "regShort_{0}.properties".format(language)
        return self._get_text(file_name)

    def _get_help_text(self, language):
        file_name = "regInfo_{0}.properties".format(language)
        return self._get_text(file_name)

    def _get_text(self, file_name):
        file_path = get_data_file_path(file_name)

        with open(file_path, mode='r', encoding='cp1251') as f:
            for line in f:
                if line.startswith(self.code_name):
                    start = len(self.code_name)
                    result = line[start:].strip()

                    if six.PY3:
                        result = bytes(result, 'ascii')

                    return result.decode('unicode-escape')

        return ""

    def to_primitive(self, context=None):
        return {
            'air_force': self.air_force.to_primitive(context),
            'code_name': self.code_name,
            'verbose_name': six.text_type(self.verbose_name),
            'help_text': six.text_type(self.help_text),
        }

    def __repr__(self):
        return "<Regiment '{:}'>".format(self.code_name)


class Regiments(object):

    _cache = {}
    _file_name = 'regiments.ini'

    def __new__(cls):
        raise TypeError("'{0}' must not be instantiated".format(cls.__name__))

    @classmethod
    def get_by_code_name(cls, code_name):
        if code_name in cls._cache:
            return cls._cache[code_name]

        flight_prefixes = AirForces.get_flight_prefixes()
        flight_prefix = None
        found = False

        file_path = get_data_file_path(cls._file_name)
        with open(file_path, mode='r', encoding='cp1251') as f:

            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line in flight_prefixes:
                    flight_prefix = line
                    continue

                if line == code_name:
                    found = True
                    break

        if found and flight_prefix:
            air_force = AirForces.get_by_flight_prefix(flight_prefix)
            regiment = Regiment(air_force, code_name)
            cls._cache[code_name] = regiment
            return regiment

        raise ValueError(
            "Regiment with code name '{0}' was not found."
            .format(code_name)
        )

    @classmethod
    def filter_by_air_force(cls, air_force):
        result = []

        flight_prefixes = AirForces.get_flight_prefixes()
        found = False

        file_path = get_data_file_path(cls._file_name)
        with open(file_path, mode='r', encoding='cp1251') as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line == air_force.default_flight_prefix:
                    # Flag that proper section was found.
                    found = True
                    continue

                if found:
                    if (
                        line in flight_prefixes or
                        (line.startswith('[') and line.endswith(']'))
                    ):
                        # Next section was found. Fullstop.
                        break

                    if line in cls._cache:
                        regiment = cls._cache[line]
                    else:
                        regiment = Regiment(air_force, line)
                        cls._cache[line] = regiment

                    result.append(regiment)

        return result
