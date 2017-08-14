# -*- coding: utf-8 -*-

import maya
import pytimeparse

from timee.timee_general import Timee
from timee.timee_dt import TimeeDT
from timee.timee_duration import TimeeDuration


def parse(text, from_timezone=None):

    """
    :rtype: TimeeDT
    """

    timee_dt = None

    if from_timezone:
        timee_dt = parse_with_maya(text, timezone=from_timezone)
        return timee_dt

    else:

        for parse_method in parsing_methods():
            result = parse_method(text)

            if result is not None:
                timee_dt = result
                break

    return timee_dt


def timee_parse(text, from_timezone=None):
    return parse(text, from_timezone)


def parsing_methods():

    _parsing_methods = [
        # parse_duration,
        parse_with_maya,
        parse_2
    ]

    return _parsing_methods


def parse_duration(text):

    seconds = pytimeparse.parse(text)

    timee_duration = TimeeDuration(seconds)

    return timee_duration


def timee_parse_duration(text):
    return parse_duration(text)


def when(text, timezone=None):

    return ''


def timee_parse_point(text):

    """
    :rtype: TimeeDT
    """

    timee_dt = parse(text)

    return timee_dt


def parse_2(text):

    """
    :type text: str
    """

    if 'before' not in text:
        return None

    # 30 days before Dec 1

    parts = text.split(' before ')

    duration_string = parts[0]
    timee_duration = parse(duration_string)

    point_string = parts[1]
    timee_dt = timee_parse_point(point_string)

    result = timee_dt.subtract(timee_duration)

    return result


def parse_with_maya(text, timezone=None):

    if timezone is None:
        timezone = 'UTC'

    try:
        maya_dt = maya.when(text, timezone=timezone)
    except ValueError as e:
        print('## Maya parsing failed.')
        maya_dt = None
        pass

    if maya_dt:
        timee_dt = Timee.from_maya(maya_dt)
        return timee_dt

    return None


