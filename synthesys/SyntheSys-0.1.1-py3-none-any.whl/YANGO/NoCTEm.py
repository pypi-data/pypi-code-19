#!/usr/bin/python

########################################################################

import os, sys, logging

#try: 
#	from gi.repository import Gtk, Gdk, GLib, Pango
#	from gi.repository.GdkPixbuf import Pixbuf, InterpType
#except ImportError: 
#	import gtk as Gtk
#	import glib as GLib
#	import pango as Pango
#	from gtk import gdk as Gdk
	
import tempfile

from SyntheSys.YANGO import Matrix
from SyntheSys.YANGO import Emulation
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from SyntheSys.SysGen import Simulation

########################################################################
RESPONSE_SIMULATE = -12 
RESPONSE_EMULATE  = -13
########################################################################
def SetTrafficMatrix(IPMatrix):
	"""
	return a matrix with initialized traffic information.
	"""
	DimX, DimY = IPMatrix.Size()
	M = Matrix.Matrix()
	for x in range(DimX):
		for y in range(DimY):
			Item = IPMatrix.Get(x,y)
			if Item:
				M.AddAtPosition({
					"Name":"{0}_x{1}y{2}".format(Item.Parameters["Common"]["Name"],x,y),
					"Position":"{0}:{1}".format(x,y),
					"Targets":{},
					}, x, y)
	
	for x in range(DimX):
		for y in range(DimY):
			Item = M.Get(x,y)
			if Item:
				for Coord, Item in M.BrowseMatrix():
					Item["Targets"][Coord]=0
			
	return M

########################################################################
class NoCTEmDialog(Gtk.Dialog):
	"""
	A dialog for traffic emulation specification for NoC
	"""
	#======================================================================
	def __init__(self, NoCComponent, ParentWindow=None):
		"""
		Initialize widgets and NoC Display in a dialog.
		"""
		self.NoCComponent = NoCComponent
		Gtk.Dialog.__init__(self, "NoC Traffic Emulation", ParentWindow, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT)
		
		# Declare widgets
		Title = Gtk.Label(str="NoC Traffic Emulation")
		self.DrawingArea = Gtk.DrawingArea()
		EventBox = Gtk.EventBox()
		BoxTreeView = Gtk.VBox(homogeneous=False, spacing=0)
		SWinDraw = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		SWinTree = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
		
		#TreeView definition
		self.TreeView = Gtk.TreeView()
		self.ListStore = Gtk.ListStore(str, int)
		self.TreeView.set_model(self.ListStore)
		ColumnRouterName = Gtk.TreeViewColumn("Router")
		ColumnSpinPackets = Gtk.TreeViewColumn("Packet(s)")
		self.TreeView.append_column(ColumnRouterName)
		self.TreeView.append_column(ColumnSpinPackets)
		CellRendererText = Gtk.CellRendererText()
		ColumnRouterName.pack_start(CellRendererText, False)
		ColumnRouterName.add_attribute(CellRendererText, "text", 0)
		CellRendererSpin = Gtk.CellRendererSpin()
		CellRendererSpin.set_property("editable", True)
		CellRendererSpin.set_property("adjustment", Gtk.Adjustment(0, 0, 100, 1, 10, 0))
		ColumnSpinPackets.pack_start(CellRendererSpin, True)
		ColumnSpinPackets.add_attribute(CellRendererSpin, "text", 1)
		
		self.add_button("Simulate", RESPONSE_SIMULATE) 
		self.add_button("Emulate", RESPONSE_EMULATE) 
		self.add_button(Gtk.STOCK_CLOSE, Gtk.RESPONSE_CLOSE) 
		#self.set_modal() 
		
		# Arrange widgets
		Content = self.get_content_area()
		Content.pack_start(Title, expand=False, fill=False, padding=2)
		Content.pack_start(SWinDraw, expand=True, fill=True, padding=2)
		Content.pack_start(SWinTree, expand=True, fill=True, padding=2)
		SWinDraw.add_with_viewport(EventBox)
		SWinTree.add_with_viewport(BoxTreeView)
		EventBox.add(self.DrawingArea)
		BoxTreeView.pack_start(self.TreeView, expand=True, fill=True, padding=2)
		x, y = ParentWindow.get_size()
		SWinDraw.set_size_request(int(x*0.4), int(y*0.3))
		SWinTree.set_size_request(int(x*0.4), int(y*0.3))
		
		#Events connection
		EventBox.connect("button_press_event", self.OnDrawingClick)
		CellRendererSpin.connect("edited", self.SpinChanged)
		self.DrawingArea.connect("expose_event", self.Expose)
		
		
		self.TrafficMatrix = SetTrafficMatrix(NoCComponent.IPMatrix)
		self.SelectedRouter=None
		self.show_all()
		self.SelX, self.SelY = -1, -1
			
	#======================================================================	
	def Expose(self, widget, event):
		"""
		Refresh cairo drawing if the window's size change.
		"""
		# Draw the NoC
		Ctx = self.DrawingArea.window.cairo_create()
		W, H = self.DrawingArea.window.get_size()
		self.W, self.H = self.NoCComponent.Display(Ctx, W, H, Selected=(self.SelX, self.SelY), Ratio=1)
		self.DrawingArea.set_size_request(int(self.W), int(self.H))
		
		return False

	#======================================================================	
	def SpinChanged(self, Widget, Path, Value):
		"""
		Update value matrix with new value.
		"""
		print("SpinChanged")
		self.ListStore[Path][1] = int(Value)
		if self.SelectedRouter!=None:
			self.SelectedRouter["Targets"][self.ListStore[Path][0]]=int(Value)
		
	#======================================================================	
	def OnDrawingClick(self, win, event):
		"""
		Get the position clicked by the mouse, calculate the ID of the clicked router
		Update TreeView using values in matrix
		"""
		if Gtk.events_pending():
			print("Execute first pending events")
			Gtk.main_iteration()
		logging.info("Get the position clicked by the mouse, calculate the router clicked")
		logging.info("Update TreeView using the values in matrix")
		dimension =[]
		
		xsize, ysize = self.TrafficMatrix.Size()
		self.SelX, self.SelY = self.NoCComponent.Drawing.GetSelected(event.x, event.y, ysize-1, Type="NoC", Ratio=1.0)
		self.SelectedRouter = self.TrafficMatrix.Get(self.SelX, self.SelY)
		if self.SelectedRouter==None:
			self.SelX, self.SelY = -1, -1
		self.UpdateTree()
		return 0
		
	#======================================================================	
	def UpdateTree(self):
		""" 
		Update TreeView using the data in the matrix
		"""
