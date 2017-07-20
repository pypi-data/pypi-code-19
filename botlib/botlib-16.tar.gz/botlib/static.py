# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" static definitions. """

import logging
import os
import re

ERASE_LINE = '\033[2K'
BOLD = '\033[1m'
GRAY = '\033[99m'
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
BLA = '\033[95m'
ENDC = '\033[0m'

colors = {
    "ERASE_LINE": ERASE_LINE,
    "BOLD": BOLD,
    "RED": RED,
    "YELLOW": YELLOW,
    "GREEN": GREEN,
    "BLUE": BLUE,
    "BLA": BLA,
    "ENDC": ENDC
}

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

year_formats = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
]
timere = re.compile('(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)')
bdmonths = ['Bo', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthint = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}

dirmask = 0o700
filemask = 0o600

nodict_types = [list, str, int, float, bool, None]
basic_types = [dict, list, str, int, float, bool, None]

resume = {}
histfile = os.path.expanduser("~/.botlib/history")

headertxt = '''# this is an BOTLIB file, %s
#
# the bot can edit this file !!

'''
