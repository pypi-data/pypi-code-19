
########################################################################

import os, sys
import tempfile
import logging
import time, traceback
from distutils.file_util import copy_file
import shutil
import Threads


#try: 
#	import gi
#	gi.require_version("Gtk", "3.0")
#	from gi.repository import Gtk, Gdk, GLib, Pango
#	from gi.repository.GdkPixbuf import Pixbuf, InterpType, PixbufAnimation
#except ImportError: 
#	import gtk as Gtk
#	import glib as GLib
#	import pango as Pango
#	from gtk import gdk as Gdk
	
########################################################################

from SyntheSys.YANGO import Components
from SyntheSys.YANGO import Constraints
#from SyntheSys.YANGO import NoCTEm
from SyntheSys.YANGO import HouseKeeping


from SyntheSys.SysGen import Simulation
from SyntheSys.Utilities.GenericGUI import Interface
from SyntheSys.Utilities.BugManager import BugTracking
from SyntheSys.Utilities import BugManager

# Anti-aliased fonts
os.environ['GDK_USE_XFT'] = "1"

########################################################################

class GUI(Interface):
	"This is the GUI builder class"
	LibPath   = "./"
	Bundle    = None
	ZoomRatio = 1.0
	LastPath  = os.path.normpath("./")
	HTree     = None
	SelectedComponent = None
	#======================================================================
	def __init__(self, Title, Version, LibPath, BundleDir, CloseFunctions=[], ResourcesDirs=[]):
		Interface.__init__(self, Title=Title, CloseFunctions=CloseFunctions, ResourcesDirs=ResourcesDirs)
#		try:
		self.LibPath=os.path.abspath(LibPath)
		self.Bundle = HouseKeeping.BundleObject(BundleDir)
	# Set the Glade file-------------------------------------------	
#		logging.debug("Fetch GUI widgets")
		GUI=self.BuildInterface("GUI_model.glade")
	# Get objects--------------------------------------------------
		self.scrolled_area 	= GUI.get_object("scrolled_area")
		self.frame_param     	= GUI.get_object("frame_param")
		#---
		self.spin_height 	= GUI.get_object("spin_height")
		self.spin_weight 	= GUI.get_object("spin_weight")
		#---
		self.button_zoomin     	= GUI.get_object("button_zoomin")
		self.button_zoomout    	= GUI.get_object("button_zoomout")
		self.button_lib   	= GUI.get_object("button_lib")
		self.button_generate   	= GUI.get_object("button_generate")
		self.button_MapAsNoC   	= GUI.get_object("button_MapAsNoC")
		self.button_NoCTEm   	= GUI.get_object("button_NoCTEm")
		self.ButtonSimulate   	= GUI.get_object("ButtonSimulate")
		#---
		self.image_noc     	= GUI.get_object("image_noc")
		#---
		self.menu_design     	= GUI.get_object("menu_design")
		self.menuitem_addAlgo   = GUI.get_object("menuitem_addAlgo")
		self.menuitem_addArch   = GUI.get_object("menuitem_addArch")
		self.menuitem_addFPGA   = GUI.get_object("menuitem_addFPGA")
		self.menuitem_addPort   = GUI.get_object("menuitem_addPort")
		self.menuitem_addNoC    = GUI.get_object("menuitem_addNoC")
		self.menuitem_addIP     = GUI.get_object("menuitem_addIP")
		self.menuitem_remove    = GUI.get_object("menuitem_remove")
		self.menuitem_src       = GUI.get_object("menuitem_src")
		self.menuitem_fromlib   = GUI.get_object("menuitem_fromlib")
		self.menuitem_tolib     = GUI.get_object("menuitem_tolib")
		self.menuitem_resources = GUI.get_object("menuitem_resources")
		self.menuitem_addlib    = GUI.get_object("menuitem_addlib")
		#---
		self.ViewBox_Draw     	= GUI.get_object("ViewBox_Draw")
		self.ViewBox     	= GUI.get_object("ViewBox")
		self.treeview_design    = GUI.get_object("treeview_design")
		self.treeview_design.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

		self.treeview_param     = GUI.get_object("treeview_param")
		self.CellValue          = GUI.get_object("CellValue")
		#self.CellCombo          = GUI.get_object("CellCombo")
		#---
		self.DrawingArea        = GUI.get_object("drawingarea")
		self.ScrolledDrawing    = GUI.get_object("ScrolledDrawing")
	# Events Connections-------------------------------------------
#		logging.debug("Connect events to handlers")
		self.treeview_design.connect("button_press_event", self.popup_treerow_menu)
		self.ChID = self.treeview_design.get_selection().connect("changed", self.ComponentSelectionChanged)
		self.treeview_design.connect("key_press_event", self.on_tree_key_event)
		self.treeview_param.connect("key_press_event", self.on_param_key_event)
		#---
		self.MainWindow.connect("destroy", self.on_MainWindow_destroy)
		#--- 
		self.button_zoomin.connect("clicked", self.on_button_zoomin_clicked)
		self.button_zoomout.connect("clicked", self.on_button_zoomout_clicked)
		self.button_lib.connect("clicked", self.on_button_lib_clicked)
		self.button_generate.connect("clicked", self.on_button_generate_clicked)
		self.button_MapAsNoC.connect("clicked", self.on_button_MapAsNoC_clicked)
		self.button_NoCTEm.connect("clicked", self.on_button_NoCTEm_clicked)
		self.ButtonSimulate.connect("clicked", self.on_ButtonSimulate_clicked)
		#--- 
		self.menuitem_addAlgo.connect("activate", self.on_menuitem_addItem_activate, "Algorithm")
		self.menuitem_addArch.connect("activate", self.on_menuitem_addItem_activate, "Architecture")
		self.menuitem_addFPGA.connect("activate", self.on_menuitem_addItem_activate, "FPGA")
		self.menuitem_addPort.connect("activate", self.on_menuitem_addItem_activate, "Port")
		self.menuitem_addNoC.connect("activate", self.on_menuitem_addItem_activate, "NoC")
		self.menuitem_addIP.connect("activate", self.on_menuitem_addItem_activate, "IP")
		self.menuitem_addlib.connect("activate", self.on_menuitem_addItem_activate, "Library")
		self.menuitem_remove.connect("activate", self.on_menuitem_remove_activate)
		self.menuitem_src.connect("activate", self.on_menuitem_src_activate)
		self.menuitem_fromlib.connect("activate", self.on_menuitem_fromlib_activate)
		self.menuitem_tolib.connect("activate", self.on_menuitem_tolib_activate)
		self.menuitem_resources.connect("activate", self.on_menuitem_resources_activate)
		
		self.DrawingArea.connect("draw", self.Draw)
		self.DrawingArea.connect("scroll-event", self.on_draw_scroll_event)
	
		self.CellValue.connect('edited', self.on_value_edited)

	# Set icon / images -------------------------------------------
		#logging.debug("Set GUI images")
		#self.MainWindow.set_icon_from_file(self.Bundle.Get("adacsys_icon.ico"))
	# Attribute ----------------------------------------------------
		self.ZoomRatio=1.0
		self.LastPath = self.LibPath
		self.HTree = None
		self.AddNewApp(Name="MyNoCApplication") # Set self.HTree
		GLib.idle_add(self.UpdateTree)
		self.SelectedComponent = None
		self.TempDirs=[]
		self.ActivityDiagram=None # Contain the Canvas for activity diagram
#		ActivityDiagram.IcoLib  = self.Bundle.Get("Lib.png")
#		ActivityDiagram.IcoServ = self.Bundle.Get("Service.png")
		PixbufMapAsNoC=Pixbuf.new_from_file(self.Bundle.Get("NoCMap.svg"))
		ScaledBuf = PixbufMapAsNoC.scale_simple(24, 24, InterpType.HYPER)
		self.button_MapAsNoC.set_icon_widget(Gtk.Image().set_from_pixbuf(ScaledBuf))	
		
	# Initialization tasks -----------------------------------------
