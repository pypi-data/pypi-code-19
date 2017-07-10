#!/usr/bin/python

#-----------------------------
VERSION="1.0"
DATETIME="2014-06-25 at 18:21:47"
MODULE="YANGO"
NAME="YANGO"
DESCRIPTION="A NoC base application generator"
#-----------------------------

import os, sys, logging

#try: 
#	from gi.repository import Gtk, Gdk, GLib, Pango
#	from gi.repository.GdkPixbuf import Pixbuf, InterpType
#except ImportError: 
#	import gtk as Gtk
#	import glib as GLib
#	import pango as Pango
#	from gtk import gdk as Gdk

import datetime
import zipfile
try: import fcntl, termios, struct
except: pass
import argparse

from yango import Components
from yango import GUI
from yango import Tools

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from Utilities import BugManager

import pyInterCo
from pyInterCo.XmlLibManager import XmlLibManager



#======================================================================	
def TestEnv():
	try: 
		logging.info("Environment variables found. NoC generator GUI can start now.")
		return True
	except: 
		Dialog = Gtk.MessageDialog(None, Gtk.DIALOG_MODAL, Gtk.MESSAGE_INFO, Gtk.BUTTONS_OK, "\n{0}\n".format("The 'ADACSYS_ROOT', 'ADACSYS_VERSION' and/or 'ADACSYS_TOOL' are not set.\n\nPlease source the 'a_env_ava_soft' script, or set those variables manually."))
		Dialog.set_title("Environment variables not set")
		response = Dialog.run()
		Dialog.destroy()

		return False

#=======================================================================
def Banner(Softname, Binaryname, Description, DateTime, Version):
	"Print the ADACSYS banner."
	Height, Width = get_terminal_size(fd=1)
	logging.debug("Start banner print")
	print(( "*"*Width ))
	print(( ("*{0:^"+str(Width-2)+"}*").format(" ")))
	print(( ("*{0:^"+str(Width-2)+"}*").format("{0} version {1}".format(Softname, Version))))
	print(( ("*{0:^"+str(Width-2)+"}*").format(" ")))
	print(( ("*{0:^"+str(Width-2)+"}*").format(Binaryname)))
	print(( ("*{0:^"+str(Width-2)+"}*").format(Description)))
	print(( ("*{0:^"+str(Width-2)+"}*").format(" ")))
	print(( ("*{0:^"+str(Width-2)+"}*").format("Compiled {0}".format(DateTime))))
	print(( ("*{0:^"+str(Width-2)+"}*").format(" ")))
	print(( "*"*Width ))
	
	return True

#=======================================================================
def get_terminal_size(fd=1):
    """
    Returns height and width of current terminal. First tries to get
    size via termios.TIOCGWINSZ, then from environment. Defaults to 25
    lines x 80 columns if both methods fail.
 
    :param fd: file descriptor (default: 1=stdout)
    """
    try:
        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except:
        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except:  
            hw = (25, 80)
 
    return hw


#===================================================================================
def ArgDir(DirPath):
	"""
	Test validity of directory path passed as argument
	"""
	if os.path.isdir(DirPath):
		return os.path.normpath(os.path.abspath(DirPath))
	else:
		while(1):
			Response = input("Directory '' does not exist. Do you want to create it ? (Y/n)")
			if Response == 'Y':
				try: 
					os.makedirs(DirPath)
					return os.path.normpath(os.path.abspath(DirPath))
				except: 
					raise argparse.ArgumentTypeError("No valid output directory specified.")
					return
			elif Response == 'n':
				break;
		raise argparse.ArgumentTypeError("No output directory specified.")
		

