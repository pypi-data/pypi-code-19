import sys
import unittest
from unittest.mock import Mock, patch
import asyncio
import threading
import queue
import os

import xmlrunner
import time

import younit
from test import common
from test import unittest_utils


# @unittest.skip("skipped")
class TestNameDecorator(unittest.TestCase):
    def setUp(self):
        self.original = sys.stdout
        self.stdout_file = open('redirect.txt', 'w')
        sys.stdout = self.stdout_file

    def tearDown(self):
        sys.stdout = self.original
        self.stdout_file.close()

        expected = '\n******** STARTING TEST: test_that_name_decorator_works *********\n'
        with open('redirect.txt', 'r') as f:
            actual = f.read()

        os.remove("redirect.txt")

        self.assertEqual(expected,actual)

    @younit.test_name
    def test_that_name_decorator_works(self):
        pass

# @unittest.skip("skipped")
class TestSetClearHanging(unittest.TestCase):
    @younit.set_test_hang_alarm
    def setUp(self):
        pass

    @younit.clear_test_hang_alarm
    def tearDown(self):
        pass

    # @unittest.skip("skipped")
    def test_that_test_hangs(self):
        with self.assertRaises(younit.TestHang):
            time.sleep(2)

    # @unittest.skip("skipped")
    def test_that_test_doesnt_hang(self):
        time.sleep(0.1)

# @unittest.skip("skipped")
class TestHanging(unittest.TestCase):

    # @unittest.skip("skipped")
    @younit.test_hang_alarm
    def test_that_test_hangs(self):
        with self.assertRaises(younit.TestHang):
            time.sleep(2)

    # @unittest.skip("skipped")
    @younit.test_hang_alarm
    def test_that_test_doesnt_hang(self):
        time.sleep(0.1)



# @unittest.skip("skipped")
class TestCloseAllThreads(unittest.TestCase):

    def setUp(self):
        self.threads_to_close = []

    def tearDown(self):
        time.sleep(0.01)
        self.assertEqual(1,threading.active_count())

    @younit.close_all_threads
    def test_that_all_threads_are_closed(self):
        t = ThreadRunner()
        self.threads_to_close.append(t)
        t.start()


class AsyncioTestWithMocking(unittest.TestCase):

    async def async_setUp(self):
        self.x = younit.AsyncMock()
        await self.x()

    async def async_tearDown(self):
        await self.x()

    @younit.asyncio_test
    async def test_runs_mock(self):
        self.x.mock.assert_called_once()

class ThreadRunner(object):
    def __init__(self):
        self.q = queue.Queue()

    def start(self):
        t = threading.Thread(target=self.worker)
        t.start()

    def worker(self):
        self.q.get()


    def close(self):
        self.q.put(None)


if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
