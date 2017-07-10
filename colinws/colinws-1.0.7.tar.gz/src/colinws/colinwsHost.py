#!/usr/bin/env python
#-*- coding: utf-8 -*-
#Author: Colin
#Date: 2017-01-10
#Desc: 定义一些主机相关的操作
#

import socket
import fcntl
import struct
import os
import commands

def getIPAdress(ifname='eth0'):
	'''
	利用Python socket模块 得到给定网口对应的当前主机的IP地址
	'''
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname[:15]))[20:24])

def getIPAdress2():
	'''
	利用Linux命令`ip` 得到当前主机的IP
	'''
	_, ip = commands.getstatusoutput("""echo `/sbin/ip a | grep -E "eth[0-9]$|em[0-9]$|br[0-9]$|bond[0-9]$"|grep -E '[0-9]{1,3}/[0-9]{1,2}'| awk '{print $2}'|awk -F "/" '{print $1}'  | awk -F '.' '{print $0}'`""")
	return ip
