
import os, sys, datetime, traceback
import logging
sys.path.append(os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), "../Utilities"))))
from Utilities.ExtensionSilence import ExtensionSilence
from Utilities import ColoredLogging
import struct
try: 
	if not sys.platform.startswith('win'): 
		import fcntl
		import termios
except: pass
import argparse


if sys.maxsize==2**32/2-1: ARCHI="32" # SysArch = "32" if sys.maxsize==2**32/2-1 else "64"
else: ARCHI="64"


LM=None


#======================================================================	
def TestEnv(ToolName):
	global ExecPath 
#	logging.debug("EXECUTABLE CURRENT PATH:"+str(os.path.abspath("./")))
	try: 
		if ToolName is None:
			logging.info("Environment variables found.")
			return True
		elif 'ADACSYS_TOOL' in os.environ:
			if os.environ['ADACSYS_TOOL']==ToolName:
				logging.info("{0} environment variables found. AVA-Test GUI can start.".format(ToolName))
				return True
			else:
				logging.error("Wrong environment variable.\n'ADACSYS_TOOL' environment variable is not set.")
				return False
		else:
			logging.error("Command called for wrong ADACSYS tool.\n'ADACSYS_TOOL' environment variable is set to '{0}'. This tool is {1}.\n\nSet this variable to '{1}' to get it run.".format(os.environ['ADACSYS_TOOL'], ToolName))
			return False
	except: 
		logging.error(traceback.format_exc(10))

		return False


#=======================================================================
#def AVABanner(Softname, Binaryname, Description, DateTime, Version):
#	"""
#	Print the ADACSYS banner.
#	"""
#	Height, Width = GetTerminalSize(fd=1)
#	logging.debug("Start banner print")
#	print("*"*Width)
#	print(("*{0:^"+str(Width-2)+"}*").format(" "))
#	print(("*{0:^"+str(Width-2)+"}*").format("ADACSYS {0} version {1}".format(Softname, Version)))
#	print(("*{0:^"+str(Width-2)+"}*").format(" "))
#	print(("*{0:^"+str(Width-2)+"}*").format(Binaryname))
#	print(("*{0:^"+str(Width-2)+"}*").format(Description))
#	print(("*{0:^"+str(Width-2)+"}*").format(" "))
#	print(("*{0:^"+str(Width-2)+"}*").format("Compiled {0}".format(DateTime)))
#	print(("*{0:^"+str(Width-2)+"}*").format("Copyright (c) ADACSYS, 2008-2014, All Rights Reserved."))
#	print(("*{0:^"+str(Width-2)+"}*").format(" "))
#	print(("*{0:^"+str(Width-2)+"}*").format("UNPUBLISHED, LICENSED SOFTWARE."))
#	print(("*{0:^"+str(Width-2)+"}*").format("CONFIDENTIAL AND PROPRIETARY INFORMATION WHICH IS"))
#	print(("*{0:^"+str(Width-2)+"}*").format("THE PROPERTY OF ADACSYS SAS OR ITS LICENSORS."))
#	print(("*{0:^"+str(Width-2)+"}*").format(" "))
#	print("*"*Width)
#	return

#=======================================================================
#def CheckLicence(KeepToken=False, RegularCheck=False, GUI=False):
#	"""
#	return True if licence is valid, False otherwise.
#	Use LicenceManager C extension.
#	"""
#	global LM, LicenceStatus
#	
#	try: import LicenceManager
#	except: 
#		logging.error("Licence manager exception.")
#		sys.exit(1)	
#		
#	logging.info("Checking ADACSYS license...")
#	LM = LicenceManager.LicenceManager()
#	if GUI and not sys.platform.startswith('win'):
#		with ExtensionSilence(stdout="./ADACSYS_LICENSE_STDOUT.txt", stderr="./ADACSYS_LICENSE_STDERR.txt", mode='w+'):
#			Success=LM.checkAdacsys(keepToken=KeepToken, regularCheck=RegularCheck, forceCheck=False)
#			
#		try:
#			with open("./ADACSYS_LICENSE_STDOUT.txt", 'r') as StdOutFile:
#				LicenceStatus=StdOutFile.read()
#			with open("./ADACSYS_LICENSE_STDERR.txt", 'r') as StdErrFile:
#				LicenceStatus+=StdErrFile.read()
#			os.remove("./ADACSYS_LICENSE_STDOUT.txt")
#			os.remove("./ADACSYS_LICENSE_STDERR.txt")
#			print(LicenceStatus)
#		except: pass
#		return Success
#	else:
#		if not LM.checkAdacsys(keepToken=KeepToken, regularCheck=RegularCheck, forceCheck=False):
#			if GUI: LicenceStatus="No valid license found"
#			logging.error("No valid license found")
#		else:
#			logging.info("Valid license found")
#			return True
#	return False
	
