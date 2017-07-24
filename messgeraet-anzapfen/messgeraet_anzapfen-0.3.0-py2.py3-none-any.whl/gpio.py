#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    COPYRIGHT (C) 2016 by Sebastian Stigler

    NAME
        gpio.py -- gpio dummy

    DESCRIPTION
        This module will be used if the ``RPi.GPIO`` is not available.
        The functions will only create a logmessage.

    FIRST RELEASE
        2016-05-31  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""

import logging

_logger = logging.getLogger(__name__)

BOARD = 'BOARD'
BCM = 'BCM'
OUT = 'OUT'
LOW = 'LOW'
HIGH = 'HIGH'


def setmode(mode):
    """Set the pin mode"""
    _logger.warning('Mode is set to {mode}'.format(mode=mode))


def setup(pin, direction, pull=None):
    """Set the pin direction"""
    _logger.warning('Pin {pin} is configured as {direction}PUT'.format(
        pin=pin, direction=direction))


def setwarnings(state):
    """Set warnings on or off"""
    _logger.warning('Warnings are set to {state}'.format(state=repr(state)))


def output(pin, state):
    """Set pin state"""
    _logger.warning('Pin {pin} is set to {state}'.format(pin=pin, state=state))

# vim: ft=python ts=4 sta sw=4 et ai
