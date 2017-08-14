#!/usr/bin/env python


import logging
log = logging.getLogger('prospecting.errors')


class ProspectingException(Exception):
    """Base class for API integration exceptions"""
    pass


class BadInputError(ProspectingException):
    """Raised when input not of type(pd.DataFrame())"""

    def __init__(self):
        log.error('BadInputError. Input must be of type(pd.DataFrame())')
        log.info('No column names in headerrow. Add columns to sheet or pass headerrow=None.')
        log.info('Check self.data for malformed response (no columns set).')


class TooManyMetricsError(ProspectingException):
    """Raised when too many metrics requested in AnalyticsApi"""

    def __init__(self, metrics_count):
        log.error('Too many metrics. Max possible is 10, '
                  'number provided is: {0}'.format(metrics_count))


class TooManyDimensionsError(ProspectingException):
    """Raised when too many dimensions requested in AnalyticsApi"""

    def __init__(self, dimensions_count):
        log.error('Too many dimensions. Max possible is 7, '
                  'number provided is: {0}'.format(dimensions_count))