#=======================================================================
def GetTerminalSize(fd=1):
	"""
	Returns height and width of current terminal. First tries to get
	size via termios.TIOCGWINSZ, then from environment. Defaults to 25
	lines x 80 columns if both methods fail.

	fd: file descriptor (default: 1=stdout)
	"""
	if sys.platform.startswith('win'): return (25, 80)
	else:
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
			os.close(fd)
		except:
			try:
				os.close(fd) # ?
				hw = (os.environ['LINES'], os.environ['COLUMNS'])
			except:  
				hw = (25, 80)
	 
		return hw
    
#===================================================================================
def ArgIsFile(FilePath):
	"""
	Test validity of file path passed as argument
	"""
	if os.path.isfile(FilePath):
		return os.path.abspath(os.path.normpath(os.path.expanduser(FilePath)))
	else:
		raise argparse.ArgumentTypeError("'{0}' does not exist or is not a file.".format(FilePath))
    
#====================================================================
def ParseOptions(LaunchFunc, Version):
	"""
	Parse argument options and do corresponding actions.
	"""
	Parser = argparse.ArgumentParser(description="GUI for AVA-Test tool.", epilog="")
	
	#------------------General command arguments-----------------
	# ARGUMENT: Server name
#	Parser.add_argument('-t', '--top', action='store', help='Path to the top VHDL file.', type=ArgIsFile, default=None)
	# ARGUMENT: Server name
#	if Version.startswith('RD') or Version.startswith('test'): 
#		Parser.add_argument('-v', '--verbose', action='store_true', help='Display debug messages.', default=False)
		
	Parser.set_defaults(func=LaunchFunc)
	Args = Parser.parse_args()
		
	return Args
	
#====================================================================
def ConfigLogging(Version, ModuleName, UseLogFile=True):
	"""
	Configure logging mode.
	"""
	LogDir=os.path.expanduser(os.path.join('~/', ModuleName+'_logs'))
	if not os.path.isdir(LogDir):
		os.makedirs(LogDir)
	#======================================================================
	if 'SYNTHESYS_LOG_LEVEL' in os.environ:
		LogLevel=os.environ['SYNTHESYS_LOG_LEVEL'].upper()
		if LogLevel=="DEBUG": # and (Version.lower().startswith("rd") or Version.lower().startswith("test")):
#			sys.argv.remove("DEBUG")
			UseLogFile=False
			LoggingMode = logging.DEBUG
		elif LogLevel=="INFO": 
#			sys.argv.remove("INFO")
			UseLogFile=False
			LoggingMode = logging.INFO
		elif LogLevel=="ERROR": 
#			sys.argv.remove("ERROR")
			UseLogFile=False
			LoggingMode = logging.ERROR
		else: 
			print("'{0}' log level not supported. 'SYNTHESYS_LOG_LEVEL' env must be [DEBUG, INFO, ERROR]".format(LogLevel))
			LoggingMode = logging.INFO
	else: 
		LoggingMode = logging.INFO
	#======================LOGGING CONFIGURATION===========================
	if 'SYNTHESYS_LOG_FILE' in os.environ:
		LogFilePath=os.environ['SYNTHESYS_LOG_FILE']
#	if UseLogFile is True: 
		ColoredLogging.SetActive(False)
		LogFile = os.path.abspath(os.path.normpath(LogFilePath))
#		logging.basicConfig(filename=LogFile, format='%(asctime)s | %(levelname)s: %(message)s', level=LoggingMode, filemode='w+') # Change to ERROR for releases
		logging.basicConfig(filename=LogFile, format='%(asctime)s | %(levelname)s: %(message)s', level=LoggingMode, filemode='w+') # Change to ERROR for releases
	else: 
		ColoredLogging.SetActive(True)
		logging.basicConfig(filename=None, format='%(levelname)s: %(message)s', level=LoggingMode) # Change to ERROR for releases
	#======================================================================
	
	
#====================================================================
def TimeStamp(Format='%Y-%m-%d_%Hh%Mm%Ss'):
	return datetime.datetime.now().strftime(Format)
#====================================================================

# ==========   START OF THE CMD INTERFACE GUI  ============
def Start(NAME, MODULE, DESCRIPTION, DATETIME, VERSION, GUI):
	"""
	Initialize command line parameters/option parsing and banner display.
	"""
	F=lambda arg: GUI.Start() # Get rid of 'arg' argument
	Args = ParseOptions(F, VERSION)
	
	try: Args.func(Args)
	except KeyboardInterrupt:
		logging.info("Keyboard Interrupt: Leave {0}.".format(MODULE))
	return True
	
