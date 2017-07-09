#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test script for wifi-direct lcd input"""
import sys
from iot_message import message
sys.path.append("../../")
from charlcd.drivers.wifi_direct import WiFi  # NOQA
from charlcd import direct as charlcd  # NOQA


def test1():
    """test 40x4 set & write"""
    msg = message.Message('node-40x4')
    drv = WiFi(msg, ['node-40x4'], ('192.168.1.255', 5053))
    lcd = charlcd.CharLCD(40, 4, drv)
    lcd.init()
    lcd.set_xy(10, 2)
    lcd.write('-Second blarg !')
    lcd.set_xy(10, 1)
    lcd.write("-second line")


def test2():
    """test stream"""
    msg = message.Message('node-40x4')
    drv = WiFi(msg, ['node-40x4'], ('192.168.1.255', 5053))
    lcd = charlcd.CharLCD(40, 4, drv)
    lcd.init()
    lcd.stream('1234567890qwertyuiopasdfghjkl')


def test3():
    """demo 3 - lcd 40x4 and write with xy"""
    msg = message.Message('node-40x4')
    drv = WiFi(msg, ['node-40x4'], ('192.168.1.255', 5053))
    lcd = charlcd.CharLCD(40, 4, drv)
    lcd.init()
    lcd.write('-First blarg1 !')
    lcd.write('-Second blarg2 !', 0, 1)
    lcd.write('-Third blarg3 !', 0, 2)
    lcd.write('-Fourth blarg4 !', 0, 3)
    lcd.write('12345678901234567890', 15, 1)
    lcd.stream('1234567890qwertyuiopasdfghjkl')


test3()
