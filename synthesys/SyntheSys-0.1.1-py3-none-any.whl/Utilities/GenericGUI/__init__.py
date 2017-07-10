

__all__=[]

import logging

#try: 
#	import gi
#	gi.require_version('Gtk', '3.0')
#	from gi.repository import Gtk, Gdk, GLib, Pango
#except ImportError: 
#	import gtk as Gtk
#	import gtk.gdk as Gdk
#	import glib as GLib
#	import pango as Pango
########################################################################

import os, sys, re, subprocess, traceback, signal
import shlex
#import serial
#import time
#from distutils.file_util import copy_file

ModulePath = os.path.dirname(__file__)
sys.path.append(os.path.join(ModulePath, "../"))
import Threads

import BugManager
from BugManager import BugTracking

from . import Bundle
#import locale
#locale.setlocale(locale.LC_ALL, '')
#os.environ['LANG']="en_US.UTF-8"
#Anti-aliased fonts
os.environ['GDK_USE_XFT'] = "1"
########################################################################
class Interface:
	"This is the GUI builder for Generic GUI"
	#======================================================================
	def __init__(self, Title, CloseFunctions=[], ResourcesDirs=[]):
		#------------------------------------------       
		signal.signal(signal.SIGINT, self.CatchSINGINT)
		#------------------------------------------
		self.Title=Title
		self.Bundle = Bundle.BundleObject(*ResourcesDirs)
		self.CloseFunctions=CloseFunctions
		GtkRC=self.Bundle.Get("gtkrc")
		if sys.platform.startswith("win"):
			GtkRC_Win=self.Bundle.Get("gtkrc_win")
			logging.debug("Windows Gtkrc: {0}".format(GtkRC_Win))
			Bundle.LoadGtkTheme([GtkRC_Win, GtkRC,])
		else:
			Bundle.LoadGtkTheme([GtkRC,])
			
		self.ErrorMsg=""
		
		self.IsDestroyed=False

	#======================================================================	
	#                       Main window
	#======================================================================		
	def InitGUI(self, GUI):
		"""
		Get main windows and initialize it.
		"""	
	# Get objects--------------------------------------------------
		self.MainWindow = GUI.get_object("MainWindow")

	# Events Connections-------------------------------------------
		self.MainWindow.connect("destroy", self.on_MainWindow_destroy)

	# Set icon / images -------------------------------------------
		self.MainWindow.set_icon_from_file(self.Bundle.Get("adacsys_icon.ico")) 
		
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