#		Components.LoadLibraries([os.path.join(self.LibPath, "Application"), ])
		
	# Now show the windows -----------------------------------------
		#self.ComboModel=Gtk.ListStore(str)
		#self.CellCombo.set_property("model", self.ComboModel)
#		logging.debug("Show window")
		self.MainWindow.show()
			
		self.EXIT=False
#		#======================================================================
#		except:
#			logging.error("GUI initialization failed: Notify and quit Gtk main loop.")
#			GLib.idle_add(Gtk.main_quit)	
			
			
#======================================================================	
#                       Main window
#======================================================================		
	def on_MainWindow_destroy(self, MainWindow, ThirdArg=None):
#		try:	
		
		if self.EXIT is False: 
			self.EXIT=True
			self.Bundle.Clean()
			for DirPath in self.TempDirs: 
				if os.path.isdir(DirPath):
					shutil.rmtree(DirPath)
			logging.info("Leaving YANGO.")
			Gtk.main_quit()
		return True	
#		except:
#			Gtk.main_quit()
#			return True
#======================================================================	
	@BugTracking	
	def SetApplication(self, App):
		"""
		Change Htree Application component by another.
		"""
		if not isinstance(App, Components.App):
			logging.error("Application argument '{0}' is not an component App instance.".format(App))
			raise TypeError("Application argument '{0}' is not an component App instance.".format(App))
		else:
			App.SetBundle(self.Bundle)
			self.HTree=App
			logging.info("Set GUI application to '{0}'.".format(self.HTree))
		return False
		
#======================================================================	
	@BugTracking	
	def AddNewApp(self, Name="MyNoCApplication", TCG=None):
		"""
		Add a new Application component to Hierarchy Tree
		"""
		self.HTree=Components.App(Library=self.LibPath, Name=Name, Bundle=self.Bundle)
		self.HTree.AddChild("Algorithm", Name=Name+"_Algo", FromLib=False, ExtraParameters={})
		return self.HTree
	
#======================================================================	
	@BugTracking	
	def UpdateTree(self):
#		logging.info("Update treeview")
		self.treeview_design.get_selection().disconnect(self.ChID)
		# Save expand state for each row
		self.SaveExpandState(self.HTree)
		
		self.treeview_design.get_model().clear()
		self.DisplaySubtree(self.HTree)
		#self.treeview_design.expand_all()
		
		# Now display selected component
		if self.SelectedComponent:
#			logging.debug("Now display selected component")
			#self.SelectedComponent.Display(self.DrawingArea.window.cairo_create(), W, H, Ratio=self.ZoomRatio)
			self.ShowComponent(self.SelectedComponent)
		else:
			self.ShowComponent(None)
		self.ChID = self.treeview_design.get_selection().connect("changed", self.ComponentSelectionChanged)
		
#======================================================================	
	@BugTracking		
	def SaveExpandState(self, SubTree, ParentState=True):
		"""
		Save expand state for each row of the treeview.
		State is stored in tree item parameters.
		"""
		if ParentState==False:
			SubTree.ExpandState = False
		else:
			SubTree.ExpandState = True
		
		#elif SubTree.TreePath!=None:
		#	if SubTree.Parent==None: SubTree.ExpandState = True
		#	elif len(filter(lambda x: len(x)>0, SubTree.ChildLists.values()))==0:
		#		SubTree.ExpandState = True
		#	else:
		#		ExpState = self.treeview_design.row_expanded(SubTree.TreePath)
		#		if ExpState==None: SubTree.ExpandState = True
		#		else: SubTree.ExpandState = False
		#	print SubTree,"=> Saved expanded state =", SubTree.ExpandState
		#else: 
		#	SubTree.ExpandState = True
		if SubTree.Parent==None: 
			ExpState = True
		elif SubTree.TreePath!=None:
			ExpState = self.treeview_design.row_expanded(SubTree.TreePath)
			if ExpState==None: ExpState = True
		else:
			ExpState = True
		for ChildrenType, ChildrenList in list(SubTree.ChildLists.items()):
			for Child in ChildrenList:
				self.SaveExpandState(Child, ExpState)
		
#======================================================================	
	@BugTracking		
	def DisplaySubtree(self, SubTree, parent = None):
		"""
		Display hierarchical tree of components into the treeview recursively.
		"""
#		logging.debug("Display in tree {0}".format(SubTree))
		ChildList=[]
		KeyList=list(SubTree.ChildLists.keys()); KeyList.sort()
		for Key in KeyList:
			ChildList+=SubTree.ChildLists[Key]
		Model = self.treeview_design.get_model()
		
		TreeIter = Model.append( parent, (Pixbuf.new_from_file(SubTree.Icon).scale_simple(SubTree.IconSize[0], SubTree.IconSize[1], InterpType.BILINEAR), SubTree.Parameters["Common"]["Name"]) )
		SubTree.TreePath = Model.get_path(TreeIter)
		
				
		# Restore expand state for previously displayed rows
		if SubTree.TreePath!=None :
			if SubTree.ExpandState==False:
				self.treeview_design.collapse_row(SubTree.TreePath)
			else:
				self.treeview_design.expand_to_path(SubTree.TreePath)
			
		if(ChildList != []):
			for Child in ChildList:
				self.DisplaySubtree(Child, TreeIter)
	

#======================================================================	
	@BugTracking		
	def SelectComponent(self, TreePath):
		if TreePath==None: 
			self.SelectedComponent=None
#			logging.debug("No Component selected.")
		else:
			self.SelectedComponent= self.HTree.Get(TreePath)
#			logging.debug("Component '{0}' selected.".format(self.SelectedComponent))

#======================================================================	
	@BugTracking		
	def on_tree_key_event(self, treeview, event):
		"""
		Callback called when the user press a button over a tree row : remove item.
		"""
		keyname = Gdk.keyval_name(event.keyval)
		logging.debug("Key %s (%d) was pressed." % (keyname, event.keyval))
#		if ((Gdk.keyval_name(event.keyval) == 'Z') and
#			(event.get_state() & Gdk.ModifierType.CONTROL_MASK) and
#			(event.get_state() & Gdk.ModifierType.SHIFT_MASK)):
#			self.redo()
		if ("Delete", ).count(keyname):
			# Get the selection
			Selected = treeview.get_selection().get_selected_rows()[1]
			for Path in Selected:
				# Deleted item from main tree
				self.HTree.Get(Path).Remove()
			if len(Selected):
				self.UpdateTree()
			
		return False

#======================================================================
	@BugTracking			
	def on_draw_scroll_event(self, DrawingArea, Event):
		"""
		Callback called when user scroll over the drawing area.
		"""
		if Event.direction == Gdk.ScrollDirection.UP:
			self.on_button_zoomout_clicked(self.button_zoomout)
			logging.debug("Scroll up => Zoom out.")
			return True # Handled
		elif Event.direction == Gdk.ScrollDirection.DOWN:
			self.on_button_zoomin_clicked(self.button_zoomin)
			logging.debug("Scroll down => Zoom in.")
			return True # Handled
		elif Event.direction == Gdk.ScrollDirection.LEFT:
			logging.debug("Scroll left => Not supported.")
			return False # Handled
		elif Event.direction == Gdk.ScrollDirection.RIGHT:
			logging.debug("Scroll right => Not supported.")
			return False # Handled
			
		return False # Not Handled
	