#=======================================================================
def ShowItem(Options):
	"""
	Display on console the parameters of a given component.
	"""
	def Show(Item, ItemName):
		Item.SetFromLib(ItemName)
		print(Item)
		for Key in list(Item.Parameters.keys()):
			print(("Parameters {0}".format(Key)))
			for Param in list(Item.Parameters[Key].keys()):
				print(("{0:<.50}{1}".format(Param, Item.Parameters[Key][Param])))
		
	if Options.Application:
		for ItemName in Options.Application:
			Item=Components.App()
			Show(Item, ItemName)
	if Options.Architecture:
		for ItemName in Options.Architecture:
			Item=Components.Arch()
			Show(Item, ItemName)
	if Options.FPGA:
		for ItemName in Options.FPGA:
			Item=Components.FPGA()
			Show(Item, ItemName)
	if Options.Port:
		for ItemName in Options.Port:
			Item=Components.Port()
			Show(Item, ItemName)
	if Options.NoC:
		for ItemName in Options.NoC:
			Item=Components.NoC()
			Show(Item, ItemName)
	if Options.IP:
		for ItemName in Options.IP:
			Item=Components.IP()
			Show(Item, ItemName)
	sys.exit(0)

#=======================================================================
def ShowGUI(Options):
	"""
	Initialize and launch GUI.
	"""
	if Options.lib is None: Library=pyInterCo.BBLIBRARYPATH
	else: Library=Options.lib

	#---------------Setup components---------------------
	APP=Components.App(Library=XmlLibManager(Library), Name=Options.application, Bundle=None)
	NoC=APP.AddChild("NoC", Name="AdoCNet", FromLib=True)
	for i in range(4):
		IP=NoC.AddChild("IP", Name=None, FromLib=False)
	#----------------------------------------------------
	
	YangoGUI=Tools.InitGUI(LibraryPath=Library, Application=APP)
	
	
	YangoGUI.Start()

#=======================================================================
def Implement(Options):
	"""
	Create a App component object for each application specified.
	From it, execute the Generate methode to get all outputs files.
	"""
	if "application" in Options.__dict__:
		Application=Components.App(Library=Options.lib, Name=Options.application)
		if Application.IsInLibrary(Options.application):
			#------------------------------------------------
			def CmdSuccess():
				"""
				Current command execution succeeded: pass.
				"""
				pass
	
			#------------------------------------------------
			def CmdFailed():
				"""
				Current command execution failed: pass.
				"""
				logging.error("An error occured during implementation process: aborted.")
			#------------------------------------------------
			logging.info("YANGO: Implementation start for application '{0}'.".format(Options.application))
			Application.SetFromLib(Options.application)
			for ImplementFlow in Application.Generate(Options.output):
				if ImplementFlow!=None:
					ImplementFlow.Start(CmdSuccess, CmdFailed, StopAfterFailure=True)
		else:
			logging.error("No application named '{0}' available in library.".format(Options.application))
	else:
		logging.error("Please specify an application name.")
	sys.exit(0)
	
#=======================================================================
def EvalModule(Options):
	"""
	Implement specified module on target architecture and fetch resource usage.
	"""
	ModName  = Options.module
	Archi    = Options.architecture
	ParamVal = Options.parameter
	
	
	
	return 
	
#=======================================================================
def ParseOptions():
	"""
	Parse argument options and do corresponding actions.
	"""
	# Display the banner on terminal
	Banner(MODULE, MODULE+".exe", "Yet Another NoC Generator and Optimizer", DATETIME, VERSION)
	Parser = argparse.ArgumentParser(description='Generate HDL and binaries of NoC based applications.', epilog="If no arguments are specified, the GUI will popup.")
	
	#------------------General command arguments-------------------------------------
	# ARGUMENT: Launch the GUI
	Parser.add_argument('-g', '--gui', action='store_true', help='If the GUI should be open (ignoring specified options).', default=False)
	# ARGUMENT: Display version
	Parser.add_argument('--version', action='version', version="%(prog)s: version='{0}'".format(VERSION), help="Displays YANGO version.")
	
	#================================================================
	SubParsers = Parser.add_subparsers(help='YANGO Sub-commands.', dest='Sub-command')
	SubParsers.required = True
	# Create the parser for the 'Implement' command
	BuildParser = SubParsers.add_parser('implement', help='Build all files of a saved application, for a set of saved architecture.')
	# Create the parser for the 'HDL' command
	GetHDLParser = SubParsers.add_parser('hdl', help='Generate HDL sources for an item (NoC, IP or whole applications).')
	# Create the parser for the 'Show' command
	ShowParser = SubParsers.add_parser('show', help='Print item information in terminal.')
	EvalParser = SubParsers.add_parser('eval', help='Evaluate the resources used by a library module.')
	# Create the parser for the 'gui' command
	GUIParser = SubParsers.add_parser('gui', help='Launch the GUI.')
	
	#================================================================
	#------------------'Implement' command arguments----------------------------------------
	BuildParser.add_argument('-l', '--lib', metavar='LibPath', type=str, help='The path to a valid YANGO library.', default=pyInterCo.BBLIBRARYPATH)
	BuildParser.add_argument('-a', "--application", metavar='AppName', type=str, help='The saved application name.', default='NoCDesign')
	BuildParser.add_argument("-o", "--output", metavar='OutputPath', type=ArgDir, help='Path to the output folder to store the output files (sources and binaries).', default="./")
	
	#------------------'GetHDL' command arguments---------------------------------------
