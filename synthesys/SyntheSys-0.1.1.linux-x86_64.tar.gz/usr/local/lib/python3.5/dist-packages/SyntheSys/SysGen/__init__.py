#!/usr/bin/python


__all__=["LibManager", "PackageBuilder", "Service", "Module", "HwLib", "XmlLibManager", "LibEditor", "HDLEditor", "Constraints"]

import os, sys


BBLIBRARYPATH=os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Library", "HDL")))
HWLIBRARYPATH=os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Library", "HW")))
SWLIBRARYPATH=os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Library", "SW")))
if not os.path.isdir(BBLIBRARYPATH): 
	import logging
	logging.error("[SyntheSys.SysGen] Basic block library '{0}' not found. Please specify a correct path in the options.".format(BBLIBRARYPATH))
	sys.exit(1)
if not os.path.isdir(HWLIBRARYPATH): 
	import logging
	logging.error("[SyntheSys.SysGen] Hardware library '{0}' not found. Please specify a correct path in the options.".format(HWLIBRARYPATH))
	sys.exit(1)
if not os.path.isdir(SWLIBRARYPATH): 
	import logging
	logging.error("[SyntheSys.SysGen] Software library '{0}' not found. Please specify a correct path in the options.".format(SWLIBRARYPATH))
	sys.exit(1)
	
	





	