#======================================================================	
	@BugTracking		
	def on_param_key_event(self, treeview, event):
		"""
		Callback called when the user press a button over a parameter row : suggest new choices.
		"""
		keyname = Gdk.keyval_name(event.keyval)
		logging.debug("Key %s (%d) was pressed." % (keyname, event.keyval))

		if ("Return", "space", "KP_Enter").count(keyname):
			Model, Selection = treeview.get_model(), treeview.get_selection()
			Path  = Model.get_path(Selection.get_selected()[1]) # new selected path
			Param = Model.get_value(Model.get_iter(Path), 0)
			ParentIter = Model.iter_parent(Model.get_iter(Path))
			ParentParam = Model.get_value(ParentIter, 0)
			# Find in which category this parameter is
			Category=None
			for Key in list(self.SelectedComponent.Parameters.keys()):
				if list(self.SelectedComponent.Parameters[Key].keys()).count(Param):
					Category=Key
					break
				elif list(self.SelectedComponent.Parameters[Key].keys()).count(ParentParam):
					Category=Key
					break
			if not Category: 
				logging.error("Couldn't determine which category this parameter '{0}' belongs to.".format(Param))
				return False
			if Param=="Sources":
				self.OpenSourcesManager()
			elif Param=="Constraints":
				FilePath=self.ChoosePath(Multiple=False, Folder=False, Save=False)
				if FilePath!=None: 
					self.SelectedComponent.Parameters[Category][Param]=FilePath
				if not self.SelectedComponent.TestParameter(Category, Param):
					self.SelectedComponent.Parameters[Category][Param]=None
				self.UpdateTree()
				return False
			elif ["Resets","Clocks","NetworkInterface","Ports","Disconnected"].count(ParentParam):
				Availables=self.SelectedComponent.AvailableValues(Param, ParentParam)
				if not Availables: 
					logging.error("None value for 'Availables'.")
					return False
				if not len(list(Availables.keys())): return False
				Value=self.ChooseValue(Availables, Msg="Available values for parameter '{0}'".format(Param))
				if Value!=None: 
					# First find value in available list
					Chosen=None
					for IOMapType, IOMapList in list(Availables.items()):
						for IOMap in IOMapList: 
							if str(Value) == str(IOMap):
								Chosen = IOMap
								break
						if Chosen!=None: break
					
					# If Choosen IOMap has already been used, unreference old signal mapping
					if Chosen.Signal!=None:
						logging.info("Already referenced mapping signal '{0}' has been chosen: changing reference.".format(Chosen))
						OldSig = Chosen.Signal
						try:
							OldIOMap = self.SelectedComponent.Parameters[Category][ParentParam][OldSig]
#							logging.debug("Old mapping: {0}".format(OldIOMap))
							if OldIOMap!=None:
								OldIOMap.Signal=None # Unreference old signal mapping
								self.SelectedComponent.Parameters[Category][ParentParam][OldSig]=Constraints.IOMap(Signal=OldSig)
#								logging.debug("Restore old '{0}' signal mapping to none.".format(OldSig))
						except: # It's a reference from another IP signal.
							logging.error("Cannot unreference another IP's mapping. Another IP port ('{0}') may not be mapped to FPGA Pad any more.".format(OldSig))
						
					# Get signal port from IP ports
					for S in list(self.SelectedComponent.Parameters[Category][ParentParam].keys()):
						if str(S)==str(Param):	
							Chosen.Signal=S
							break
						
#					logging.debug("New mapping: {0}".format(Chosen))
					self.SelectedComponent.Parameters[Category][ParentParam][S]=Chosen
					if ParentParam=="Clocks":
						Chosen.IsClock=True
				
			else:
				Availables = self.SelectedComponent.AvailableValues(Param)
				if not len(Availables[Param]): return False
				Value=self.ChooseValue(Availables, Msg="Available values for parameter '{0}'".format(Param))
				if Value!=None: self.SelectedComponent.Parameters[Category][Param]=Value
				self.SelectedComponent.TestParameter(Category, Param)
			self.ShowComponent(self.SelectedComponent)
		return False

#======================================================================	
	@BugTracking		
	def ChooseValue(self, Values, Msg="Available values :"):
		"""
		Open dialog to choose between available values (in a treeview).
		"""
		logging.debug("Dialog: Choose a new value.")
		ValueTypes = sorted(Values.keys())
#		# Create a combobox to select which ValueType to display-------------------
#		if len(ValueTypes)>1:
#			Combo=Gtk.combo_box_new_text()
#			for ValueType in ValueTypes:
#				Combo.append_text(ValueType)
#		# Define function for Treeview update--------------------------------------
#		def on_combo_changed(Combo):
#			TreeModel.clear()
#			Type = Combo.get_active_text()
#			for item in Values[Type]: TreeModel.append(None, [item,]) 
#				
#		Combo.connect("changed", on_combo_changed)
		# Create a treeview--------------------------------------------------------
		TreeModel= Gtk.TreeStore(str)
		for Type in ValueTypes:
			ParentType = TreeModel.append(None, [Type,]) 
			for Value in Values[Type]: 
				TreeModel.append(ParentType, [str(Value),]) 
		TreeView = Gtk.TreeView(TreeModel)
		TreeView.get_selection().set_mode(Gtk.SELECTION_SINGLE)
		TreeView.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
		TreeView.set_headers_visible(False)
		Dialog = Gtk.Dialog("Select value", self.MainWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.OK))

		SW=Gtk.ScrolledWindow()
		Dialog.get_content_area().pack_start(Gtk.Label(Msg), expand=False, fill=False, padding=5)
		Dialog.get_content_area().pack_start(SW, padding=7)
		SW.add_with_viewport(TreeView)
		Dialog.resize(300, 500)
		
		if len(ValueTypes)==1: TreeView.expand_all()
		Dialog.show_all()
		Response=Dialog.run()
		if Response==Gtk.ResponseType.OK:
			Selection=TreeView.get_selection()
			logging.debug("Dialog: response = OK.")
			if Selection != None:
#				logging.debug("Dialog: Selected value = OK.")
				(TreeModel, TreeIter)=Selection.get_selected()
				if TreeIter:
					Value = TreeModel.get_value(TreeIter, 0).strip()
					logging.debug("Dialog: New value = '{0}'.".format(Value))
					Dialog.destroy()
					if ValueTypes.count(Value): return None
					else: return Value
			else:
				logging.debug("Dialog: no value selected (aborting).")
#		else:
#			logging.debug("Dialog: response = reject.")
		Dialog.destroy()
		return None

#======================================================================	
	@BugTracking		
	def on_value_edited(self, CellValue, Path, NewValue):
		"""
		Find the sub dictionary of parameters concerned, and edit value as required.
		"""
		NewValue=NewValue.strip()
		Model = self.treeview_param.get_model()
		VName = HouseKeeping.Normalize(Model.get_value(Model.get_iter(Path), 0)).decode('utf-8')
		
		logging.debug("Value edited: '{0}'".format(VName))
		logging.debug("New value proposed: '{0}'".format(NewValue))
		#-------------------------------------------------------------------
		def FindDict(ParamDict, VName):
			print("VName={0}".format(VName))
			for Item in list(ParamDict.keys()):
				if isinstance(ParamDict[Item], dict):
					print("Item: {0} > {1}".format(Item, ParamDict[Item]))
					if str(VName) in ParamDict[Item]:
						return ParamDict[Item], Item
					else:
						print("Item: {0} not found".format(str(VName)))
						Found,DName=FindDict(ParamDict[Item], VName) # Recursive
						if Found: return Found, DName
			return None, None
		#-------------------------------------------------------------------
		ParamDict, DictName = FindDict(self.SelectedComponent.Parameters, VName)
		if ParamDict:
			OldValue=ParamDict[VName]
			if isinstance(OldValue, str):
				ParamDict[VName]=NewValue
			elif isinstance(OldValue, list):
			# If it was a list, consider new value as a list (coma separated strings)
				ParamDict[VName]=[x for x in NewValue.split(',') if x!=""]
			if not self.SelectedComponent.TestParameter(DictName, VName): 
				# Restore old value
				ParamDict[VName]=OldValue
				self.Popup("Wrong parameter value", "Value '{0}' doesn't fit rules.".format(NewValue), "warning")
						
			logging.debug("Value '{0}' set to '{1}'.".format(VName, NewValue))
			self.ShowComponent(self.SelectedComponent)
			self.UpdateTree()
		return False
#======================================================================	
	@BugTracking		
	def ComponentSelectionChanged(self, Selection):
		"""
		Update drawing view and parameter view according to newly selected component.
		"""
