# -*-: coding utf-8 -*-
""" Bluetooth setup utilities. """

import getpass
import os
import subprocess
import time

from .os_helpers import execute_command


class Bluetooth:
    """ Bluetooth setup utilities. """

    @staticmethod
    def setup():
        print("Setting up Bluetooth")
