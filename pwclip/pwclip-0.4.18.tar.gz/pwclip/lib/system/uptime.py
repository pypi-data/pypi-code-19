#!/usr/bin/env python3

from system.fileage import fileage

def uptime():
	with open('/proc/uptime', 'r') as utf:
		return int(utf.read().split(' ')[0].split('.')[0])

def wittime(target):
	return (uptime() > fileage(target))
