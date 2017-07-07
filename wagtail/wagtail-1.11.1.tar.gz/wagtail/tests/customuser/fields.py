from __future__ import absolute_import, unicode_literals

import random

from django.db import models
from django.utils.six import text_type

LOWER_BOUND = -2147483648
UPPER_BOUND = 2147483647
SHIFT = 92147483647


class ConvertedValue(text_type):
    def __new__(cls, value):
        value = int(value)

        if UPPER_BOUND < value:
            display_value = value
            db_value = value - SHIFT
        else:
            db_value = value
            display_value = value + SHIFT

        self = super(ConvertedValue, cls).__new__(cls, display_value)
        self.db_value = db_value

        return self

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.db_value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.db_value == other.db_value
        return self.db_value == other

    def __hash__(self):
        return hash(self.db_value)


class ConvertedValueField(models.IntegerField):
    '''
        Roughly copied from https://github.com/django/django/blob/d6eaf7c0183cd04b78f2a55e1d60bb7e59598310/tests/custom_pk/fields.py
    '''

    def pre_save(self, instance, add):
        value = getattr(instance, self.attname, None)
        if not value:
            value = ConvertedValue(random.randint(LOWER_BOUND, UPPER_BOUND))
            setattr(instance, self.attname, value)
        return value

    def to_python(self, value):
        if not value:
            return
        if not isinstance(value, ConvertedValue):
            value = ConvertedValue(value)
        return value

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return
        return ConvertedValue(value)

    def get_db_prep_save(self, value, connection):
        if not value:
            return
        return ConvertedValue(value).db_value

    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return
        return ConvertedValue(value).db_value