#		logging.info("Update TreeView using data in the matrix")
		self.ListStore.clear()	
		if self.SelectedRouter==None: return False
		for (x,y), NbPackets in list(self.SelectedRouter["Targets"].items()):
			self.ListStore.append([self.TrafficMatrix.Get(x,y)["Name"], NbPackets])
	
		self.Expose(self, None)
		return True


#===============================================================================
def TrafficSynthesizer(NoCComponent, MainWindow):
	"""
	Display NoC traffic spec dialog.
	Then fetch specification and return it
	"""
	Dialog = NoCTEmDialog(NoCComponent, MainWindow)
	while(1):
		Response = Dialog.run()
		Latencies=None
		if Response==RESPONSE_SIMULATE:
			logging.info("Choosen: Traffic simulation.")
			OutputPath=tempfile.mkdtemp(suffix='', prefix='TrafficSimulation')
			if not os.path.exists(OutputPath):
				os.makedirs(OutputPath)
			Sim = Simulation.TrafficSimulation(
						TopModule=BuildTop(NoCComponent, Dialog.TrafficMatrix), 
						TrafficMatrix=Dialog.TrafficMatrix, 
						OutputPath=OutputPath)
			#------------------------------------------
			Msg = Sim.Run(Simulator="gHDL") # Run simulation
			MsgDialog = Gtk.MessageDialog(Dialog, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE, "\n{0}\n".format(Msg))
			MsgDialog.set_title(Msg)
			response = MsgDialog.run()
			MsgDialog.destroy() 
			#------------------------------------------
		
			Latencies = Sim.GetLatences()
			GenLatenceFile(Latencies, OutputPath="./")
		
		elif Response==RESPONSE_EMULATE:
			logging.info("Choosen: Traffic emulation.")
			OutputPath=tempfile.mkdtemp(suffix='', prefix='TrafficEmulation')
			if not os.path.exists(OutputPath):
				os.makedirs(OutputPath)
			ArchiList = NoCComponent.FindArchitectures()
			if ArchiList==None: return {}
			else: Archi = ArchiList[0].Parameters["Common"]["Name"]
			Emu = Emulation.TrafficEmulation(
						TopModule=BuildTop(NoCComponent, Dialog.TrafficMatrix), 
						TrafficMatrix=Dialog.TrafficMatrix,
						Architecture=Archi, 
						OutputPath=OutputPath)
			#------------------------------------------
			Msg = Emu.Run(Emulator="AVA-Soft") # Run simulation
			MsgDialog = Gtk.MessageDialog(Dialog, Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE, "\n{0}\n".format(Msg))
			MsgDialog.set_title(Msg)
			response = MsgDialog.run()
			MsgDialog.destroy() 
			#------------------------------------------
		
			Latencies = Emu.GetLatences()
			GenLatenceFile(Latencies, OutputPath="./")
		else:
			logging.info("Close Traffic synthesizer.")
			break
	
	Dialog.destroy()
	return Latencies

