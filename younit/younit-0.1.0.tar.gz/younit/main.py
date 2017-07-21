'''
the main module where the helpers are defined
'''

import signal
import unittest
import asyncio
from unittest.mock import MagicMock


class TestHang(Exception):
    pass


def test_name(func):
    '''
    A decorator that prints the test name before
    starting a test.

    Convenient if you want to separate the output of
    different tests.

    Usage::

        class MyTestCase(unittest.TestCase):
            @test_name
            def test_this(self):
                print("im testing this")

            @test_name
            def test_that(self):
                print("im testing that")

    '''
    def inner(*args, **kwargs):
        print("\n******** STARTING TEST: {} *********".format(func.__name__))
        return func(*args, **kwargs)
    return inner


def _test_hang_handler(signum, frame):
    raise TestHang


def test_hang_alarm(func):
    '''
    A decorator that sets an alarm of 1 second before
    starting any test.

    If a test takes longer than 1 second, a :class:`TestHang`
    exception is raised.

    If a test takes less than 1 second, the alarm is cancelled.

    Usage::

        class MyTestCase(unittest.TestCase):

            @test_hang_alarm
            def test_this(self):
                time.sleep(3)

    '''
    def inner(*args, **kwargs):
        signal.signal(signal.SIGALRM, _test_hang_handler)
        signal.alarm(1)
        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)

    return inner


def set_test_hang_alarm(func):
    '''
    A decorator that sets an alarm of 1 second before
    starting any test.

    If a test takes longer than 1 second, a :class:`TestHang`
    exception is raised.

    Should be used during set up and in conjunction with
    :func:`clear_test_hang_alarm` during tear down.

    Usage::

        class MyTestCase(unittest.TestCase):
            @set_test_hang_alarm
            def setUp(self):
                pass

            @clear_test_hang_alarm
            def tearDown(self):
                pass
    '''

    def inner(*args, **kwargs):
        signal.signal(signal.SIGALRM, _test_hang_handler)
        signal.alarm(1)
        return func(*args, **kwargs)
    return inner


def clear_test_hang_alarm(func):
    '''
    A decorator that resets an alarm set by :func:`set_test_hang_alarm`

    Should be used during tear down and in conjunction with
    :func:`set_test_hang_alarm` during set up.

    Usage::

        class MyTestCase(unittest.TestCase):
            @set_test_hang_alarm
            def setUp(self):
                pass

            @clear_test_hang_alarm
            def tearDown(self):
                pass
    '''
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)
    return inner


def close_all_threads(func):
    '''
    A decorator that closes any threads that are created
    as part of running a test.

    To use, ensure your threads are able to be closed by
    invoking a ``close()`` method on an object related to the
    thread. Then add the object to the ``self.threads_to_close``
    list.


    Usage::

        class MyTestCase(unittest.TestCase):
            def setUp(self):
                self.threads_to_close = []
                x = start_a_new_thread()
                #x is an object with a close() method
                #that closes the thread
                self.threads_to_close.append(x)

            @close_all_threads
            def test_this(self):
                y = start_a_new_thread()
                self.threads_to_close.append(y)
    '''
    def inner(self):
        try:
            return func(self)
        finally:
            [x.close() for x in self.threads_to_close]

    return inner


def asyncio_test(func):
    '''
    A decorator that runs a test as a coroutine including
    any set up and tear down coroutines.

    Usage::

        class MyTestCase(unittest.TestCase):
            async def async_setUp(self):
                pass

            async def async_tearDown(self):
                pass

            @asyncio_test
            async def test_this(self):
                pass

    '''
    def inner(self):
        async def run(self, *args, **kwargs):
            await self.async_setUp()

            try:
                return await func(self, *args, **kwargs)
            finally:
                await self.async_tearDown()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(True)

        try:
            self.loop.run_until_complete(run(self))
        finally:
            self.loop.close()

    return inner


def AsyncMock(*args, **kwargs):
    '''
    A function that can be used to mock a coroutine.

    Returns a coroutine function with a mock attribute.
    The mock attribute is a :class:`unittest.mock.MagicMock` object that records
    usage.


    Usage::

        class MyTestCase(unittest.TestCase):
            async def async_setUp(self):
                pass

            async def async_tearDown(self):
                pass

            @asyncio_test
            async def test_this(self):
                x = AsyncMock()
                await x()
                x.mock.assert_called_once()
    '''

    # thanks to miguel grinberg for this
    # https://blog.miguelgrinberg.com/post/unit-testing-asyncio-code

    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro
