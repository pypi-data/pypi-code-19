#/usr/bin/env python3
"""pwclip init module"""
import sys
from os.path import abspath, dirname, exists, join as pjoin
# this only makes sence while i need the lib folder in the PYTHONPATH
# otherwise i need to rewrite lots of code cause i have thus libs in the
# python environment path at my workstation and do not change that =)
__lib = pjoin(dirname(__file__), 'lib')
if exists(__lib) and __lib not in sys.path:
	sys.path = [__lib] + sys.path
from pwclip.cmdline import cli, gui

def pwclip():
	"""pwclip passcrypt gui mode"""
	gui()

def ykclip():
	"""pwclip yubico gui mode"""
	gui('yk')

def pwcli():
	"""pwclip cli mode"""
	cli()