#=====================================================================
def GenLatenceFile(Latencies, OutputPath):
	"""
	Create output file and print into this file the specified latencies.
	"""
	FilePath=os.path.join(OutputPath, "Latencies.txt")
	with open(FilePath, "w+") as LFILE:
		for R1, (R2, Licence) in Latencies:
			LFILE.write("{0}=>{1}:{2}".format(R1, R2, Latence))
	return FilePath

#=====================================================================
def BuildTop(NoCComponent, TrafficMatrix):
	"""
	Create a top module that instanciate NoC and its traffic generators and receptors.
	"""
	logging.info("Files generation for traffic synthesis : start.")
	
	NameList=[] # List of IP instance for NoCComponent
	################################################################
	NoCComponent.UpdateModuleParameters()
	# Create a module to add to library (and its associated XML)----
	Infos = {}
	TopName = "TrafficSynthesizer"
	Infos["Name"]=TopName
	Infos["Version"]="1.0"
	Infos["Title"]="Traffic synthesis platform"
	Infos["Purpose"]= "Generate traffic inside a network and calculate latencies."
	Infos["Desc"]= "Generate traffic inside a network and calculate latencies."
	Infos["Tool"]="Xilinx 13.1"
	Infos["Area"]=""
	Infos["Speed"]=""
	Infos["Issues"]=""
	
	TopModule = LibManager.NewModule(
				Infos  = Infos, 
				Params = [],  # TODO: Get proper signals 
				Ports  = [],  # TODO: Get proper signals 
				Clocks = [],  # TODO: Get proper signals 
				Resets = [],  # TODO: Get proper signals
				)
	LibManager.AddModule(TopModule) 
	
	# Generate file for this NoC -----------------------------------
	logging.info("Generates files for '{0}'.".format(NoCComponent))
	NoCServ = NoCComponent.Parameters["Common"]["Service"]
	NoCInterfaces = NoCServ.GetInterfaces(NoCComponent.Parameters["Common"]["Interface"])
	
	InstName = InstanceName(NoCServ.Name, NameList)
	NameList.append(InstName)
	NoCServ.Alias=InstName
	XMLServNoC=TopModule.AddXMLServ(NoCServ, InstName)
	# Set NoC service parameters -----------------------------------
	for PName in NoCServ.Params:
		# Get component parameter value
		for CParam in NoCComponent.Parameters["Common"]["Generics"]:
			if CParam.Name == PName:
				TopModule.MapServParam(NoCServ, PName, CParam.Default)
				break
	IOMapList = [] # FPGA IO pad connections
	for PositionTuple, RouterDict in TrafficMatrix.BrowseMatrix():
		Targets = RouterDict["Targets"]
		for (x,y) in Targets:
			break
		Header = NoCComponent.GenHeader(TrafficMatrix.Get(x,y)["Position"])
		FlitWidth = NoCComponent.Parameters["Parent"]["FlitWidth"]
	
		
		TGInstName = InstanceName(RouterDict["Name"].replace('(','_').replace(')','_')+"_TG", NameList)
		TRInstName = InstanceName(RouterDict["Name"].replace('(','_').replace(')','_')+"_TR", NameList)
		NameList.append(TGInstName)
		NameList.append(TRInstName)
		TGServ = LibManager.GetService("TrafficGenerator", ServiceAlias=TGInstName)
		TRServ = LibManager.GetService("TrafficReceptor", ServiceAlias=TRInstName)
		
		#IOMapList = IPChild.Generate(Header=Header, FlitWidth=FlitWidth) # TODO: set all kind of generics
		if TGServ==None or TRServ==None:
			logging.error("Service '{0}' or '{1}' not found ! Unable to fetch it in library.".format(TGServ, TRServ))
			return None 
		
		# Connect IP with NoC --------------------------------------
		TGInterfaces = TGServ.GetInterfaces(NoCComponent.Parameters["Common"]["Interface"])
		TRInterfaces = TRServ.GetInterfaces(NoCComponent.Parameters["Common"]["Interface"])
		XMLServIP=TopModule.AddXMLServ(TGServ, TGInstName)
		XMLServIP=TopModule.AddXMLServ(TRServ, TRInstName)
		
		DimX, DimY = list(map(int, NoCComponent.Parameters["Common"]["Dimensions"].lower().split('x')))
		# Set TG/TR parameters -----------------------------------
		Params = {"FlitWidth":FlitWidth, "NbRouters":DimX*DimY, "LocalAddr_x":DimX, "LocalAddr_y":DimY}
		for PName, Val in list(Params.items()):
			if PName in TGServ.Params:
				TopModule.MapServParam(TGServ, PName, Val)
			if PName in TRServ.Params:
				TopModule.MapServParam(TRServ, PName, Val)
			break
			
		# Set TG variables ---------------------------------------
		for TGConfItf in TGServ.GetInterfaces("TGConfig"):
			TopModule.SpreadUpward(ModInterface=TGConfItf, Prefix="")
		# Set TR variables ---------------------------------------
		for TRConfItf in TRServ.GetInterfaces("TRConfig"):
			TopModule.SpreadUpward(ModInterface=TRConfItf, Prefix="")
			
		# Connect TG/TR to network -------------------------------
		ItfLinks = []
		for TGItf in TGInterfaces:
			for NoCItf in NoCInterfaces:
				if TGItf.IsCompatibleWith(NoCItf):
					ItfLinks.append( (TGItf, NoCItf) )
					break
		for TRItf in TRInterfaces:
			for NoCItf in NoCInterfaces:
				if TRItf.IsCompatibleWith(NoCItf):
					ItfLinks.append( (TRItf, NoCItf) )
					break
		
		# Link network interfaces
		Position = Pos2Number(RouterDict["Position"], NoCComponent.Parameters["Common"]["Dimensions"])
		for IPItf, NetItf in ItfLinks:
			TopModule.Connect(NetItf[Position], IPItf)
			
			
	LibManager.AddModule(TopModule) # Update module in library
			  
#	SourcesList = TopModule.GetSources(Synthesizable=True, IsTop=True)
#	SourcesList = map(lambda x: os.path.join(SrcDir, os.path.basename(x)) if os.path.isfile(x) else os.path.join(SrcDir, x), SourcesList)
	
	#---------------------------------------------------------------
	      
	return TopModule



#======================================================================
def Pos2Number(Position, Dimensions):
	"""
	Return a Dictionary (and comment) built from XML elementTree object.
	"""
	try: x, y = [int(x) for x in Position.split(':')]
	except:
		logging.error("Bad format for IP position ('{0}') expected format '[integer]:[integer]'.")
		return None
	try: DimX, DimY = [int(x) for x in Dimensions.split('x')]
	except:
		logging.error("Bad format for IP position ('{0}') expected format '[integer]:[integer]'.")
		return None
	
	return y*DimX+x


#=======================================================================
def InstanceName(BaseName, NameList):
	"""
	Return a new name that is not in the list.
	"""
	N=0
	while(BaseName+'_'+str(N) in NameList): N+=1
	return BaseName+'_'+str(N)


















