#/usr/bin/env python3
"""pwclip init module"""
import sys
from os.path import abspath, dirname, exists
# this only makes sence while i need the lib folder in the PYTHONPATH
# otherwise i need to rewrite lots of code cause i have thus libs in the
# python environment path at my workstation and do not change that =)
__lib = '%s/lib'%abspath(dirname(__file__))
if exists(__lib) and __lib not in sys.path:
	sys.path = [__lib] + sys.path
from colortext import abort, fatal
from pwclip.cmdline import cli, gui

def ykclip():
	"""yubi mode pwclip gui mode"""
	try:
		gui('yk')
	except (RuntimeError, KeyboardInterrupt):
		exit(1)

def pwclip():
	"""pwclip gui mode"""
	try:
		gui()
	except (RuntimeError, KeyboardInterrupt):
		exit(1)
	
def pwcli():
	"""pwclip cli mode"""
	try:
		cli()
	except RuntimeError as err:
		fatal(err)
	except KeyboardInterrupt:
		abort()