#		logging.debug("Component selection changed event.")
		# Get the selected path(s)		
		TreeIter = Selection.get_selected()[1]
		if TreeIter:
			Path = self.treeview_design.get_model().get_path(TreeIter) # new selected path
			self.SelectComponent(Path) # Get selected component
			if Selection.count_selected_rows()==1:
				self.ShowComponent(self.SelectedComponent)
		else:
			self.frame_param.hide()
			self.SelectComponent(None) # Get selected component
			
		self.DrawingArea.queue_draw()
		return False
#======================================================================	
	@BugTracking		
	def popup_treerow_menu(self, TreeView, event):
		"""
		Callback called when the user press a button over a row check if it's 
		the right button and emit a signal on that case
		"""
		logging.debug("Clic on component tree view.")

		# Get the selection
		selection = TreeView.get_selection()
		# Get the selected path(s)
		rows = selection.get_selected_rows()
		# Figure out which item they right clicked on
		path = TreeView.get_path_at_pos(int(event.x), int(event.y))
		#--------------------------------------------------------------
		if path is None:
			selection.unselect_all()
			self.frame_param.hide()
			self.SelectComponent(None) # Get selected component
#			logging.debug("Selected Component: None.")
			return False
		#--------------------------------------------------------------
		if path[0] not in rows[1]:
			#selection.unselect_all()
			selection.select_path(path[0]) 
		#--------------------------------------------------------------

		Path = TreeView.get_model().get_path(selection.get_selected()[1]) # new selected path

		self.SelectComponent(Path) # Get selected component
		
		if(isinstance(self.SelectedComponent, Components.App)):
			if self.SelectedComponent.APCG!=None: self.button_MapAsNoC.show()
			else: self.button_MapAsNoC.hide()
			self.button_generate.show()
		elif(isinstance(self.SelectedComponent, Components.Algo)):	
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
		elif(isinstance(self.SelectedComponent, Components.Arch)):
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
		elif(isinstance(self.SelectedComponent, Components.FPGA)):
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
		elif(isinstance(self.SelectedComponent, Components.Port)):
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
		elif(isinstance(self.SelectedComponent, Components.IP)):
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
			#if(isinstance(self.SelectedComponent, Components.NoC)):
		elif(isinstance(self.SelectedComponent, Components.Lib)):
			self.button_MapAsNoC.hide()
			self.button_generate.hide()
		# Check for right click
		if event.button == 3:
			logging.debug("But Right clic ! (show popup)")
			# If they didnt right click on a currently selected row, change the selection
			if selection.count_selected_rows() > 1:
				self.menuitem_addFPGA.set_sensitive(False)
				self.menuitem_addNoC.set_sensitive(False)
				self.menuitem_addIP.set_sensitive(False)
				self.menu_multi.Popup(None, None, None, TreeView, event.button, event.time)
			else:
				model    = TreeView.get_model()
				if(isinstance(self.SelectedComponent, Components.App)):
					self.menuitem_addAlgo.show()
					self.menuitem_addArch.show()
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_addNoC.show()
					self.menuitem_addIP.show()
					self.menuitem_addlib.hide()
					self.menuitem_remove.hide()
					self.menuitem_src.hide()
					self.menuitem_resources.hide()
				elif(isinstance(self.SelectedComponent, Components.Algo)):
					self.menuitem_addAlgo.hide()
					self.menuitem_addArch.hide()	
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_addNoC.hide()
					self.menuitem_addIP.hide()
					self.menuitem_addlib.hide()
					self.menuitem_remove.show()
					self.menuitem_src.hide()
					self.menuitem_resources.hide()
				elif(isinstance(self.SelectedComponent, Components.Arch)):
					self.menuitem_addAlgo.hide()
					self.menuitem_addArch.hide()	
					self.menuitem_addFPGA.show()
					self.menuitem_addPort.show()
					self.menuitem_addNoC.hide()
					self.menuitem_addIP.hide()
					self.menuitem_addlib.hide()
					self.menuitem_remove.show()
					self.menuitem_src.hide()
					self.menuitem_resources.hide()
				elif(isinstance(self.SelectedComponent, Components.FPGA)):
					self.menuitem_addAlgo.hide()	
					self.menuitem_addArch.hide()
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_addNoC.hide()
					self.menuitem_addIP.hide()
					self.menuitem_addlib.hide()
					self.menuitem_remove.show()
					self.menuitem_src.hide()
					self.menuitem_resources.hide()
				elif(isinstance(self.SelectedComponent, Components.Port)):
					self.menuitem_addAlgo.hide()
					self.menuitem_addArch.hide()
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_addNoC.hide()
					self.menuitem_addIP.hide()
					self.menuitem_addlib.hide()
					self.menuitem_remove.show()
					self.menuitem_src.hide()
					self.menuitem_resources.hide()
				elif(isinstance(self.SelectedComponent, Components.IP)):
					self.menuitem_addAlgo.hide()
					self.menuitem_addArch.hide()
					self.menuitem_src.show()	
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_remove.show()
					self.menuitem_resources.show()
					if(isinstance(self.SelectedComponent, Components.NoC)):
						self.menuitem_addNoC.show()
						self.menuitem_addIP.show()
						self.menuitem_addlib.hide()
					else:
						self.menuitem_addNoC.hide()
						self.menuitem_addIP.hide()
						self.menuitem_addlib.show()
				elif(isinstance(self.SelectedComponent, Components.Lib)):
					self.menuitem_addAlgo.hide()	
					self.menuitem_addArch.hide()
					self.menuitem_addFPGA.hide()
					self.menuitem_addPort.hide()
					self.menuitem_addNoC.hide()
					self.menuitem_addIP.hide()
					self.menuitem_addlib.hide()
					self.menuitem_remove.show()
					self.menuitem_src.show()
					self.menuitem_resources.hide()
				else:
					return False

				self.menu_design.Popup(None, None, None, TreeView, event.button, event.time)
	
		# Be sure to return True to stop selection being changed by right clicking
			return True

#======================================================================	
	@BugTracking	
	def ShowComponent(self, TreeMember):
		"""
		Display parameters as a list in parameter treeview.
		"""
		if not TreeMember: 
			Width  = self.ScrolledDrawing.get_allocation().width
			Height = self.ScrolledDrawing.get_allocation().height
#			Components.Drawing.DrawWelcome(self.DrawingArea.window.cairo_create(), Width, Height, AdacsysLogo=self.Bundle.Get("adacsys_logo.png"))
			self.DrawingArea.set_size_request(Width, Height)
			self.treeview_param.get_model().clear()
			return 
#		logging.info("Show parameters of {0}".format(TreeMember))
		self.treeview_param.get_model().clear()
		
		#--------------------------------------------------------------------
		def AddParam(ParamDict, TreeParent, Editable=False):
			ValueNameList = list(ParamDict.keys())
			ValueNameList.sort()
			for VName in ValueNameList:
				Value = ParamDict[VName]
				# IF DICTIONARY => New Child ! --------------------------
				if isinstance(Value, dict):
					if VName == "Parent":
						if TreeMember.Parent:
							SubTitle = TreeMember.Parent.Type+" parameters"
						else:
							SubTitle = TreeMember.Type+" parameters"
					elif VName == "Resources" or VName == "Common":
						SubTitle = VName+" parameters"
					else:
						SubTitle = VName
					NewParent = self.treeview_param.get_model().append(TreeParent, [SubTitle,"", False,])
					AddParam(Value, NewParent, VName!="Resources")
				# IF List => coma separated values ----------------------
				elif isinstance(Value, list) and not isinstance(Value, str):
					Values="\n".join([str(x) if x!=None else "" for x in Value])
					self.treeview_param.get_model().append(TreeParent, [VName, 
										str(Values), 
										Editable,])
				# IF string => string values ----------------------------
				else:
					if Value is None: # Get first item
						Value=""
						ParamDict[VName]=Value # and set it !
					self.treeview_param.get_model().append(TreeParent, [str(VName), 
										str(Value), 
										Editable,])
		#--------------------------------------------------------------------
		AddParam(TreeMember.Parameters, None)

		self.treeview_param.expand_all()
		self.frame_param.show()
		
