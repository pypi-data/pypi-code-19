#/usr/bin/env python3
"""pwclip init module"""
import sys

from os import environ

from os.path import abspath, dirname

# this only makes sence while i need the lib folder in the PYTHONPATH
# otherwise i need to rewrite many code in comparison to how i need it
# to be able to change things more easily and work on the code
__lib = '%s/lib'%abspath(dirname(__file__))
if __lib not in sys.path:
	sys.path = [__lib] + sys.path

from colortext import abort, fatal

from pwclip.cmdline import cli

def pwclipper():
	"""pwclip wrapper function"""
	try:
		cli()
	except RuntimeError as err:
		fatal(err)
	except KeyboardInterrupt:
		abort()
