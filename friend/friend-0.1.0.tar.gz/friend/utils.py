import functools as f
import os
import random
import time


class IncompleteEnvironment(RuntimeError):
    """
    An exception which is used to indicate when environment
    variables are unset.
    """
    def __init__(self, message, variables):
        """
        :param message: Error message as a string
        :param variables: A list of missing variables as strings
        """
        super(IncompleteEnvironment, self).__init__(message)
        self.variables = variables


def cached(func):
    """
    A decorator function to cache values. It uses the decorated
    function's arguments as the keys to determine if the function
    has been called previously.
    """
    cache = {}

    @f.wraps(func)
    def wrapper(*args, **kwargs):
        key = func.__name__ + str(sorted(args)) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


def retry_wait_time(attempt, cap):
    """
    Determine a retry wait time based on the number of the
    retry attempt and a cap on the wait time. The wait time
    uses an exponential backoff with a random jitter.
    The algorithm used is explained at
    https://www.awsarchitectureblog.com/2015/03/backoff.html.

    :param int attempt: The number of the attempt
    :param int cap: A cap on the wait time in milliseconds
    :returns: The number of milliseconds to wait
    :rtype: int
    """
    base = 100
    max_wait = min(cap, base * (2 ** attempt))
    return random.choice(range(0, max_wait))


def retry_ex(callback, times=3, cap=120000):
    """
    Retry a callback function if any exception is raised.

    :param function callback: The function to call
    :keyword int times: Number of times to retry on initial failure
    :keyword int cap: Maximum wait time in milliseconds
    :returns: The return value of the callback
    :raises Exception: If the callback raises an exception
    """
    for attempt in range(times + 1):
        if attempt > 0:
            time.sleep(retry_wait_time(attempt, cap) / 1000.0)
        try:
            return callback()
        except:
            if attempt == times:
                raise


def retry_bool(callback, times=3, cap=120000):
    """
    Retry a callback function if it returns False.

    :param function callback: The function to call
    :keyword int times: Number of times to retry on initial failure
    :keyword int cap: Maximum wait time in milliseconds
    :returns: The return value of the callback
    :rtype: bool
    """
    for attempt in range(times + 1):
        if attempt > 0:
            time.sleep(retry_wait_time(attempt, cap) / 1000.0)
        ret = callback()
        if ret or attempt == times:
            break
    return ret


def retryable(retryer=retry_ex, times=3, cap=120000):
    """
    A decorator to make a function retry. By default the retry
    occurs when an exception is thrown, but this may be changed
    by modifying the ``retryer`` argument.

    See also :py:func:`retry_ex` and :py:func:`retry_bool`. By
    default :py:func:`retry_ex` is used as the retry function.

    Note that the decorator must be called even if not given
    keyword arguments.

    :param function retryer: A function to handle retries
    :param int times: Number of times to retry on initial failure
    :param int cap: Maximum wait time in milliseconds

    :Example:

    ::

      @retryable()
      def can_fail():
          ....

      @retryable(retryer=retry_bool, times=10)
      def can_fail_bool():
          ....
    """
    def _retryable(func):
        @f.wraps(func)
        def wrapper(*args, **kwargs):
            return retryer(lambda: func(*args, **kwargs), times, cap)
        return wrapper
    return _retryable


def select(coll, key, value):
    """
    Given an iterable of dictionaries, return the dictionaries
    where the values at a given key match the given value.
    If the value is an iterable of objects, the function will
    consider any to be a match.

    This is especially useful when calling REST APIs which
    return arrays of JSON objects. When such a response is
    converted to a Python list of dictionaries, it may be
    easily filtered using this function.

    :param iter coll: An iterable containing dictionaries
    :param obj key: A key to search in each dictionary
    :param value: A value or iterable of values to match
    :type value: obj or iter
    :returns: A list of dictionaries matching the query
    :rtype: list

    :Example:

    ::

      dicts = [
          {'hi': 'bye'},
          {10: 2, 30: 4},
          {'hi': 'hello', 'bye': 'goodbye'},
      ]

      matches = select(dicts, 'hi', 'bye')
      # Returns [{'hi': 'bye'}]

      matches = select(dicts, 'hi', ('bye', 'hello'))
      # Returns [{'hi': 'bye'}, {'hi': 'hello', 'bye': 'goodbye'}]
    """
    if getattr(value, '__iter__', None):
        iterable = value
    else:
        iterable = [value]
    return [v for v in coll if key in v and v[key] in iterable]


def ensure_environment(variables):
    """
    Check os.environ to ensure that a given collection of
    variables has been set.

    :param variables: A collection of environment variable names
    :returns: os.environ
    :raises IncompleteEnvironment: if any variables are not set, with
        the exception's ``variables`` attribute populated with the
        missing variables
    """
    missing = [v for v in variables if v not in os.environ]
    if missing:
        formatted = ', '.join(missing)
        message = 'Environment variables not set: {}'.format(formatted)
        raise IncompleteEnvironment(message, missing)
    return os.environ
