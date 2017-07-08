"""
Utility module to fetch system information.
"""

import os
import sys
import time
import platform
import calendar
import datetime

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class SysUtils:
    """
    Utility class containing methods to fetch system information.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_epoch_time():
        """
        Returns the current epoch time.

        :return: The current epoch time.
        :rtype: int
        """

        return calendar.timegm(time.gmtime())

    @staticmethod
    def get_timestamp(ts_format="%m/%d/%Y %I:%M:%S %p"):
        """
        Get current date/time in specified format.

        :param ts_format: Format in which to return the date/time.

        :return: The datetime object in specified format.
        :rtype: datetime
        """

        return datetime.datetime.fromtimestamp(time.time()).strftime(ts_format)

    @staticmethod
    def get_timestamp_utc(ts_format="%Y-%m-%d %H:%M:%S"):
        """
        Get current UTC date/time in specified format.

        :param ts_format: Format in which to return the date/time.

        :return: The datetime object in specified format.
        :rtype: datetime
        """

        return datetime.datetime.utcfromtimestamp(time.time()).strftime(ts_format)

    @staticmethod
    def get_user_input():
        """
        Reads user input from CLI console.

        :return: The user input string.
        :rtype: str
        """

        user_input = sys.stdin.readline()
        return user_input

    @staticmethod
    def suspend_thread(delay_in_sec):
        """
        Suspends the Python thread, this method is currently executing in, for specified duration.

        :param delay_in_sec: The delay duration, in seconds.

        :return: Does not return a value.
        :rtype: None
        """

        time.sleep(delay_in_sec)

    @staticmethod
    def get_pid():
        """
        Gets Process ID of the currently executing Python process.

        :return: Does not return a value.
        :rtype: None
        """

        return os.getpid()

    @staticmethod
    def get_os():
        """
        Gets the name of the Operating System.

        :return: The OS name.
        :rtype: str
        """

        return os.name

    @staticmethod
    def get_platform():
        """
        Gets the name of the Platform.

        :return: The platform name.
        :rtype: str
        """

        return platform.system()

    @staticmethod
    def end_process(exit_code):
        """
        Ends the currently executing Python process.

        :param exit_code: The exit code to be returned to the OS.

        :return: The exit code.
        :rtype: int
        """

        sys.exit(exit_code)
