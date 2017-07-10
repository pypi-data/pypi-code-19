
########################################################################

import os, sys
import logging

########################################################################

#=======================================================================
#                           ARGUMENT PARSER
#=======================================================================
def SetupParseOptions(SubParsers):
	"""
	Parse argument options and do corresponding actions.
	"""
	Parser = SubParsers.add_parser('display', help='Display synoptics of a VHDL entity in a Gtk window.')
	
	#------------------General command arguments-------------------------------------
	# ARGUMENT: VHDL file path
	Parser.add_argument('file', action='store', type=FilePath, help='VHDL source file to be parsed as DUT (Design Under Test).')
	# ARGUMENT: Display version
	Parser.add_argument('-v', '--version', action='version', version="SetupTBGen version='{0}'".format(VERSION), help="Displays SetupTBGen version.")
	
	Parser.set_defaults(func=Display_Opt)
	return Parser
	
#====================================================================	
def DirectoryPath(Path):
	"""
	raise error if path is no a directory
	"""
	if os.path.isdir(Path):
		return os.path.abspath(Path)
	else:
		try: os.makedirs(Path)
		except: raise TypeError
		
#====================================================================	
def FilePath(Path):
	"""
	raise error if path is no a directory
	"""
	if os.path.isfile(Path):
		return os.path.abspath(os.path.normpath(os.path.expanduser(Path)))
	else:
		raise TypeError
		
#================================================================
def Display_Opt(Options):
	"""wrapper for Display function"""
	return Display(VHDLFilePath=Options.file)

	
#=======================================================================
def Display(VHDLFilePath, ParentWindow=None):
	"""
	Parse VHDL file and display its synoptic in a GUI.
	"""
	if not os.path.isfile(VHDLFilePath):
	  logging.error("[Display] Given VHDL file '{0}' does not exist or is not a file.".format(VHDLFilePath)); return False
	if not VHDLFilePath.lower().endswith('.vhd'):
	  logging.error("[Display] Given file does not have a VHDL extension.".format(VHDLFilePath)); return False
	  
	#SynWin = SynopticWindow(ParentWindow=ParentWindow)
	if ParentWindow is None:
	  SynWin=Interface()
	  return SynWin.Start()
	else:
	  return True
	
	
	

os.environ['GDK_USE_XFT'] = "1"
########################################################################
#                           GENERIC GUI
########################################################################
class Interface:
	"This is the GUI builder for Generic GUI"
	#======================================================================
	def __init__(self, Title, IconPath=None, CloseFunctions=[], ResourcesDirs=[]):
		#------------------------------------------       
		signal.signal(signal.SIGINT, self.CatchSINGINT)
		#------------------------------------------
		self.Title=Title
		self.IconPath=IconPath
		self.CloseFunctions=CloseFunctions
			
		self.ErrorMsg=""
		
		self.IsDestroyed=False

	#======================================================================	
	#                       Main window
	#======================================================================		
	def InitGUI(self, ParentWindow=None):
		"""
		Get main windows and initialize it.
		"""	
	# Get objects--------------------------------------------------
		self.MainWindow = GUI.get_object("MainWindow")

	# Events Connections-------------------------------------------
		self.MainWindow.connect("destroy", self.on_MainWindow_destroy)

	# Set icon / images -------------------------------------------
		if self.IconPath: self.MainWindow.set_icon_from_file(IconPath) 
		
	# Cursor-------------------------------------------------------
		self.BusyCursor   = Gdk.Cursor(Gdk.CursorType.WATCH.WATCH)
		self.NormalCursor = Gdk.Cursor(Gdk.CursorType.ARROW)
		
	# First show Tasks----------------------------------------------		
		self.MainWindow.set_title(self.Title)
		
	#======================================================================	
	def BuildInterface(self, GladeFileName):
		"""
		Build GUI object and return it.
		"""
		# Set the Glade file-------------------------------------------	
		if GladeFileName!=None: 
			GUI=Bundle.BuildFromGlade(self.Bundle.Get(GladeFileName))
			if GUI==None: 
				logging.error("GUI initialization error: unable to build GUI widgets without glade file.")
				return None
			self.InitGUI(GUI)
			return GUI
		else: 
			logging.error("No Glade file specified: GUI building aborted.")
			return None
		
	#======================================================================		
	def Start(self):
		"""
		Launch Gtk main loop.
		"""
		GLib.threads_init()
		Gdk.threads_enter()
		Gtk.main()
		Gdk.threads_leave()
		
	#======================================================================	
	@BugTracking	
	def on_MainWindow_destroy(self, MainWindow):
		if self.IsDestroyed: return True
		self.IsDestroyed=True
		logging.debug("GUI: Main window Exit")
		for CloseFunc in self.CloseFunctions:
			logging.debug("Close function: {0}".format(CloseFunc))
			CloseFunc()
		GLib.idle_add(Gtk.main_quit)
		return True
	#=======================================================================
	@BugTracking	
	def CatchSINGINT(self, Sig, frame):
		"Handler for SIGINT interrupt signal."
		logging.warning("Ctrl+C pressed: exiting.")
		Gtk.main_quit()
		for CloseFunc in self.CloseFunctions:
#			logging.debug("Close function: {0}".format(CloseFunc))
			try: CloseFunc()
			except: pass
		return True

	#======================================================================	
	#                 COMMON METHODS
	#======================================================================	
	def Popup(self, title, text, dialog_type="info", ErrorMsg=None):
		"show a dialog with title and text specified"
		# Construct dialog according to dialog type
		if(dialog_type == "check"):	
			text += "\n\nClic on 'OK' to continue"
			logging.debug("[GUI] {0}: {1}".format(title, text))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CANCEL, text=text)# With Cancel button
			dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK) # Add the OK button
		elif(dialog_type == "info"):
			logging.debug("[GUI] info Popup <INFO: {0}>".format(title))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="\n{0}\n".format(text))
		elif(dialog_type == "result"):
			logging.debug("[GUI] result Popup :{0}".format(text))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="\n{0}\n".format(text))
		elif(dialog_type == "warning"):
			logging.debug("[GUI] warning Popup <# WARNING: {0}>".format(title))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.CLOSE, text=text)
		elif(dialog_type == "error"):
			logging.debug("[GUI] error Popup <# ERROR: {0}>".format(title))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE, text="\n{0}".format(text))
			if not ErrorMsg is None:
				self.ErrorMsg=ErrorMsg.strip()
			else:
				self.ErrorMsg=self.ErrorMsg.strip()
			if self.ErrorMsg!="":
				if len(self.ErrorMsg)>=3000: self.ErrorMsg=self.ErrorMsg[:3000]
				DBox=dialog.get_content_area()
				ExpBox=Gtk.Expander(label="More details")
				DBox.pack_start(ExpBox, False, False, padding=0)
				TextView=Gtk.TextView()
				TextView.set_wrap_mode(Gtk.WrapMode.WORD)
				ExpBox.add(TextView)
				TxtBuf=TextView.get_buffer()
				TxtBuf.insert(TxtBuf.get_end_iter(), self.ErrorMsg.replace('\x00', ''))
#				TxtBuf.set_text(self.ErrorMsg)
#				logging.debug("=> Expander text='{0}'".format(TxtBuf.get_text(TxtBuf.get_start_iter(), TxtBuf.get_end_iter())))
				ExpBox.set_expanded(False)
		elif(dialog_type == "question"):
			logging.debug("[GUI] question Popup <INFO: {0}>".format(title))
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.YES_NO, text="\n{0}\n".format(text))
		elif(dialog_type == "input"):
			logging.debug("[GUI] input Popup <{0}>".format(title))
			dialog = Gtk.InputDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.CANCEL, text="\n{0}".format(text))
			dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK) # Add the OK button
		else:
			dialog = Gtk.MessageDialog(self.MainWindow, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=text)

		dialog.show_all()
		dialog.set_title(title)
		response = dialog.run()
		dialog.destroy()
		return response

	#======================================================================	
	@BugTracking
	def ChoosePath(self, Multiple=True, Folder=False, Save=False):
		"Open a dialog to choose a directory(ies) or a file(s) (default). Return the path or the list of path if multiple selections, None if cancelling."
		logging.debug("GUI: Open Filechooser")
		if(Folder):
			filechooserdialog = Gtk.FileChooserDialog(title="Select directory", parent=self.MainWindow, action=Gtk.FileChooserAction.SELECT_FOLDER, buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		elif(Save):
			filechooserdialog = Gtk.FileChooserDialog(title="Save as...", parent=self.MainWindow, action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		else:
			filechooserdialog = Gtk.FileChooserDialog(title="Select file", parent=self.MainWindow, action=Gtk.FileChooserAction.OPEN, buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		filechooserdialog.set_select_multiple(Multiple)

		if(filechooserdialog.run() == Gtk.ResponseType.OK):
			
			if(Multiple):
				choosen =  filechooserdialog.get_filenames()
			else:
				choosen =  filechooserdialog.get_filename()
			filechooserdialog.destroy()
			return choosen
		else:
			filechooserdialog.destroy()
			logging.debug("GUI: Choose file cancelled")
			return None
		
#=======================================================================
def PopupDialog(Title, Message):
	"""
	Create a dialog a popup it.
	"""
	Dialog = Gtk.MessageDialog(None, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text="\n{0}\n".format(Message))
	Dialog.set_title(Title)
	response = Dialog.run()
	Dialog.destroy()

#======================================================================	


