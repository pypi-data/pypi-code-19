#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test script for virtual buffered lcd"""
import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import buffered as lcd  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA
from charlcd.handler import Handler # NOQA

GPIO.setmode(GPIO.BCM)


def demo1():
    """demo: send message to handler"""
    i2c_20x4 = I2C(0x3b, 1)
    i2c_20x4.pins = {
        'RS': 6,
        'E': 4,
        'E2': None,
        'DB4': 0,
        'DB5': 1,
        'DB6': 2,
        'DB7': 3
    }

    lcd_1 = lcd.CharLCD(20, 4, i2c_20x4)
    lcd_1.init()

    message = {
        'protocol': 'iot:1',
        'node': 'computer',
        'chip_id': 'd45656b45afb58b1f0a46',
        'event': 'lcd.content',
        'parameters': {
            'content': [
                '12345678901234567890',
                'abcdefghijklmnopqrst',
                '12345678901234567890',
                'abcdefghijklmnopqrst',
            ]
        },
        'targets': [
            'ALL'
        ]
    }

    handler = Handler(lcd_1)
    handler.handle(message)


demo1()
