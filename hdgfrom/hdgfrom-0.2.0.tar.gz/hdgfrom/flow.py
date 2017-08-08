#
# hdg-from -- Generate HDG files for GEMSS
#
# Copyright (C) 2017 Di WU
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the MIT license. See the LICENSE file for details.
#

# Compatibility with Pyhton 2.7
from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime


class Rate:

    ERROR_INVALID_RATE = "Rate cannot be negative, but found (value={})"

    def __init__(self, value):
        if value < 0:
            message = self.ERROR_INVALID_RATE.format(value)
            raise ValueError(message)

        self._value = value

    @property
    def value(self):
        return self._value


class Observation:

    def __init__(self, rate, time):
        self._rate = rate
        self._time = time

    @property
    def rate(self):
        return self._rate

    @property
    def time(self):
        return self._time


class Flow:

    DEFAULT_USER_NAME = "Unknown"
    DEFAULT_WATER_BODY = "Unknown"

    def __init__(self, water_body=None, observations=[], start_date=None, user_name=None):
        self._water_body = water_body or self.DEFAULT_WATER_BODY
        self._observations = observations
        self._start_date = start_date or datetime(2017, 1, 1, 12)
        self._user_name = user_name or self.DEFAULT_USER_NAME

    @property
    def water_body(self):
        return self._water_body

    @water_body.setter
    def water_body(self, water_body):
        self._water_body = water_body

    @property
    def observations(self):
        return self._observations

    def rate_at(self, time):
        return None

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, new_date):
        self._start_date = new_date

    @property
    def end_date(self):
        return self._start_date + self._observations[-1].time

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        self._user_name = user_name