#		# if algo has been selected : Show CDFG
#		if isinstance(TreeMember, Components.Algo):  
#			x = self.ViewBox_Draw.get_allocation().width
#			y = self.ViewBox_Draw.get_allocation().height
#			if self.ActivityDiagram==None:
#				self.ActivityDiagram=ActivityDiagram.Canvas(x-117, y, Libs=["./NoCXML/lib", "./NoCXML/NoC"])
#				self.ActivityDiagram.show_all()
#				self.ActivityDiagram.SetTCGHandler(self.HTree.MapTCG)
#				self.ViewBox.pack_start(self.ActivityDiagram, expand=True, fill=True)	
#			else:
#				self.ActivityDiagram.show_all()
#			self.ViewBox_Draw.hide()
#		# If an activity diagram has been specified update TCG
#		else:
#			self.ViewBox_Draw.show() 
#			if self.ActivityDiagram!=None: 
#				self.ActivityDiagram.hide_all()
#				if isinstance(TreeMember, Components.App):
#					TreeMember.UpdateAlgo() # AD_Tree=self.ActivityDiagram.GetTree()) 
#			# Now show component draw
#			W, H = self.DrawingArea.window.get_size()
#		
#			CTX=self.DrawingArea.window.cairo_create()
#			W, H = TreeMember.Display(CTX, W, H, Ratio=self.ZoomRatio)
#			#self.Drself.DrawingArea.window.awingArea.set_size_request(int(W), int(H));
		# Now show component draw
#		Width  = self.ScrolledDrawing.get_allocation().width
#		Height = self.ScrolledDrawing.get_allocation().height
#		CTX=self.DrawingArea.window.cairo_create()
#		W, H = TreeMember.Display(CTX, Width, Height, Ratio=self.ZoomRatio)
#		Sx, Sy = max(Width, int(W)), max(Height, int(H))
#		self.DrawingArea.set_size_request(Sx, Sy)
#		print(("Drawing area size: x, y =", Sx, Sy))

#======================================================================	
#	@BugTracking	
#	def SetTCG(self, TCG): 
#		"""
#		Build a graph from the activity tree.
#		"""
#		if TCG!=None:					
#			self.HTree.SetTCG(TCG=TCG)
#			return True
#		else:
#			logging.error("No TCG built: no input specified.")
#			return False

#======================================================================	
	@BugTracking	
	def SetCDFG(self, CDataFlowGraph):
		"""
		Set Control Data Flow Graph for app algorithm.
		"""
		if CDataFlowGraph==None:
			logging.error("No Control Data Flow Graph specified: CDFG setting failed.")
			return False
		else:
			A=self.HTree.GetAlgo()
			if A!=None: A.SetCDFG(CDFG=CDataFlowGraph)
			else:
				A=self.HTree.AddChild("Algorithm", Name=self.HTree.Parameters["Common"]["Name"]+"_Algo", FromLib=False, ExtraParameters={})
				if A!=None: A.SetCDFG(CDFG=CDataFlowGraph)
				else: 
					logging.error("Failed to add algorithm to application '{0}'".format(self.HTree.Parameters["Common"]["Name"]))
					return False
			return True

#======================================================================	
	@BugTracking	
	def Draw(self, widget, Ctx):
		"Refresh cairo drawing if the window's size change."
		# context = self.DrawingArea.window.cairo_create()
		# self.DrawingArea.draw(context)

		# set a clip region for the draw event
		#self.Ctx.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		Width  = self.ScrolledDrawing.get_allocation().width
		Height = self.ScrolledDrawing.get_allocation().height
		if(self.SelectedComponent):
			if self.SelectedComponent.Drawing is None:
				W, H = Components.Drawing.DrawWelcome(Ctx, Width, Height)#, AdacsysLogo=self.Bundle.Get("adacsys_logo.png"))
			else:
				W, H = self.SelectedComponent.Display(Ctx, Width, Height, Ratio=self.ZoomRatio)
		else:
			W, H = Components.Drawing.DrawWelcome(Ctx, Width, Height)#, AdacsysLogo=self.Bundle.Get("adacsys_logo.png"))
			
		Sx, Sy = max(Width, int(W)), max(Height, int(H))
		self.DrawingArea.set_size_request(Sx, Sy)
		return False
#======================================================================
	@BugTracking	
	def on_menuitem_addItem_activate(self, menuitem, Type):
		"""
		Add a new child to selected component (if Child=IP: select module)
		"""
		Child = self.SelectedComponent.AddChild(Type)
		self.UpdateTree()
#======================================================================
	@BugTracking	
	def on_menuitem_remove_activate(self, menuitem_remove):
		self.SelectedComponent.Remove()
		self.UpdateTree()
#======================================================================
	@BugTracking	
	def on_menuitem_src_activate(self, menuitem_src):
		self.OpenSourcesManager()
		self.ShowComponent(self.SelectedComponent)
#======================================================================
	@BugTracking	
	def on_menuitem_fromlib_activate(self, menuitem_fromlib):
		Availables = self.SelectedComponent.GetAvailable()
		Value = self.ChooseValue(Availables, Msg="Available {0}s in library :".format(self.SelectedComponent.Type.lower()))
		if Value:
			self.SelectedComponent.SetFromLib(Value.split('(')[0])
			self.UpdateTree()
#======================================================================
	@BugTracking	
	def on_menuitem_tolib_activate(self, menuitem_tolib):
		if self.SelectedComponent.IsInLib(): # TODO: add comment entry question
			Text="Item '{0}' found in library.\nDo you want to overwrite it ?".format(self.SelectedComponent)
			if(self.Popup("Item already in library: overwrite ?",Text,"question")==True):
				self.SelectedComponent.UpdateLibElement()
		else:
			self.SelectedComponent.AddToLib()
#======================================================================
	@BugTracking	
	def on_button_zoomin_clicked(self, ButtonZoomIn):
		self.ZoomRatio+=0.1
		self.DrawingArea.queue_draw()

#======================================================================
	@BugTracking	
	def on_button_zoomout_clicked(self, ButtonZoomOut):
		self.ZoomRatio-=0.1
		self.DrawingArea.queue_draw()
		
