#!/usr/bin/env python
# coding: utf-8
import datetime
import requests

# The URL of the Clowder API
CLOWDER_API_ROOT = 'http://www.clowder.io/'
CLOWDER_API_URL = CLOWDER_API_ROOT + 'api'
CLOWDER_DELETE_URL = CLOWDER_API_ROOT + 'delete'
# Allowed keys for data given
ALLOWED_KEYS = ('name', 'url', 'value', 'status', 'frequency', 'public', 'alert', 'expire')
# Required keys for all posts
REQUIRED_KEYS = ('name', )

api_key = None

# We set an extremely same timeout because we don't care
# about receiving a response
TIMEOUT = 0.1

def _validate_data(data):
    """Validates the given data and raises an error if any non-allowed keys are
    provided or any required keys are missing.

    :param data: Data to send to API
    :type data: dict
    """
    data_keys = set(data.keys())
    extra_keys = data_keys - set(ALLOWED_KEYS)
    missing_keys = set(REQUIRED_KEYS) - data_keys

    if extra_keys:
        raise ValueError(
            'Invalid data keys {!r}'.format(', '.join(extra_keys))
        )

    if missing_keys:
        raise ValueError(
            'Missing keys {!r}'.format(', '.join(missing_keys))
        )


def _send(data):
    """Send data to the Clowder API.

    :param data: Dictionary of API data
    :type data: dict
    """
    url = data.get('url', CLOWDER_API_URL)

    _validate_data(data)

    if api_key is not None:
        data['api_key'] = api_key

    if 'value' not in data:
        data['value'] = data.get('status', 1)

    if 'frequency' in data:
        data['frequency'] = _clean_frequency(data['frequency'])

    try:
        requests.post(url, data=data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pass


def ok(data):
    """Send a success signal to clowder.

    :param data: Data to be sent along (Should not include 'status')
    :type data: dict
    """
    if 'status' in data:
        raise AttributeError('Status should not be provided to okay')
    else:
        data['status'] = 1

    _send(data)


def fail(data):
    """Send a failure signal to clowder.

    :param data: Data to be sent along (Should not include 'status')
    :type data: dict
    """
    if 'status' in data:
        raise AttributeError('Status should not be provided to fail')
    else:
        data['status'] = -1

    _send(data)


def delete(name):
    """Delete the monitored service with the given name.

    :param name: A service name
    :type name: str or unicode
    """
    data = {
        'url': CLOWDER_DELETE_URL,
        'name': name
    }

    _send(data)


def submit(**kwargs):
    """Shortcut that takes an alert to evaluate and makes the appropriate API
    call based on the results.

    :param kwargs: A list of keyword arguments
    :type kwargs: dict
    """
    if 'alert' not in kwargs:
        raise ValueError('Alert required')

    if 'value' not in kwargs:
        raise ValueError('Value required')

    alert = kwargs.pop('alert')
    value = kwargs['value']

    if alert(value):
        fail(kwargs)
    else:
        ok(kwargs)


def _clean_frequency(frequency):
    """Converts a frequency value to an integer. Raises an error if an invalid
    type is given.

    :param frequency: A frequency
    :type frequency: int or datetime.timedelta
    :rtype: int
    """
    if isinstance(frequency, int):
        return frequency
    elif isinstance(frequency, datetime.timedelta):
        return int(frequency.total_seconds())

    raise ValueError('Invalid frequency {!r}'.format(frequency))
