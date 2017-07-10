
import contextlib
import sys, os, re
import logging
import platform
import fileinput
import glob
import types
import shutil
#from SyntheSys.Utilities.RemoteOperations 
from Utilities import RemoteOperations

#------------------SYSTEM RECOGNITION--------------------
if sys.maxsize > 2**32: ARCHI="64" # SysArch = "32" if sys.maxsize==2**32/2-1 else "64"
else: ARCHI="32"
if sys.platform.startswith('win'): 
	OS="win";OS_CLASS="windows";OS_FULL_NAME=platform.platform()
else: OS="lin";OS_CLASS="linux";OS_FULL_NAME="_".join(platform.linux_distribution()+(ARCHI,))
#------------------SYSTEM RECOGNITION--------------------

#======================================================
# SYNTHESYS ERROR HANDLER
class SyntheSysError(Exception):
	def __init__(self, Message="SyntheSys Error"):
		self.Message = Message
	def __str__(self):
		return repr(self.Message)
		
#======================================================
def GetSysInfo():
	global ARCHI, OS, OS_CLASS, OS_FULL_NAME
	return ARCHI, OS, OS_CLASS, OS_FULL_NAME
#===========================================================
# USAGE:
#	with Silence():
#		foo()
#
#===========================================================
class DummyFile(object):
	def write(self, x): pass

#===========================================================
@contextlib.contextmanager
def Silence(FD):
	SavedFD = FD
	FD = DummyFile()
	yield
	FD = SavedFD

#===========================================================
class cd:
	"""
	Context manager for changing the current working directory
	"""
	#---------------------------------------------------
	def __init__(self, newPath):
		self.newPath = newPath
	#---------------------------------------------------
	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)
	#---------------------------------------------------
	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)
       
#======================================================================
def ReplaceTextInFile(FileName, OldText, NewText):
	Found = False
#	print("OldText:", OldText)
	if not os.path.exists(FileName):
		raise NameError("File <{0}> cannot be found".format(FileName))
	else:
		for line in fileinput.input(FileName, inplace=True):
			if( line.count(OldText) ):
				Found = True
#				text = "\nFound: <" + line
				line = line.replace(OldText, NewText)
#				text += ("> replaced by <"+line+">")
			sys.stdout.write(line)
#	print("Found:", Found)
	return Found
	
#======================================================================
def IterFiles(SearchPaths=[], Name="*.ini"):
	"""
	Generator that yield each configuration files found in specified directories.
	"""
	for SearchPath in SearchPaths:
		for Root, Dirs, Files in os.walk(SearchPath, topdown=True):
			Template=os.path.join(Root, Name)
			MatchedFiles=glob.glob(Template)
			for FileName in MatchedFiles:
				yield os.path.join(Root, FileName)
				
				

#======================================================================
def ListModules(ModName):
	try:
		Module = __import__(ModName, globals(), locals(), [ModName.split('.')[-1]])
	except ImportError:
		return
	print(ModName)
	for Name in dir(Module):
		if type(getattr(Module, Name)) == types.ModuleType:
			ListModules('.'.join([ModName, Name]))
		
#======================================================================
def IndentationLevel(Line, TabSize=4): 
	"""
	return the indentation level of specified line.
	"""
	LineX=Line.expandtabs(TabSize)
	if LineX.isspace():
		return 0
	else:
		return int((len(LineX)-len(LineX.lstrip()))/TabSize)

#======================================================================
def NaturalSort(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)


#======================================================================
def CleanTempFiles(Path, Host=None):
	"""
	Test environment variable 'SYNTHESYS_KEEP_ALL' and remove specified folder if value is 'true'.
	"""
	if 'SYNTHESYS_KEEP_ALL' in os.environ: 
		if os.environ['SYNTHESYS_KEEP_ALL'].lower()=='true': 
			logging.info("The 'SYNTHESYS_KEEP_ALL' environment variable is set. Do not remove the '{0}' folder.".format(OutputPath))
		else: 
			if Host is None:
				shutil.rmtree(Path)
			else:
				R=RemoteOperations()
				R.RemoteRun(Command='rm -rf {Path}'.format(Path=Path), abort_on_prompts='True', warn_only=True)
				
	else: 
		if Host is None:
			shutil.rmtree(Path)
		else:
			R=RemoteOperations()
			R.RemoteRun(Command='rm -rf {Path}'.format(Path=Path), abort_on_prompts='True', warn_only=True)
	return 







		
				
				