#======================================================================
	@BugTracking	
	def on_button_lib_clicked(self, Buttonlib):
		"""
		Open a dialog for managing library items.
		"""
		Buttonlib.set_sensitive(False)
		#-------------------------------------------------------------------
		logging.debug("Dialog: open library manager.")
		# Create a combobox to select which library to display
		ComboLib=Gtk.combo_box_new_text()
		for LibFamily in ["Application","Architecture","FPGA","Port","NoC","IP",]:
			ComboLib.append_text(LibFamily)
	
		# Create a treeview
		TreeModel= Gtk.TreeStore(str)
		TreeView = Gtk.TreeView(TreeModel)
		TreeView.get_selection().set_mode(Gtk.SELECTION_SINGLE)
		TreeView.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
		TreeView.set_headers_visible(False)
		TreeView.set_rules_hint(True)
		Dialog = Gtk.Dialog("Select value", self.MainWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))
	
		ComboLib.COMPONENT=None
		#------------------------------
		def on_library_selected(Combo):
			TreeModel.clear()
			Lib = Combo.get_active_text()
			C=Components.App(self.LibPath, Bundle=self.Bundle)
			if Lib=="Application":   Combo.COMPONENT = C
			elif Lib=="Architecture":Combo.COMPONENT = Components.Arch(Parent=C)
			elif Lib=="FPGA":Combo.COMPONENT = Components.FPGA(Parent=C)
			elif Lib=="Port":Combo.COMPONENT = Components.Port(Parent=C)
			elif Lib=="NoC": Combo.COMPONENT = Components.NoC(Parent=C)
			elif Lib=="IP":  Combo.COMPONENT = Components.IP(Parent=C)
		
			ValueDict = Combo.COMPONENT.GetAvailable()
			for Cat in sorted(ValueDict.keys()): 
				Parent = TreeModel.append(None, [Cat,]) 
				for item in ValueDict[Cat]:
					TreeModel.append(Parent, [item,]) 
			#TreeView.expand_all()
		#------------------------------
		ComboLib.connect("changed", on_library_selected)
		ComboLib.set_active(0)

		SW=Gtk.ScrolledWindow()
		SW.add_with_viewport(TreeView)
	
		Dialog.get_content_area().pack_start(ComboLib, expand=False, fill=False, padding=5)
		HBox = Gtk.HBox(homogeneous=False, spacing=2)
		HBox.pack_start(SW, expand=True, fill=True, padding=0)
		VBox = Gtk.VButtonBox()
		BtnRemove = Gtk.Button(label="Remove", stock=Gtk.STOCK_REMOVE, use_underline=True)
		#------------------------------
		def on_removed_clicked(BtnRemove, Combo):
			Selection=TreeView.get_selection()
			if Selection != None:
				(TreeModel, TreeIter)=Selection.get_selected()
				if TreeIter:
					if TreeModel.iter_parent(TreeIter) is None: return
					Value = TreeModel.get_value(TreeIter, 0).strip().split()[0]
					logging.debug("Dialog: remove lib value = '{0}'.".format(Value))
					Combo.COMPONENT.RemoveLibElement(Value)
					on_library_selected(Combo) # Update list
		#------------------------------
		BtnRemove.connect("clicked", on_removed_clicked, ComboLib)
		VBox.pack_start(BtnRemove, expand=False, fill=False, padding=0)
		HBox.pack_start(VBox, expand=False, fill=False, padding=0)
		Dialog.get_content_area().pack_start(HBox, padding=7)
		Dialog.resize(600, 400)

		Dialog.show_all()
		Response=Dialog.run()
		Dialog.destroy()
		#-------------------------------------------------------------------
		Buttonlib.set_sensitive(True)

#======================================================================
	@BugTracking	
	def on_button_generate_clicked(self, ButtonGenerate):
		ButtonGenerate.set_sensitive(False)
		#try:
		# First check child parameters
		for Key in list(self.HTree.ChildLists.keys()):
			for Child in self.HTree.ChildLists[Key]:
				WrongParams = Child.CheckParameters()
				if len(WrongParams):
					Text="\n".join(["{0}'s value '{1}' not in {2}.".format(
						Param, 
						Child.Parameters[Type][Param],
						AvalableList
						) for Type,Param,AvalableList in WrongParams])
					self.Popup("Wrong '{0}' parameters.".format(Child), Text, "warning")
					ButtonGenerate.set_sensitive(True)
					return False
		# Now we can generate files !
		OutputPath=self.ChoosePath(Multiple=False, Folder=True, Save=False)
		if OutputPath!=None:
			if os.path.isdir(OutputPath): 
				# Iterate on each architecture (each command flow)
				self.HTree.GenerateHDL(OutputPath, TBValues={}, TBClkCycles=1600, CommunicationService=None)
				self.Popup("Application '{0}' successfully generated.".format(self.HTree), "Application '{0}' successfully generated.".format(self.HTree), "info")
#					logging.debug("Display the waiter dialog for FPGA implementation.")
#					self.Run(ImplementFlow)
		#except: self.Popup("Generation failed", "Runtime error when generating output files.", "error")
		#finally: 
		ButtonGenerate.set_sensitive(True)
		return False

#======================================================================
	@BugTracking	
	def on_button_MapAsNoC_clicked(self, ButtonMapAsNoC):
		ButtonMapAsNoC.set_sensitive(False)
		#-----------------------------------
		self.HTree.MapTCG()
		self.UpdateTree()
		
		#-----------------------------------
		ButtonMapAsNoC.set_sensitive(True)
		return False

#======================================================================
	@BugTracking	
	def on_button_NoCTEm_clicked(self, ButtonNoCTEm):
		ButtonNoCTEm.set_sensitive(False)
		#-----------------------------------
		if not isinstance(self.SelectedComponent, Components.NoC):
			logging.error("Selected component is not a NoC component: simulation aborted.")
			self.Popup("No NoC selected", "Selected component is not a NoC component.", "error")
			#-----------------------------------
			ButtonNoCTEm.set_sensitive(True)
			return False
		Results = NoCTEm.TrafficSynthesizer(self.SelectedComponent, self.MainWindow)
		#-----------------------------------
		ButtonNoCTEm.set_sensitive(True)
		return False

#======================================================================
	@BugTracking	
	def on_ButtonSimulate_clicked(self, ButtonSimulate):
		ButtonSimulate.set_sensitive(False)
		#-----------------------------------
		OutputPath=tempfile.mkdtemp(suffix='', prefix='{0}_Simulation'.format(self.SelectedComponent.Parameters["Common"]["Name"]))
		if not os.path.exists(OutputPath):
			os.makedirs(OutputPath)
			
		if not "Module" in self.SelectedComponent.Parameters["Common"]:
			logging.error("No top module generated from selected item. Please generate module first.")
			self.Popup("Simulation error", "No top module generated from selected item: aborted.", "error")
			#-----------------------------------
			ButtonSimulate.set_sensitive(True)
			return False
		Sim = Simulation.Simulation(
					Module=self.SelectedComponent.Parameters["Common"]["Module"], 
					OutputPath=OutputPath)
		Sim.Run(Simulator="isim")
		#-----------------------------------
		ButtonSimulate.set_sensitive(True)
		return False
		
