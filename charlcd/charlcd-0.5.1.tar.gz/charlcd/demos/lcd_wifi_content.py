#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test script for wifi-content lcd input"""
import sys
from iot_message import message
sys.path.append("../../")
from charlcd.drivers.wifi_content import WiFi  # NOQA
from charlcd import buffered as charlcd  # NOQA


def test1():
    """test flush"""
    msg = message.Message('node-40x4')
    drv = WiFi(msg, ['node-40x4'], ('192.168.1.255', 5053))
    lcd = charlcd.CharLCD(40, 4, drv)
    lcd.init()
    lcd.write('-  Blarg !')
    lcd.write('-   Grarg !', 0, 1)
    lcd.write('-    ALIVE  !!!!', 0, 2)
    lcd.flush()

    lcd.write('/* ', 19, 0)
    lcd.write('|*|', 19, 1)
    lcd.write(' */', 19, 2)

    lcd.flush()


test1()
