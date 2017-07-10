#!/usr/bin/env python

# __author__ = "Eric Allen Youngson"
# __email__ = "eric@successionecological.com"
# __copyright__ = "Copyright 2015, Succession Ecological Services"
# __license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the Google
    calendar API """


import sys
sys.path.append('../geepal')

from googleapiclient.discovery import build
from googleapiclient.http import HttpMock

import pytz
import datetime as dt
import types as tp
import re

import get_events as ge
import pprint as pp

import pytest


pattern = re.compile("(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")


def test_relative_datetime():
    """ This function tests the datatypes of the inut & output of the =
        get_events.relative_datetime function. """

    relPeriods = ['today', 'tomorrow', 'yesterday']

    all_tzs = pytz.all_timezones
    for all_tz in all_tzs:
        for relPeriod in relPeriods:
            datetimeObj = ge.relative_datetime(relPeriod=relPeriod, tz=all_tz)
            assert type(relPeriod) is str
            assert isinstance(datetimeObj, dt.datetime)


def test_midnight_datetime():
    """ This function tests the datatypes of the output of the
        get_events.midnight_datetime function. """

    dtime = dt.datetime(minute=49, hour=7, second=23, microsecond=45,
                                                     year=2017, month=2, day=5)
    midnightDt = ge.midnight_datetime(dtime)

    assert midnightDt.minute == midnightDt.hour == midnightDt.second == midnightDt.microsecond == 0


class TestEventRange:
    """ This function tests a new version of the event_range() function to
        allow two modes; one for relative date-range specification in plain-
        English, or a specified date range passed directly to the function.

    Args:

    Returns:
    """

    def test_returns_tuple(self):
        """  """

        options = ['day', 'week', 'month', 'year']
        for option in options:
            evStart_evEnd = ge.event_range(relRange=option)
            assert type(evStart_evEnd) is tuple
 
    def test_tuple_contains_strings(self):
        """  """

        options = ['day', 'week', 'month', 'year']
        for option in options:
            evStart_evEnd = ge.event_range()
            (isoPeriodBegin, isoPeriodEnd) = evStart_evEnd
            assert type(isoPeriodBegin) == str

    def test_date_strings_match_pattern(self):
        """  """

        options = ['day', 'week', 'month', 'year']
        for option in options:
            evStart_evEnd = ge.event_range()
            (isoPeriodBegin, isoPeriodEnd) = evStart_evEnd
            assert pattern.match(isoPeriodBegin)
            assert pattern.match(isoPeriodEnd)
    
    def test_specific_date_range_provided(self):
        """  """

        evStart_evEnd = ge.event_range(start='2016-06-01', end='2016-06-30')
        (isoPeriodBegin, isoPeriodEnd) = evStart_evEnd
        assert pattern.match(isoPeriodBegin)
        assert pattern.match(isoPeriodEnd)

    def test_datetime_format_exception(self):
        """  """

        #with pytest.raises(Exception) as excinfo:
        evStart_evEnd = ge.event_range(start='sldkjf', end='nxowenc')
        #assert 'Date Error: Check format (iso8601)' in str(excinfo.value)
        assert Exception

        ## Can't test this statement: Raises SyntaxError: positional argument follows keyword argument
        # evStart_evEnd = ge.event_range(start='2016-06-01', '2016-06-30') 
        # assert Exception

        #with pytest.raises(Exception) as excinfo:
        evStart_evEnd = ge.event_range('2016-06-01', end='2016-06-30')
        #assert 'Period start and/or end not found' in str(excinfo.value)
        assert Exception

        #with pytest.raises(Exception) as excinfo:
        evStart_evEnd = ge.event_range(stuff='2016-06-01', end='2016-06-30')
        #assert 'Period start and/or end not found' in str(excinfo.value)
        assert Exception

        #with pytest.raises(Exception) as excinfo:
        evStart_evEnd = ge.event_range('2016-06-01', '2016-06-30')
        #assert 'Period start and/or end not found' in str(excinfo.value)
        assert Exception


# @pytest.mark.skip(reason="Unable to find suitable mocking content")
def test_get_events():
    """  """

    # Example code: https://developers.google.com/api-client-library/python/guide/mocks
    # Discovery object: https://developers.google.com/discovery/v1/reference/apis/getRest
    http = HttpMock('../geepal/calendar-discovery.json', {'status': '200'})
    api_key = 'your_api_key'
    service = build('calendar', 'v3', http=http, developerKey=api_key)

    assert service.events()

    evStart_evEnd = ('2016-02-03-00:00:00z', '2016-02-05-00:00:00z')
    calendars = {'Sunrise and sunset for Portland':
                 'i_71.63.230.104#sunrise@group.v.calendar.google.com'}
    evStartEvEnd_eventsDct = ge.get_events(service, evStart_evEnd, calendars)
     
    assert evStartEvEnd_eventsDct