#======================================================================
	@BugTracking	
	def Run(self, ImplementFlow, Title="Waits for commands execution", Func=None, Args=[]):
		"""
		Display a waiter dialog. Check return values of commands to update status.
		Always check live status of thread: if zombie => close dialog.
		"""
		if ImplementFlow==None: return False
		IconBusy=PixbufAnimation(self.Bundle.Get("StatusBusy.gif"))
		IconIdle=Pixbuf.new_from_file(self.Bundle.Get("StatusIdle.png")).scale_simple(20, 20,InterpType.BILINEAR)
		IconOK=Pixbuf.new_from_file(self.Bundle.Get("StatusOk.png")).scale_simple(20, 20,InterpType.BILINEAR)
		IconCancelled=Pixbuf.new_from_file(self.Bundle.Get("StatusCancelled.png")).scale_simple(50, 10,InterpType.BILINEAR)
		IconError=PixbufAnimation(self.Bundle.Get("StatusError.gif"))
		
		Dialog = Gtk.Dialog(Title, self.MainWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT)
		CancelBtn = Dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		# Fill dialog area with command info / status
		VBox = Gtk.VBox()
		Dialog.get_content_area().pack_start(VBox, expand=False, fill=False, padding=5)
		IconList=[]
		Cnt=0
		
		#------------------------------------------------
		# Setup dialog contain : Fill HBox with Command info + status icon
		for Command, Info in ImplementFlow.ListCommands():
			Cnt+=1
			HBox = Gtk.HBox()
			VBox.pack_start(HBox, False, False, padding=5)
			HBox.pack_start(Gtk.Label("{0} - ".format(Cnt)+Info), False, False, padding=5)
			x, y, Icon = 40, 40, Gtk.image_new_from_pixbuf(IconIdle) # Waiting icon	
			HBox.pack_start(Icon, False, False, padding=5)
			IconList.append(Icon)
			
		#------------------------------------------------
		Icons={"OK":IconOK, "BUSY":IconBusy, "IDLE":IconIdle, "ERROR":IconError, "CANCELLED":IconCancelled}
		#Running=[None,]
		#def Watch(Func=None, Args=[]):
		#	for Index in range(0, len(IconList)):
		#		if FPGACmds[Index][1] == None: 
		#			IconList[Index].set_from_pixbuf(Icons["IDLE"])
		#		elif FPGACmds[Index][1] == "Running": 
		#			if not Running[0]==Index:
		#				Running[0]=Index
		#				IconList[Index].set_from_animation(Icons["BUSY"])
		#			# Stop thread if it's last command
		#			if Index==(len(IconList)-1):Event.set()
		#		else: 
		#			IconList[Index].set_from_pixbuf(Icons["OK"])
		#	if not Thread.isAlive():
		#		logging.debug("Thread is not alive any more: join it !")
		#		RetList = map(lambda x: x[1], FPGACmds)	
		#		logging.debug("Return List: {0}".format(RetList))	
		#		if RetList.count(None) or RetList.count("Running"):
		#			self.Popup("Command execution failed", "Command execution failed.", "error", Dialog)
		#		Thread.join()
		#		Dialog.destroy()
		#		if Func!=None: 
		#			Text=Func(*Args)
		#			if Text: self.Popup("Success", Text, "info")
		#		return  False # stop calling Watch
		#	return True # Go on calling Watch
		
		#logging.debug("Now that dialog is displayed, update it each 500ms.")
		#GLib.timeout_add(500, Watch, Func, Args) # Every 500 milliseconds
		Dialog.show_all()
		IconList[0].set_from_animation(Icons["BUSY"])
		
		#------------------------------------------------
		class FlowCtrl:
			#------------------------------------------------
			def __init__(self):
				self.CurrentStepIndex=0
			#------------------------------------------------
			def CmdSuccess(self):
				"""
				Change state icon for current command to "OK" icon.
				"""
				IconList[self.CurrentStepIndex].set_from_pixbuf(Icons["OK"])
				self.CurrentStepIndex+=1
				if self.CurrentStepIndex<len(IconList):
					IconList[self.CurrentStepIndex].set_from_animation(Icons["BUSY"])
		
			#------------------------------------------------
			def CmdFailed(self):
				"""
				Change state icon for current command to "OK" icon.
				"""
				IconList[self.CurrentStepIndex].set_from_animation(Icons["ERROR"])
				self.CurrentStepIndex+=1
				Dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
				CancelBtn.destroy()
				for i in range(self.CurrentStepIndex,len(IconList)):
					IconList[i].set_from_pixbuf(Icons["CANCELLED"])
					
		#------------------------------------------------
		FC = FlowCtrl()
		Thread = Threads.LaunchAsThread("FPGA_implementation", ImplementFlow.Start, [FC.CmdSuccess, FC.CmdFailed, True])
		#------------------------------------------------
		
		Response = Dialog.run()
		if Response==Gtk.ResponseType.CANCEL:
			# Kill the running process
			pass
		Dialog.destroy()
		Thread.join()
		return True
	
#======================================================================
	@BugTracking	
	def MapSignals(self, SignalList, TypeList):
		"""
		Open a dialog that enable user to select a type for each 
		signal (Resets, Clocks, Network Interface, Ports).
		SignalList is a list of signal. A signal is a list of
		[SigName, SigType, SigIO, SigSize]
		"""
		logging.debug("GUI: Open signal mapping dialog.")
		#-------------------------------------------------------------------
		Dialog = Gtk.Dialog("Select value", self.MainWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		
		VBox = Gtk.VBox()
		VBox.pack_start(Gtk.Label("Select IP signals types :"), expand=False, fill=False, padding=5)
		#SW=Gtk.ScrolledWindow()
		#SW.add_with_viewport(VBox)		
		Dialog.get_content_area().pack_start(VBox, expand=False, fill=False, padding=5)
		
		ComboList=[]
		for SigName, SigIO, SigSize, SigType in SignalList:
			HBox = Gtk.HBox(homogeneous=False, spacing=2)
			if SigSize>1: Label="{0:<3}: <b>{1}[0:{2}]</b>".format(SigIO,SigName, SigSize-1)
			else:Label="{0:<3}: <b>{1}</b>".format(SigIO,SigName)
			GtkLabel = Gtk.Label(Label)
			GtkLabel.modify_font(pango.FontDescription("monospace 10"))
			GtkLabel.set_use_markup(True)
			GtkLabel.set_justify(Gtk.JUSTIFY_LEFT)
			GtkLabel.set_alignment(0, 0)
			HBox.pack_start(GtkLabel, expand=True, fill=True, padding=0)
			# Create a combobox to select which signal type is selected
			Combo=Gtk.combo_box_new_text()
			if SigIO == "OUT": SubTypeList = TypeList[2:] # Don't show resets and clocks
			else: SubTypeList = TypeList
			for Type in SubTypeList: Combo.append_text(Type) # Append to combobox
			ComboList.append(Combo)
			HBox.pack_start(Combo, expand=False, fill=False, padding=2)
			VBox.pack_start(HBox, expand=False, fill=False, padding=2)
			Combo.set_active(0)

		Dialog.show_all()
		Dialog.resize(300, 300)
		Response=Dialog.run()
		Dialog.destroy()
		
		SigDict={}
		if Response==Gtk.ResponseType.OK:
			for Type in TypeList: SigDict[Type]=[] # Initialize lists
		
			ResultList = [x.get_active_text() for x in ComboList]
			if len(ResultList)>0:
				for Index in range(0, len(ResultList)):
					 SigDict[ResultList[Index]].append(SignalList[Index])
		return SigDict
		#-------------------------------------------------------------------
		

#======================================================================
	@BugTracking	
	def on_menuitem_resources_activate(self, menuitem_resources):
		if not self.SelectedComponent.IsInLibrary():
			Title = "Add '{0}' to library ?".format(self.SelectedComponent)
			Text  = "To determine resource utilization, '{0}' must be in library.\nDo you want to add it ?".format(self.SelectedComponent)
			if self.Popup(Title, Text, "question")==True: 
				self.SelectedComponent.AddToLib()
			else: return False
		#----------------------------------------------------
		# List of associated FPGA
		FPGAList = self.SelectedComponent.FindFPGA()
		if len(FPGAList)==0:
			self.Popup("No associated architecture found", "No hardware architecture is associated with this design.\nYou can however choose to evaluate resources usage for available FPGA.", "warning")
			DummyFPGA = Components.FPGA(Bundle=self.Bundle)
			DummyFPGA.Library=self.LibPath
			AvailableFPGA = DummyFPGA.GetAvailable()
			FPGADict = {"Target FPGA":AvailableFPGA['FPGA']}
			FPGAList = [x.split()[0] for x in AvailableFPGA['FPGA']]
		else:
			FPGADict = {"Target FPGA":[x.Parameters["Common"]["Name"] for x in FPGAList]}
			FPGAList = [x.Parameters["Common"]["Name"] for x in FPGAList]
			
		#-----------------------------
		if len(FPGAList)==1:
			ChoosenFPGA=FPGAList[0]
		else:
			ChoosenFPGA=self.ChooseValue(FPGADict, Msg="Choose a FPGA for IP implementation :")
		if not ChoosenFPGA: return
		#-----------------------------
		for FPGAName in FPGAList:
			if ChoosenFPGA==FPGAName: 
				break
		# Create temporary folder----------------------------
		TempDir = tempfile.mkdtemp(suffix='.tmp', prefix='YANGO')
		#----------------------------------------------------
		ImplementFlow = self.SelectedComponent.Build(ChoosenFPGA, TempDir)
		if ImplementFlow==None: return False
		self.Run(ImplementFlow, Title="Waits for commands execution", Func=self.SelectedComponent.UpdateResources, Args=[ChoosenFPGA, TempDir,])
		# Schedule to remove temporary folder when closing---
		self.TempDirs.append(TempDir)
		#----------------------------------------------------
		self.ShowComponent(self.SelectedComponent)

#======================================================================
	@BugTracking	
	def OpenSourcesManager(self):
		"""
		Open a dialog to enable user to manage sources (order), add an remove files.
		"""
		logging.debug("GUI: Open sources manager dialog.")
		if self.SelectedComponent.Type=="IP":
			Name = self.SelectedComponent.Parameters["Resources"]["Module"]
		elif self.SelectedComponent.Type=="Library": 
			Name = self.SelectedComponent.Parameters["Common"]["Name"]
		else:
			logging.error("Selected component '{0}' is not an IP: source manager aborted.".format(self.SelectedComponent))
			return
		#-------------------------------------------------------------------
		Title="Manage '{0}' sources (and compilation order)".format(self.SelectedComponent)
		Dialog = Gtk.Dialog(Title, self.MainWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		Dialog.set_has_separator(True)
		VBox = Gtk.VBox()
		VBox.pack_start(Gtk.Label(Title), expand=False, fill=False, padding=5)	
		Dialog.get_content_area().pack_start(VBox, expand=False, fill=False, padding=5)
		#-------------------------------------------------------------------
		# Create a treeview
		ListStore= Gtk.ListStore(int, str)
		TreeView = Gtk.TreeView(ListStore)
		TreeView.get_selection().set_mode(Gtk.SELECTION_SINGLE)
		TreeView.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0))
		TreeView.append_column(Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=1))
		TreeView.set_headers_visible(False)
		TreeView.set_rules_hint(True)
		TreeView.set_reorderable(True)
		TreeView.set_grid_lines(Gtk.TREE_VIEW_GRID_LINES_BOTH)
		TreeView.get_selection().set_mode(Gtk.SELECTION_MULTIPLE)
		
		HBox = Gtk.HBox()
		SW=Gtk.ScrolledWindow()
		SW.add_with_viewport(TreeView)
		HBox.pack_start(SW, padding=7)
		Dialog.get_content_area().pack_start(HBox, padding=7)
		#-------------------------------------------------------------------
		FileListCopy=self.SelectedComponent.Parameters["Resources"]["Sources"][:]
		SigList = []
		TempVar = [Name, SigList, FileListCopy]
		
		#-------------------------------------------------------------------
		def UpdateSrcList():
			ListStore.clear()
			for FPath in TempVar[2]: 
				ListStore.append([TempVar[2].index(FPath), os.path.basename(FPath),])
		#-------------------------------------------------------------------
		def AddSources(AddBtn):
			FList=self.ChoosePath(Multiple=True, Folder= False, Save=False, Parent=Dialog)
			if FList:
				FList=[x for x in FList if x.endswith(".vhd") or x.endswith(".v")]
				TempVar[2]+=FList # FileListCopy
				logging.debug("Add source files: {0}".format(FList))
			UpdateSrcList()
			return True
		#-------------------------------------------------------------------
		def RemoveSources(RmBtn):
			Model, TreePathList = TreeView.get_selection().get_selected_rows()
			Indexes = []
			for TreePath in TreePathList:
				Indexes.append(Model.get_value(Model.get_iter(TreePath), 0))
			for Index in reversed(sorted(Indexes)):
				FPath = TempVar[2].pop(Index) # FileListCopy
				logging.debug("Removed '{0}' source files: {1}".format(self.SelectedComponent, os.path.basename(FPath)))
			UpdateSrcList()
			return True
		#-------------------------------------------------------------------
		def SortSources(SortBtn):
			TreeView.set_sensitive(False)
			SrcList =  [os.path.join(self.LibPath, x) for x in TempVar[2]]
			TempVar[0], TempVar[1], SrcList, Generics = Components.Parse(SrcList)
			TempVar[2] = [os.path.relpath(x, self.LibPath) for x in SrcList]
			UpdateSrcList()
			TreeView.set_sensitive(True)
			return True
		#-------------------------------------------------------------------
		def Move(Btn, Direction):
			Btn.set_sensitive(False)
			Model, TreePathList = TreeView.get_selection().get_selected_rows()
			if len(TreePathList)==1:
				Index = Model.get_value(Model.get_iter(TreePathList[0]), 0)
				if Index < len(TempVar[2]) and Index >= 0:
					if Direction=="DOWN": TargetIndex=min(len(TempVar[2])-1, Index+1)
					else: TargetIndex = max(0, Index-1)
					Swap(TempVar[2], Index, TargetIndex)
					UpdateSrcList()
					TreeView.get_selection().select_iter(Model.get_iter(TargetIndex))
			Btn.set_sensitive(True)
			return True
		#-------------------------------------------------------------------
		UpdateSrcList()
		#-------------------------------------------------------------------
		# Add left button box with button to up/down moving files
		ToolBar = Gtk.Toolbar()
		ToolBar.set_orientation(Gtk.ORIENTATION_VERTICAL)
		ToolBar.set_style(Gtk.TOOLBAR_BOTH)
		ButtonUp   = Gtk.ToolButton(Gtk.STOCK_GO_UP)
		ButtonDown = Gtk.ToolButton(Gtk.STOCK_GO_DOWN)
		ButtonUp.set_visible_vertical(True)
		ButtonDown.set_visible_vertical(True)
