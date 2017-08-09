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


class Unit:

    def __init__(self, symbol, name, factor_to_cmd):
        self._symbol = symbol
        self._name = name
        self._factor_to_cmd = factor_to_cmd

    @property
    def symbol(self):
        return self._symbol

    def match_symbol(self, symbol):
        return symbol.strip().upper() == self._symbol

    def to_CMD(self, value):
        return value * self._factor_to_cmd

    def from_CMD(self, value):
        return value / self._factor_to_cmd

    def __repr__(self):
        return self._symbol


UNITS = [
    Unit("CFS", "cubic feet per second", 2446.575),
    Unit("CMD", "cubic meters per day", 1.),
    Unit("CMH", "cubic meters per hour", 24),
    Unit("CMS", "cubic meters per second", 86400),
    Unit("GPM", "gallons per minute", 5.45),
    Unit("LPS", "liters per second", 86.4),
    Unit("MGD", "millions of gallon per day", 378.541),
    Unit("MLD", "millions of liter per day", 1000)
]

def unit_by_name(symbol):
    for any_unit in UNITS:
        if any_unit.match_symbol(symbol):
            return any_unit
    raise ValueError("Unknown unit '%s'" % name)

setattr(Unit, "by_name", staticmethod(unit_by_name))

for each_unit in UNITS:
    setattr(Unit, each_unit.symbol.upper(), each_unit)


class Rate:

    ERROR_INVALID_RATE = "Rate cannot be negative, but found (value={})"

    def __init__(self, value, unit=None):
        if value < 0:
            message = self.ERROR_INVALID_RATE.format(value)
            raise ValueError(message)
        self._value = value
        self._unit = unit or Unit.LPS

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self._unit

    def convert_to(self, new_unit):
        cmd = self._unit.to_CMD(self._value)
        converted = new_unit.from_CMD(cmd)
        return Rate(converted, new_unit)


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

    @property
    def unit(self):
        if len(self._observations) == 0:
            return None
        return self._observations[0].rate.unit

    def convert_to(self, unit):
        observations = []
        for each_observation in self._observations:
            observations.append(
                Observation(
                    each_observation.rate.convert_to(unit),
                    each_observation.time))
        return Flow(self.water_body,
                    observations,
                    self._start_date,
                    self._user_name)

    def contains_only_values_smaller_than(self, threshold):
        return all(o.rate.value < threshold for o in self._observations)
