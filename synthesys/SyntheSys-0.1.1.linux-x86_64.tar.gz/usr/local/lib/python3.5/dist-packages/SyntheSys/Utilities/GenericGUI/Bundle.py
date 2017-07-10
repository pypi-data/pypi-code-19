
import logging
import os, sys, re
#try: from gi.repository import Gtk, GLib, Pango
#except ImportError: 
#	import gtk as Gtk
#	import glib as GLib
#	import pango as Pango

from Misc import Silence

#Anti-aliased fonts
os.environ['GDK_USE_XFT'] = "1"
########################################################################

#======================================================================	
class BundleObject:
	#--------------------------------------------------------------
	def __init__(self, *OtherDirs):
		self.BundleDir=list(OtherDirs)
		if getattr(sys, 'frozen', False):
			# we are running in a |PyInstaller| bundle
			logging.debug("Bundle in frozen executable")
			if hasattr(sys, "_MEIPASS"):
				self.BundleDir+=[sys._MEIPASS,] # If file is unpacked from binary executable
#		     		BaseDir = os.environ["_MEIPASS2"]
			else: self.BundleDir+=[os.path.join(os.path.dirname(os.path.dirname(sys.modules["GUI"].__file__)), "Bundle"),]
		else:
			# we are running in a normal Python environment
			logging.debug("Python execution, bundle in current directory.")
			self.BundleDir+=[os.path.dirname(__file__),]
		
#		logging.debug("BundleDir: '{0}'".format(os.path.abspath(self.BundleDir)))
	#--------------------------------------------------------------
	def Get(self, FileName, Dir=False):
		"""
		Browse the bundle directory and return file path if it exists.
		"""
#		logging.debug("Bundle: get file '{0}'".format(FileName))
		for BundleDir in self.BundleDir:
			FilePath = GetFile(BundleDir, FileName, Folder=Dir)
			#FilePath = AvaFiles.GetFile(Dir, FileName)
			if FilePath!=None:
				if os.path.exists(FilePath):
					return FilePath
		if FilePath==None:
			logging.error("Can't find file: {0} in directories '{1}'.".format(FileName, self.BundleDir)) # If the program reach this point, it's an error
			return None
	#--------------------------------------------------------------
	def Clean(self):
#		if(os.path.exists(self.BundleDir)): 
#			shutil.rmtree(self.BundleDir) # Clean theme folder.
		pass

#======================================================================	
def BuildFromGlade(XML_file):
	if XML_file==None: return 
	Layout = Gtk.Builder()
	with Silence(sys.stdout):
		with Silence(sys.stderr):
			Layout.add_from_file(XML_file) # Building interface
	if Layout!=None:
		return Layout
	else:
		return None

#======================================================================		
def LoadGtkTheme(ThemeList):
	logging.debug("Load Gtk theme.")
	Gtk.rc_set_default_files(ThemeList)
	current_setting = Gtk.Settings.get_default()
	if Gtk.rc_reparse_all_for_settings(current_setting, True):
#		current_setting = Gtk.settings_get_default()
#		current_setting.props.Gtk_button_images = True
		return logging.debug("Load success.")
		return True
	else:
		return logging.debug("Load failed.")
		return False


#======================================================================		
def GetFile(RootDir, FileName, Folder=False):
	"Return the path of a given file(or directory) name in the specified directory (recursively)"
	if  (FileName == ""):
		raise NameError("No file name specified")
	else:# look for the file name recursively into the RootDir
		if Folder:
			for root, dirs, files in os.walk(RootDir):
				if(dirs.count(FileName) != 0):# if directory is found
					FilePath = os.path.abspath(os.path.join(root, FileName))
					return FilePath
		else:
			for root, dirs, files in os.walk(RootDir):
				if(files.count(FileName) != 0):# if file is found
					FilePath = os.path.abspath(os.path.join(root, FileName))
					return FilePath
		return None