#		ButtonUp.set_use_stock(True)
#		ButtonDown.set_use_stock(True)
		ButtonUp.connect(  "clicked", Move, "UP")
		ButtonDown.connect("clicked", Move, "DOWN")
		ToolBar.insert(ButtonUp, 0)
		ToolBar.insert(ButtonDown, 1)
		HBox.pack_end(ToolBar, expand=False, fill=False, padding=2)
		#-------------------------------------------------------------------
		# Add button box with button to add/remove files
		Bbox = Gtk.HButtonBox()
		Bbox.set_layout(Gtk.BUTTONBOX_SPREAD)
		ButtonAdd    = Gtk.Button(stock=Gtk.STOCK_ADD)
		ButtonRemove = Gtk.Button(stock=Gtk.STOCK_REMOVE)
		ButtonSort   = Gtk.Button("Sort (VHDL only)")
		ButtonAdd.connect(   "clicked", AddSources)
		ButtonRemove.connect("clicked", RemoveSources)
		ButtonSort.connect(  "clicked", SortSources)
		Bbox.pack_end_defaults(ButtonAdd)
		Bbox.pack_end_defaults(ButtonRemove)
		Bbox.pack_end_defaults(ButtonSort)
		Dialog.get_content_area().pack_start(Bbox, expand=False, fill=False, padding=5)
		#-------------------------------------------------------------------
		
		Dialog.resize(200, 400)
		Dialog.show_all()
		Response=Dialog.run()
		if Response==Gtk.ResponseType.OK:
			Dialog.destroy()
			self.SelectedComponent.Parameters["Resources"]["Sources"]=TempVar[2]
			SrcList =  [os.path.join(self.LibPath, x) for x in TempVar[2]]
			TempVar[0], TempVar[1], SrcList, Generics = Components.Parse(SrcList[-1:])
			if self.SelectedComponent.Type=="IP":
				self.SelectedComponent.Parameters["Resources"]["Generics"]=Generics
				self.SelectedComponent.Parameters["Resources"]["Module"]=TempVar[0]
				SigDict = self.MapSignals(TempVar[1], ["Resets", "Clocks", "NetworkInterface", "Ports", "Disconnected", "Custom"]) # Mapping dialog
				if SigDict!={}:
					self.SelectedComponent.MapSignals(SigDict) # Mapping parameters
			return
		else:
			Dialog.destroy()
			return
		
#======================================================================	

#----------------------------------------------------------------------
#                           SyntheSys.Utilities
#----------------------------------------------------------------------

#======================================================================	
def Swap(ItemList, IndexA, IndexB):
	"""
	Replace item pointed by IndexA in ItemList by item pointed by IndexB.
	"""
	if IndexA>(len(ItemList)-1) or IndexA<0: 
		logging.error("IndexA({0}) out of range".format(IndexA))
		return
	if IndexB>(len(ItemList)-1) or IndexB<0: 
		logging.error("IndexB({0}) out of range".format(IndexB))
		return
	ItemA = ItemList[IndexA]
	ItemB = ItemList[IndexB]
	ItemList[IndexA]=ItemB
	ItemList[IndexB]=ItemA
	
	
	
	
	
	
	
	