#	GetHDLParser.add_argument('-a', '--application', metavar='AppName', type=str, help='The name of an application saved in library.', default='NoCDesign')
#	GetHDLParser.add_argument('--NoC', metavar='NoCName', type=str, help='The name of a NoC saved in library.')
	GetHDLParser.add_argument('--module', metavar='ModuleName', type=str, help='The name of a module saved in library.', required=True)
	GetHDLParser.add_argument("-o", "--output", metavar='OutputPath', type=ArgDir, help='Path to the output folder to store the output files (sources and binaries).', default="./")
	GetHDLParser.add_argument("-p", '--parameter', metavar='ParameterAssignment', action='append', help='The name of a module saved in library.', default=[])
	
	#------------------'Show' command arguments---------------------------------------
	ShowParser.add_argument('--application', metavar='AppName', type=str, help='The name of an application saved in library.', default='NoC Design')
	ShowParser.add_argument('--noc', metavar='NoCName', type=str, help='The name of a NoC saved in library.')
	ShowParser.add_argument('--module', metavar='ModuleName', type=str, help='The name of a module saved in library.')
	ShowParser.add_argument('--architecture', metavar='ArchName', type=str, help='The name of an Architecture saved in library.')
	ShowParser.add_argument('--fpga', metavar='FPGAName', type=str, help='The name of a FPGA saved in library.')
	ShowParser.add_argument('--port', metavar='PortName', type=str, help='The name of a Port saved in library.')
	ShowParser.add_argument('-l', '--lib', metavar='LibPath', type=str, help='The path to a valid YANGO library.', default=pyInterCo.BBLIBRARYPATH)
	
	#------------------'GUI' command arguments---------------------------------------
	GUIParser.add_argument('-l', '--lib', metavar='LibPath', type=str, help='The path to a valid YANGO library.', default=pyInterCo.BBLIBRARYPATH)
	GUIParser.add_argument('-a', '--application', metavar='AppName', type=str, help='The name of an application saved in library.', default='NoCDesign')
	
	#------------------'eval' command arguments---------------------------------------
	EvalParser.add_argument('-m', '--module', metavar='ModuleName', type=str, help='The name of a module saved in library.')
	EvalParser.add_argument('--architecture', metavar='ArchiName', type=str, help='The name of an Architecture saved in library.')
	EvalParser.add_argument("-p", '--parameter', metavar='ParamValue', action='append', help='A coma sparated liste of Parameter Name and value pairs (Param:Value).', default=[])
	
	BuildParser.set_defaults( func=Implement)
	GetHDLParser.set_defaults(func=Tools.GetHDL)
	ShowParser.set_defaults(  func=ShowItem)
	GUIParser.set_defaults(   func=ShowGUI)
	EvalParser.set_defaults(  func=EvalModule)
	
	Opt = Parser.parse_args()
	Opt.func(Opt)
	return Opt
	
	
# ====================  START OF THE YANGO APPLICATION  =====================
if (__name__ == "__main__"):
	# It's a standalone module
	Options = ParseOptions()
	
	logging.shutdown()
	sys.exit(0)
