
import sys, os, logging, re
import math
from lxml import etree
import networkx as nx
import collections

from HdlLib import Drawing
from SyntheSys.YANGO import NoCMapping
from SyntheSys.YANGO import Matrix  
#from SyntheSys.YANGO import FPGABuilder
from SyntheSys.YANGO import IPGen
from SyntheSys.YANGO import Constraints
from SyntheSys.YANGO import SoCConfig
from SyntheSys.YANGO import NoCFunctions, MapUtils

from SyntheSys.Utilities import Timer, Misc
from SyntheSys.Utilities.Misc import SyntheSysError

			
from SysGen.Service import Service
from SysGen.Signal import Signal
from SysGen import Module as ICModule
from SysGen import LibEditor
from SysGen.Module import Instance
from SysGen.Protocol import DirectedProtocol
from SysGen.Interface import Interface
from SysGen.HW import HwModel

#======================================================================
class TreeMember:
	"Tree for new design"
	#----------------------------------------------------------------------
	def __init__(self, Library, Type, Name = None, Parent = None, Bundle=None):
		"""
		Abstract class initialization.
		"""
		self.Type        = Type
		self.Parent      = Parent
		self.Icon        = None
		self.TreePath    = None # Parameter set by the GUI to find component faster
		self.ExpandState = True # Used to save the treeview state (GUI)
		self.ChildLists  = {} # Dictionary of child lists 
		self.SaveXML     = True
		self.Drawing     = None
		#---
		self.Parameters={
			"Common"    : {"Name":Name, "Comments":""}, # Common to this component family parameters dictionary (Editable)
			"Parent"    : {}, # Set by parents parameters dictionary (Editable)
			"Resources" : {}, # Calculated parameters dictionary (Not manually editable)
			} 
		#---
		if Library: self.Library=Library
		elif self.Parent: self.Library=self.Parent.Library
		else: logging.error("{0} has no parent: creation failed.".format(self))
		if Bundle!=None: 
			self.Bundle = Bundle
#			logging.debug("New bundle: {0}".format(Bundle))
		else: 
			if Parent!=None: self.Bundle = Parent.Bundle
			else: self.Bundle = Bundle # i.e. None
			
#		if self.Bundle!=None:
#			self.Drawing  = Drawing.Drawing() 
#			Drawing.AdacsysLogo=self.Bundle.Get("adacsys_logo.png")
#		logging.debug("New TreeMember : [{0}] (Parent={1}): Bundle:{2}".format(self, Parent, self.Bundle))
	#----------------------------------------------------------------------
	def SetBundle(self, Bundle):
		"""
		Set bundle attribute of treemember and its children.
		"""
		self.Bundle=Bundle
		self.SetIcon()
		if not self.Bundle is None:
			self.Drawing  = Drawing.Drawing() 
			Drawing.AdacsysLogo=self.Bundle.Get("adacsys_logo.png")
		else:
			logging.error("No bundle specified : unable to draw.")
			sys.exit(1)
		for Type, Children in self.ChildLists.items():
			for Child in Children:
				Child.SetBundle(Bundle)
				Child.SetIcon()
	#----------------------------------------------------------------------
	def GetParent(self, Type=None):
		"""
		Return Tree parent of this element.
		"""
		if Type:
			if isinstance(self.Parent, Type):
				return self.Parent
			else:
				if self.Parent != None:
					return self.Parent.GetParent(Type)
				else:
					return None
		else: return self.Parent
	#----------------------------------------------------------------------
	def Get(self, TreePath):
		if(self.TreePath==TreePath):
			return self # return itself
		else:
			ChildList=[]
			for Key in list(self.ChildLists.keys()):
				ChildList+=self.ChildLists[Key]

			for item in ChildList:
				ret = item.Get(TreePath)
				if(ret): return ret # return children of children
			return None
	#----------------------------------------------------------------------
	def  GetAvailable(self):
#		logging.debug("List available items ('{0}') in library :".format(self.Type))
		if self.Type=="IP":
			AvailableList = self.Library.ListModules()
			return {self.Type:AvailableList}
		else:
			#Get the root node
			#Root = Tree.getroot()
			LibraryFile = os.path.join(self.Library, self.Type.upper()+".xml")
			if os.path.isfile(LibraryFile):
				Tree = etree.parse(LibraryFile)
			else:
				logging.error("Library file '{0}' not found. Unable to retrieve information from {1} library.".format(os.path.join(self.Library, self.Type.upper()+".xml"), self.Type)) 
				return {self.Type:[]}
				
			#Get a list of children elements with the type of component as tag
			AvailableList = Tree.iter(self.Type)

			return {self.Type:["{0}".format(x.attrib["Name"])+ ("({0})".format(str(x.text).strip().strip('\n').strip()) if str(x.text).strip().strip('\n').strip()!="" else "") for x in AvailableList]} # Append a comment (text) to the name between brackets
	#----------------------------------------------------------------------
	def AvailableValues(self, Parameter):
		"""
		Return available TreeMember parameter values in a list.
		"""
		return {Parameter:[]}
	#----------------------------------------------------------------------
	def CheckParameters(self):
		WrongParamList = []	
		for Key in list(self.Parameters.keys()):
			for Param in list(self.Parameters[Key].keys()):
				Availables = self.AvailableValues(Param)
				AvTypes = sorted(Availables.keys())
				if not len(AvTypes): return WrongParamList
				for AvType in AvTypes:
					if Availables[AvType]==[]: pass
					elif not Availables[AvType].count(self.Parameters[Key][Param]):
						WrongParamList.append([Key, Param, Availables[AvType]])
		return WrongParamList
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if Parameter == "Name":
			OldName = self.Parameters[ParameterType][Parameter]
			self.Parameters[ParameterType][Parameter] = OldName.replace(' ', '_')
			if not re.match("[a-zA-Z0-9_]\w*", self.Parameters[ParameterType][Parameter]):
				return False
		return True
	#----------------------------------------------------------------------
	def SetFromLib(self, Value):
		"""
		Get information from library item and set IP parameters.
		"""
		logging.error("Unsupported function 'SetFromLib' for TreeMember '{0}'.".format(self))
#		TreeElmt = etree.parse(os.path.join(self.Library, self.Type.upper()+".xml"))
#		#Get a list of children elements with the type of component as tag
#		for Element in TreeElmt.iter(self.Type):
#			if Element.attrib.get("Name") == Value: # Find specified Name
#				# First get the Resources----------------------------------
#				ResourcesElmt=Element.find("Resources")
#				if ResourcesElmt is not None: 
#					RscDict = Elmt2Dict(ResourcesElmt)
#					self.Parameters["Resources"].update(RscDict)
#					#if Comments: self.Parameters["Resources"]["Comments"]=Comments
#					#Element.Remove(ResourcesElmt)
#				else: logging.warning("No '{0}' child in XML file for '{1}': ignoring.".format(Param, Value))
#				
#				# Next let's consider the children-------------------------
#				for Type in self.ChildLists.keys():
#					# Remove all previous children
#					while(len(self.ChildLists[Type])): self.ChildLists[Type][0].Remove()
#					# Recreate all new children
#					ChildElmts=[]
#					for ChildElement in Element.iterchildren(Type):
##						logging.debug("New child '{0}' for '{1}'".format(ChildElement.attrib["Name"], self))
#						Child = self.AddChild(Type=Type, Name=ChildElement.get("Name"), FromLib=True)
#						if not Child: logging.error("This element '{0}' cannot have a child.'".format(self))
#						else: 
#							ParentElmt=ChildElement.find("Parent")
#							if ParentElmt is not None: 
#								ParDict=Elmt2Dict(ParentElmt)
#								Child.Parameters["Parent"].update(ParDict)
#								#if Comments: Child.Parameters["Parent"]["Comments"]=Comments 
#							else: logging.warning("No 'Parent' child in XML file for '{1}': ignoring.".format(Param, Value))
#						ChildElmts.append(ChildElement)
#					#for Elmt in ChildElmts:
#					#	Element.Remove(Elmt)
#							
#				# finally get the common parameter and the comments---------
#				#CommonDict, Comments = Elmt2Dict(Element)
#				self.Parameters["Common"].update(FromXMLAttribute(Element.attrib))
#				#self.Parameters["Common"]["Comments"]=Element.text	
#							
#				return True
#		logging.warning("Item '{0}' not in library : ignoring.".format(Value))		
		return False
	#----------------------------------------------------------------------
	def IsInLib(self):
		XMLFile = os.path.join(self.Library, self.Type.upper()+".xml")
		if os.path.exists(XMLFile): # Fetch already recorded content
			TREE = etree.parse(XMLFile)
			# Get a list of children elements with the type of component as tag
			for Element in TREE.iter(self.Type):
				# Check if it is already there
				if Element.attrib.get("Name") == self.Parameters["Common"]["Name"]:
					return True
		return False
	#----------------------------------------------------------------------
	def AddToLib(self):
		XMLFile = os.path.join(self.Library, self.Type.upper()+".xml")
		if os.path.exists(XMLFile): # Fetch already recorded content
			TREE = etree.parse(XMLFile)
			# Create a new element and add all Common parameters + comments-------
			Root = TREE.getroot()
			#NewElement = etree.SubElement(Root, tag=str(self.Type), attrib=self.Parameters["Common"])
			NewElement = XMLElmt(self.Type, self.Parameters["Common"], Root)
			#TREE.getroot().append(NewElement)
			
		else: # If no library file is found, create a new xml tree and add all Common parameters + comments-------
			Root = XMLElmt("{0}s".format(self.Type), self.Parameters["Common"])
			NewElement = XMLElmt(self.Type, self.Parameters["Common"], Root)
			#NewElement = etree.SubElement(Root, self.Type, self.Parameters["Common"])
			TREE=Root
			#NewElement = XMLElmt(self.Type, self.Parameters["Common"])
			#TREE.getroot().append(NewElement)

		# Append component children to the new element------------------------
		for Key in list(self.ChildLists.keys()):
			for Child in self.ChildLists[Key]:
				if Child.SaveXML==True:
					# XML child has only the 'Name' attribute
					ParamDict={	"Name":   Child.Parameters["Common"]["Name"], 
							"Parent": Child.Parameters["Parent"]}
					ChildElement = XMLElmt(Child.Type, ParamDict, NewElement)
			
		# Append resources child----------------------------------------------
		RscElement = XMLElmt("Resources", self.Parameters["Resources"], NewElement)
		
		# Write on the xml file-----------------------------------------------
		with open(XMLFile, "w+") as XMLFILE:
			XMLFILE.write(etree.tostring(TREE, encoding="UTF-8", pretty_print=True))
		logging.debug("Added '{0}' to '{1}' library.".format(self.Parameters["Common"]["Name"], self.Type))
		return True
	#----------------------------------------------------------------------
	def UpdateLibElement(self):
		logging.debug("Update '{0}' in '{1}' library.".format(self.Parameters["Common"]["Name"], self.Type))
		if self.IsInLib():
			if self.RemoveLibElement(self.Parameters["Common"]["Name"])==True:
				self.AddToLib()
			else:
				logging.error("Unable to remove element '{0}' from library.".format(self.Parameters["Common"]["Name"]))
				return
		else:
			logging.error("Unable to update element '{0}' because not in library.".format(self.Parameters["Common"]["Name"]))
	#----------------------------------------------------------------------
	def RemoveLibElement(self, ElementName):
		logging.debug("Remove '{0}' from '{1}' library.".format(self.Parameters["Common"]["Name"], self.Type))
		TREE = etree.parse(os.path.join(self.Library, self.Type.upper()+".xml"))

		#Get a list of children elements with the type of component as tag
		for Element in TREE.iter(self.Type):
			# Check if it is already there
			if Element.attrib["Name"] == ElementName:
				Element.getparent().remove(Element)
				# Write on the xml file-----------------------------------------------
				with open(os.path.join(self.Library, self.Type.upper()+".xml"), "w+") as XMLFILE:
					XMLFILE.write(etree.tostring(TREE, encoding="UTF-8", pretty_print=True))
				logging.info("Removed '{1}' from {0} library.".format(self.Type, ElementName))	
				return True
		return False
	#----------------------------------------------------------------------
	def IsInLibrary(self, CompName):
		"""
		Parse XML file to find if component is already saved in library.
		"""
		TREE = etree.parse(os.path.join(self.Library, self.Type.upper()+".xml"))
		# Get the root node
		#Root = Tree.getroot()
		# Get the list of children elements with the type of component as tag
		for Element in TREE.iter(self.Type):
			if Element.attrib["Name"] == CompName:
				return True
		return False
	#----------------------------------------------------------------------
	def Remove(self):
		if self.Parent==None: 
			logging.warning("This child has no parent: nothing removed.")
			return
		for ListName in list(self.Parent.ChildLists.keys()):
			if self.Parent.ChildLists[ListName].count(self):
				self.Parent.ChildLists[ListName].remove(self)
				logging.debug("'{0}' removed.".format(self))
				return
		logging.warning("'{0}' Not found in its parent ('{1}') child lists.".format(self, self.Parent))
		return
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height):
		"""
		By default draw only background. 
		"""
		if self.Drawing:
			self.Drawing.Ctx=Ctx
			self.Drawing.BackGround(Width=Width, Height=Height)
	#----------------------------------------------------------------------
	def __repr__(self):
		return "{1}({0})".format(self.Type, self.Parameters["Common"]["Name"])
	#----------------------------------------------------------------------
	def __str__(self):
		return "{0}".format(self.Parameters["Common"]["Name"])

#======================================================================
class App(TreeMember):
	"""
	Application tree member.
	"""
	#----------------------------------------------------------------------
	def __init__(self, Library, Name = "User_Application", Parent = None, Bundle=None):
		TreeMember.__init__(self, Library, "Application", Name, Parent, Bundle)
		self.SetIcon()
		self.ChildLists["Algorithm"]=[] # list algorithm objects
		self.ChildLists["Architecture"]=[] # list of Architecture(Arch) objects
		self.ChildLists["IP"]=[] # list IP objects
		self.ChildLists["NoC"]=[] # list NoC objects
		self.InitParameters(Name)
		self.APCG=None
		self.APCGImagePath = self.Parameters["Common"]["Name"]+".svg"
		self.PartitionMatrix=Matrix.Matrix()
	#----------------------------------------------------------------------
	def GetName(self):
		"""
		return application name.
		"""
		return self.Parameters["Common"]["Name"]
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("App.png")
		except: self.Icon = ""
		self.IconSize = (25, 25)
	#----------------------------------------------------------------------
	def InitParameters(self, Name):
		self.Parameters["Common"].update({ # Value => list of choices
			"Author" : "",
			"Version": "0.01",
	                "Title"  : "", 
	                "Tool"   : "ISE 13.1", 
	                "Purpose": "", 
	                "Desc"   : "", 
	                "Title"  : "", 
	                "Area"   : "", 
	                "Speed"  : "", 
	                "Issues" : "",
	                "Sources" : [],
			})
		self.Parameters["Resources"].update({ # Value => list of choices
			"Packages": [],
			})
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		return True
	#----------------------------------------------------------------------
	def OptimizeParameters(self, NbInput=16, ComCoordinates=None):
		"""
		Define FlitWidth parameters.
		"""
		if ComCoordinates is None:
			logging.error("[YANGO.Component.OptimizeParameters] Impossible to optimize parameters without no communication module's coordinates.")
			sys.exit(1)
		NoC=self.ChildLists["NoC"][0] # Only one NoC
		SizeX, SizeY=NoC.IPMatrix.Size()
		
		IPList=[M for M in NoC.ChildLists["IP"]]
		ModList=[IP.Parameters["Common"]["Service"] for IP in IPList if not (IP is None)]
		FlitWidth=NoCMapping.SetupFlitWidth(ModuleList=ModList)
		def ArrondiPuissanceSup(N, Base):
			for P in [pow(2,i) for i in range(50)]:
				if P>=N: return P
			raise SyntheSysError("Cannot find power of two higher than '{0}'".format(N))
		
		InputFifoDepth_Table=[1024 for i in range(SizeX*SizeY)]
		ComPos=Pos2Number("{0}:{1}".format(*ComCoordinates), "{0}x{1}".format(SizeX, SizeY))
		InputFifoDepth_Table[ComPos]=ArrondiPuissanceSup(2*NbInput, 2)
#		print("SizeX, SizeY:", *ComCoordinates)
#		print("ComPos:", ComPos)
#		print("InputFifoDepth_Table:", InputFifoDepth_Table)
#		input()
		ParamDict={
			"InputFifoDepth_Table" : InputFifoDepth_Table,
			"FlitWidth"      : FlitWidth,
			"NbOutputs_Table":[5 for i in range(SizeX*SizeY)],
			"NbInputs_Table" :[5 for i in range(SizeX*SizeY)],
			"Lanes"          :"1",
			"Routing"        :"XY",
			"Scheduling"     :"Priority",
#			"Dimensions":"3x3",
#			"OutputFifoDepth_Table":[32 for i in range(SizeX*SizeY)],
			}
#		for NoC in self.ChildLists["NoC"]: # list NoC objects
		for PName, PVal in ParamDict.items():
			NoC.SetParameter(PName, PVal)
		# Optimize FlitWidth
		for IP in self.ChildLists["IP"]: # list IP objects
			for PName, PVal in ParamDict.items():
				IP.SetNetworkParameter(PName, PVal)
		return ParamDict
	#----------------------------------------------------------------------
	def SetFromLib(self, Value):
		"""
		Get information from library item and set IP parameters.
		"""
#		TreeMember.SetFromLib(self, Value) # Add all children
		
		# Move each child to its recorded position if not already
		for Type, ChildrenList in self.ChildLists.items():
			if Type in ["NoC", "IP"]:
				for Child in ChildrenList:
					xChild, yChild = list(map(int, Child.Parameters["Parent"]["Position"].split(':')))
					xCur, yCur = self.PartitionMatrix.AddToMatrix(Child)
					if xChild!=xCur or yChild!=yCur:
						self.PartitionMatrix.MoveInMatrix(Child, xChild, yChild)
		self.PartitionMatrix.Shrink()
	#----------------------------------------------------------------------
	def GetTop(self):
		"""
		return Top EntityName + Top Path.
		"""
		if not "Module" in self.Parameters["Common"]: 
			logging.error("[GetTop] No module associated with application '{0}'".format(self))
			return None
		return self.Parameters["Common"]["Module"].GetTop()
	#----------------------------------------------------------------------
	def GetModule(self):
		"""
		return SyntheSys.SysGen.module associated with this application.
		"""
		Mod=self.Parameters["Common"]["Module"]
		if Mod is None:
			logging.error("No module associated with application {0}".format(self))
		return Mod
	#----------------------------------------------------------------------
	def GetClockNames(self):
		"""
		return list of clock names.
		"""
		if not "Module" in self.Parameters["Common"]: 
			logging.error("[GetClocks] No module associated with application '{0}'".format(self))
			return None
		return self.Parameters["Common"]["Module"].GetClockNames()
	#----------------------------------------------------------------------
	def GetStimuliNames(self):
		"""
		return list of Stimuli names.
		"""
		if not "Module" in self.Parameters["Common"]: 
			logging.error("[GetStimuli] No module associated with application '{0}'".format(self))
			return None
		return self.Parameters["Common"]["Module"].GetResetNames()+self.Parameters["Common"]["Module"].GetStimuliNames()
	#----------------------------------------------------------------------
	def GetTraceNames(self):
		"""
		return list of Trace names.
		"""
		if not "Module" in self.Parameters["Common"]: 
			logging.error("[GetTrace] No module associated with application '{0}'".format(self))
			return None
		return self.Parameters["Common"]["Module"].GetTraceNames()
	#----------------------------------------------------------------------
	def GetPorts(self, Direction=None):
		"""
		return list of clock names.
		"""
		if Direction is None:
			return self.Parameters["Common"]["Module"].GetPortsDict()
		else:
			Ports=self.Parameters["Common"]["Module"].GetPortsDict()
			PDict=collections.OrderedDict()
			for Name,Sig in Ports.items():
				if Sig.Direction==Direction:
					PDict[Name]=Sig
			return PDict
	#----------------------------------------------------------------------
	def GetPEs(self):
		"""
		Return a list of modules used by this application.
		"""
		PEs=[]
		for IP in self.ChildLists["IP"]: # list IP objects
			PEs.append(IP.GetModule())
		return PEs
	#----------------------------------------------------------------------
	def GenerateHDL(self, OutputPath, TBValues={}, TBClkCycles=1600, CommunicationService=None, ComAddress=(0,0), HwConstraints=None):
		"""
		Generate output files for choosen application and architecture.
		"""
		logging.debug("Files generation for application '{0}'...".format(self))
		if not os.path.isdir(str(OutputPath)):
			logging.error("Unable to generate files for application: incorrect output directory '{0}'.".format(str(OutputPath))) 
			return None
		
		AppM = Matrix.Matrix(NbElement=len(self.ChildLists["NoC"]))
#		AppPath = OutputPath #os.path.join(OutputPath, self.Parameters["Common"]["Name"])
		for Index, NoCChild in enumerate(self.ChildLists["NoC"]): # TODO Only one NoC
			NameList=[] # List of IP instance for NoCChild (AppModule)
			################################################################
			# Create a module to add to library (and its associated XML)----
			NoCChild.UpdateModuleParameters()
			Infos         = self.Parameters["Common"].copy()
			TopName       = self.Parameters["Common"]["Name"]#+"_FPGA_{0}".format(Index)
			Infos["Name"] = TopName
			AppModule  = LibEditor.NewModule(	
						Infos  = Infos, 
						Params = [],  # TODO: Get proper signals 
						Ports  = [],  # TODO: Get proper signals 
						Clocks = [],  # TODO: Get proper signals 
						Resets = [],  # TODO: Get proper signals
			                        )
			# Set NoC service parameters -----------------------------------
			NoCMap=collections.OrderedDict()
			NoCServ = NoCChild.Parameters["Common"]["Service"]
			for PName, NoCParam in NoCServ.Params.items():
				# Get component parameter value
				if PName in NoCChild.Parameters["Common"]:
					DefaultValue=NoCChild.Parameters["Common"][PName]
				elif PName in NoCChild.Parameters["Common"]["Generics"]:
					DefaultValue=NoCChild.Parameters["Common"]["Generics"][PName].Default  
				else: DefaultValue=None
				AppParam=NoCChild.Parameters["Common"]["Generics"][PName].Copy()
				AppParam.Default=DefaultValue
				AppModule.Params[PName]=AppParam
				NoCMap[PName]=[[("", PName, None)], True, None]
				AppModule.Vars[PName]=DefaultValue
#				print("PName:", PName)
#				print("DefaultValue:", DefaultValue)
#				print("NoCParam:", NoCParam)
#				print("NoCParam.Value:", NoCParam.Value)
#				print("NoCParam.Default:", NoCParam.Default)
				NoCParam.SetValue(DefaultValue)
				NoCParam.SetDefault(DefaultValue)
			
			self.Parameters["Common"]["Module"]=AppModule
			
			# Generate file for this NoC -----------------------------------
			NoCInterfaces = NoCServ.GetInterfaces(NoCChild.Parameters["Common"]["Interface"])
			
			NoCInstName = InstanceName(NoCServ.Name, NameList)
			NameList.append(NoCInstName)
			NoCServ.Alias=NoCInstName
			IPServList=[]
			IPModList=[]
			ServMappingList=[]
			
			ModList=[IP.Parameters["Common"]["Module"] for IP in NoCChild.ChildLists["IP"]]
			ModList=[M for M in ModList  if not (M is None)]
			FlitWidth=NoCMapping.SetupFlitWidth(ModuleList=ModList)
			SubstituteClk, SubstituteRst=None, None
			for IPChild in NoCChild.ChildLists["IP"]:
				TargetHeader = NoCChild.GenHeader(IPChild.Parameters["Parent"]["Target"])
				IPChild.Parameters["Parent"]["FlitWidth"]=FlitWidth
				
				Position=Pos2Number(IPChild.Parameters["Parent"]["Position"], NoCChild.Parameters["Common"]["Dimensions"])
				NoCInterfaces=[x[Position] for x in NoCInterfaces]
				
				IPMod, IPServ, ServNoCMapping, ServMapping, WrappedMod = IPChild.Generate(NameList, NoCInterfaces, Position, TargetHeader, FlitWidth, CommunicationService, OutputPath=OutputPath)
				if None in (IPMod, IPServ):
					logging.error("IP '{0}' not wrapped. NoC generation aborted.".format(IPChild))
					return False
				NoCMap.update(ServNoCMapping)
				
				#---------------------------------------
				NonWrappedServ=IPChild.Parameters["Common"]["Service"]
				if not (NonWrappedServ is CommunicationService):
					HardParameters={
						"ComHeader"      : NoCChild.GenHeader(ComAddress),
						"PipelineLength" : IPChild.GetPipelineLength(), 
						}
					if NonWrappedServ.Name=="Reduce":
						HardParameters["NbInputMax"]=63
					for PName, P in IPServ.Params.items():
						if not (PName in HardParameters) and not (PName in AppModule.Params):
							NewParam=P.Copy()
							DefaultValue=NewParam.GetValue()
							NewParam.SetValue(DefaultValue)
							NewParam.SetDefault(DefaultValue)
	#						AppModule.Params[PName]=NewParam
	#						AppModule.Vars[PName]=DefaultValue
							ServMapping[PName][0][0][1]=str(DefaultValue)
					for PName, Val in HardParameters.items():
						if PName in ServMapping:
							ServMapping[PName][0][0][1]=str(Val)#IPServ.Params[PName].GetValue()
				#---------------------------------------
						
				ServMappingList.append(ServMapping)
				if IPServ is None:
					logging.error("No service associated with node '{0}'. Unable to generate node: skipped.".format(IPChild))
					Answer=''
					while not(Answer in ['y', 'n']):
						Answer=input("Continue ? y/n : ").lower()
					if Answer=='y': continue
					else: sys.exit(1)
					
				NameList.append(IPServ.Alias)
#				# Connect IPs to NoC ---------------------------------------
#				NetworkInterfaces = IPServ.GetInterfaces(IPChild.Parameters["Common"]["Interface"])
#				ExtInterfaces = filter(lambda x: x not in NetworkInterfaces, IPServ.GetInterfaces())
#				# Link external interfaces
#				for ExtItf in ExtInterfaces:
#					AppModule.SpreadUpward(ExtItf)
				#---------------------
				IPServList.append(IPServ.Copy())
				IPModList.append(WrappedMod)
				#---------------------
				
				# Manage clocks/reset from communication element
				if IPServ is CommunicationService:
					if 'userclock' in IPMod.ProvidedServ:
						logging.debug("Clock provided by communication element ('{0}')".format(IPMod.Name))
						SubstituteClk=IPMod.ProvidedServMap['userclock']['clock']
					if 'userreset' in IPMod.ProvidedServ:
						logging.debug("Reset provided by communication element ('{0}')".format(IPMod.Name))
						SubstituteRst=IPMod.ProvidedServMap['userreset']['reset']
			
			
			MappingList=[NoCMap,]+ServMappingList
			IPServList.insert(0, NoCServ.Copy())
			IPModList.insert(0, NoCServ.GetModule()) 
			if SubstituteClk:
				for i, Mapping in enumerate(MappingList):
					if IPServList[i].Name==CommunicationService.Name: 
						Mapping[SubstituteClk]=([[CommunicationService.Alias, SubstituteClk, None],], True, {})
					else:
						if IPModList[i].IsAbstract():
							Mapping['clock']=([[CommunicationService.Alias, SubstituteClk, None],], True, {})
						else:
							for CName in IPModList[i].GetClockNames():
								if not (CName in IPModList[i].Ports): continue
								Mapping[CName]=([[CommunicationService.Alias, SubstituteClk, None],], True, {})
			if SubstituteRst:
				for i, Mapping in enumerate(MappingList):
					if IPServList[i].Name==CommunicationService.Name: 
						Mapping[SubstituteRst]=([[CommunicationService.Alias, SubstituteRst, None],], True, {})
					else:
						if IPModList[i].IsAbstract():
							Mapping['reset']=([[CommunicationService.Alias, SubstituteRst, None],], True, {})
						else:
							for RName in IPModList[i].GetResetNames():
								if RName not in IPModList[i].Ports: continue
								Mapping[RName]=([[CommunicationService.Alias, SubstituteRst, None],], True, {})
					
			
			AppModule.MapSubServices(Services=IPServList, Mappings=MappingList)
			AppModule.Reload()
			self.Library.AddModule(AppModule) # Update module in library

			# Generate sources----------------------------------------------
			TopInstance=Instance(Name="DUT_"+AppModule.Name, Mod=AppModule)
			#---------------------
			
			SourcesList = AppModule.GenSrc( 
						Synthesizable = True, 
						OutputDir     = OutputPath, 
						TestBench     = True, 
						IsTop         = True,
						ModInstance   = TopInstance,
						TBValues      = TBValues,
						TBClkCycles   = TBClkCycles,
						CommunicationService=CommunicationService,
						HwConstraints = HwConstraints
						)

			self.Parameters["Common"]["Module"]=AppModule
			self.Parameters["Common"]["Instance"]=TopInstance
			self.Parameters["Common"]["Sources"]=SourcesList
					  
			logging.debug("Sources generated:")
			for S in SourcesList:
				logging.debug("\t{0}".format(os.path.abspath(S)))
			
			#---------------------------------------------------------------
			DepDict = AppModule.GetDependencies()
#			NoCChild.ImplementParameters={
#				"TopName" : TopName, 
#				"DepDict" : DepDict, 
#				"Sources" : SourcesList, 
#				"Path"    : AppSubPath, 
#				"IOs"     : [],  
#			}
#			AppM.AddToMatrix(ParmTuple)
#			x, y = map(int, NoCChild.Parameters["Parent"]["Position"].split(':'))
#			AppM.MoveInMatrix(ParmTuple, x, y)
			#---------------------------------------------------------------
		return True
	#----------------------------------------------------------------------
	def Synthesize(self, SrcDirectory, OutputPath, ControlHW=None, RemoteHost=None):
		"""
		Implement choosen application on target architecture.
		"""
		############################################################################
		# Generate the Architecture specific binary files from HDL src-------------
		if len(self.ChildLists["Architecture"])==0:
			logging.error("No architectures set.")
			return None
		Archi = self.ChildLists["Architecture"][0]
		logging.info("Synthesize design for architecture '{0}'.".format(Archi))
		
		AppMod=self.Parameters["Common"]["Module"]
		return Archi.Synthesize(
			Mod=AppMod, 
			SrcDirectory=SrcDirectory, 
			OutputPath=OutputPath, 
			ControlHW=ControlHW, 
			RemoteHost=RemoteHost
			)
	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, Model=None, FromLib=False, ExtraParameters={}):
		"""
		Add an element as child corresponding to allowed type.
		If Library is True, fetch item from library.
		"""
		if not Name: ChildName = NewName(Type, [item.Parameters["Common"]["Name"] for item in self.ChildLists[Type]])
		else: ChildName=Name
		
		if Type == "Algorithm": 
			Child = Algo(ChildName, Parent=self)
			if FromLib: 
				if not Child.SetFromLib(ChildName): return None
		elif Type == "Architecture": 
			Child = Arch(ChildName, Model=Model, Parent=self)
		elif Type == "NoC":    
			NoCServName=ChildName
			Child = NoC(NoCServName, Parent=self)
			Serv=self.Library.Service(NoCServName, ServiceAlias=NoCServName)
			if Serv is None: 
				logging.error("No service '{0}' found in library.".format(NoCServName))
				return None
			Mod=Serv.GetModule()
			if Mod is None: return None
			if FromLib: 
				if not Child.SetFromLib(NoCName=NoCServName, NoCModule=Mod): return None
		elif Type == "IP":   
			Child = IP(ChildName, Parent=self)
			if FromLib: 
				Mod=self.Library.Module(Name)
				if Mod is None: logging.error("No module '{0}' found in library.".format(Name))
				Child.SetFromLib(ChildName, Mod)
		else:
			logging.warning("Wrong child type '{0}' : child creation aborted.".format(Type))
			raise TypeError
			return None
		self.ChildLists[Type].append(Child)
#		logging.info("Add child '{0}' to '{1}': succeeded.".format(Child, self))
		return Child
	#----------------------------------------------------------------------
	def GetAlgo(self):
		"""
		return the algorithm associated with this application.
		"""
		if len(self.ChildLists["Algorithm"]):
			return self.ChildLists["Algorithm"][0]
		else:
			return None
	#----------------------------------------------------------------------
	def UpdateAlgo(self, CDFG=None):
		"""
		Build a new packet dependency graph from activity diagram tree.
		"""
		if CDFG!=None:
			Algorithm = self.GetAlgo()
			if Algorithm!=None: Algorithm.CDFG=CDFG	
		else:
			logging.error("No Control Data Flow Graph specified: update aborted.")
			return False
		return True
	#----------------------------------------------------------------------
	def SetAPCG(self, APCG=None):
		"""
		Draw task graph of current application.
		"""
		if not APCG is None:
			self.APCG=APCG
#			Mapping={}
#			for N in self.APCG.nodes():
#				Mapping[N]=str(N)
#			GraphCopy=nx.relabel_nodes(self.APCG, Mapping, copy=True)
#			
#			try: A = nx.to_agraph(GraphCopy)
#			except: 
#				logging.error("Unable to draw graph (pygraphviz installation or python3 incompatibility may be the cause)")
#				return False
#		#	A.node_attr.update(color='red') # ??   
#			A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8 -Efontsize=8 -Gbgcolor=transparent')
#			A.draw(self.APCGImagePath)
#			logging.info("Draw Application Characterization Graph (APCG) for application '{0}': succeeded.".format(self))	
		else:
			logging.error("No Control Data Flow Graph specified: update aborted.")
			return False
		return True
#	#----------------------------------------------------------------------
	def Binding(self, Algo=None, FpgaDesign=None, NoCName=None):
		"""
		Map APCG on a NoC with modules (HW operators) assigned to operations.
		"""
		# Clean old design------------
		if len(self.ChildLists["NoC"])>0 :
			for Child in self.ChildLists["NoC"]:
				Child.Remove()
		if len(self.ChildLists["IP"])>0: 
			for Child in self.ChildLists["IP"]:
				Child.Remove()
				
		if FpgaDesign is None:
			NoCParams, M = NoCMapping.SetNoCParam(self.APCG)
			DimX, DimY = M.Size()
		else:
			NoCParams = FpgaDesign.NoCParams
			DimX = FpgaDesign.DimX
			DimY = FpgaDesign.DimY
			
		if NoCName is None: NoCName="AdOCNet"
		# Create a NoC Object with specified properties -----
		NewNoC=self.AddChild("NoC", Name=NoCName, FromLib=True)
		if NewNoC is None: 
			logging.error("Unable to add NoC child to application.")
			raise SyntheSysError("NoC name '{0}' not found in library.".format(NoCName))
		NewNoC.Parameters["Common"].update(NoCParams)
		NewNoC.Parameters["Common"]["Name"]="AdOCNet_{0}".format(NoCParams["Dimensions"])
		
		# CREATE THE ARCHITECTURE CHARACTERIZATION GRAPH (ARCG)
		logging.debug("Matrix dimensions X={X}, Y={Y}".format(X=DimX, Y=DimY))
		NewNoC.IPMatrix = Matrix.Matrix(xSize=DimX, ySize=DimY)
		if FpgaDesign is None:
			# Build a logic 2D mesh architecture graph--------------
			NoCMapping.ConfigureNoC(
					FlitWidth=int(NewNoC.Parameters["Common"]["FlitWidth"]), 
					NbCtrlFlits=2 # TODO : adjust dynamically
					)
			ARCG=NoCMapping.GenerateARCG(DimX, DimY)
			# MAPPING HEURISTIC ======================================
			Mapping, ECost=NoCMapping.Map(ARCG=ARCG, APCG=self.APCG, DimX=DimX, DimY=DimY, Algo=Algo)
		else:
			Mapping = FpgaDesign.NoCMapping
			ARCG    = FpgaDesign.ARCG
			ECost   = MapUtils.CalculateCost(Mapping, APCG=self.APCG, ARCG=ARCG)
		
		# ===================================================
		# Now add IP to NoC Children according to mapping
		for Node, (x, y) in Mapping.items():
			# Add Node IP as NoC child
			Mod = Node.GetModule()
			if Mod is None: 
				logging.error("Unable to connect IP to NoC: no module associated with it.")
				continue
			NewIP = NewNoC.AddChild("IP", Name=Mod.Name, FromLib=False)
			NewIP.SetFromLib(Mod.Name, Mod, Position="{0}:{1}".format(x, y))

		NewNoC.IPMatrix.ShrinkNones()
		#----------------------
#		logging.debug("MAP COMPLETED")	
		return Mapping, ECost, DimX, DimY, ARCG, NoCParams
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
#			logging.info("Draw APCG {0}".format(repr(self.APCG)))

			W, H = self.Drawing.App(self.APCGImagePath, Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0

#======================================================================
class Algo(TreeMember):
	"""
	Algorithm tree member
	"""
	#----------------------------------------------------------------------
	def __init__(self, Name = None, Parent = None, Bundle=None):
#		logging.debug("Bundle state: {0}".format(Bundle))
		TreeMember.__init__(self, None, "Algorithm", Name, Parent, Bundle)
		self.SetIcon()
		self.ChildLists=collections.OrderedDict() # list of Architecture(Arch) objects
		self.InitParameters(Name)
		self.AD_Tree=None # Activity diagram
		self.DCFG=None
		self.DCFGImagePath = self.Parameters["Common"]["Name"]+".svg"
		self.Drawing=None
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("Algo.png")
		except: self.Icon = ""
		self.IconSize = (30, 20)
	#----------------------------------------------------------------------
	def InitParameters(self, Name):
		self.Parameters["Common"].update({ # Value => list of choices
			})
		self.Parameters["Resources"].update({ # Value => list of choices
			})
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		return True
	#----------------------------------------------------------------------
	def SetCDFG(self, CDFG=None):
		"""
		Build a new packet dependency graph from activity diagram tree.
		"""
		if CDFG!=None:
			self.CDFG=CDFG
#			Mapping={}
#			for N in CDFG.nodes():
#				Mapping[N]=str(N)
#			CDFG_Copy=nx.relabel_nodes(CDFG, Mapping, copy=True)
#	
#			try: A = nx.to_agraph(CDFG_Copy)
#			except: 
#				logging.error("Unable to draw graph (pygraphviz installation or python3 incompatibility may be the cause)")
#				return False
#		#	A.node_attr.update(color='red') # ??
#			A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8 -Efontsize=8 -Gbgcolor=transparent')
#			A.draw(self.DCFGImagePath)
#			logging.info("Draw Control Data Flow Graph (CDFG) of application '{0}': succeeded.".format(self))	
		else:
			raise NameError
			logging.error("No Control Data Flow Graph specified: update aborted.")
			return False
		return True
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.Algo(self.DCFGImagePath, Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0

#======================================================================
class IP(TreeMember):
	"IP for a design (could be a NoC as well as an elementary bloc.)"
	Sources=[]
	#----------------------------------------------------------------------
	def __init__(self, Name = "Unkown_IP", Icon = None, Parent = None, Bundle=None):
		TreeMember.__init__(self, None, "IP", Name, Parent)
		self.Icon=Icon
		self.SetIcon()
		self.ChildLists["Library"]=[] # list of library objects
		self.Sources=[]
		self.InitParameters()
	#----------------------------------------------------------------------
	def GetPipelineLength(self):
		"""
		return the module PipelineLength value
		"""
		if "Module" in self.Parameters["Common"]:
			PipelineLength=self.Parameters["Common"]["Module"].Latency
			return PipelineLength
		else:
			logging.warning("[IP.GetPipelineLength] No module associated with IP '{0}'".format(self))
			return 1
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try:
			if self.Icon: 
				try:self.Icon = self.Bundle.Get(self.Icon)
				except: pass
			else: self.Icon = self.Bundle.Get("IP.png")
		except: self.Icon = ""
		self.IconSize = (20, 20)
		
	#----------------------------------------------------------------------
	def SourcesToLib(self, IPName, Sources, Management=False): # TODO: Use it !
		"""
		Copy each source file (HDL) to LibraryPath, under IP/Category/IPName
		"""
#		IPGen.AddSourcesToLib(IPName, Sources, LibPath=self.Library, Management=Management)
		return False

	#----------------------------------------------------------------------
	def InitParameters(self, Name = "Unknown IP"):
		self.Parameters["Resources"].update({
			})
		self.Parameters["Parent"].update({
			"FlitWidth":"16",
			"InputQDepth":8, 
			"OutputQDepth":16,
			"Position":"0:0",
			"FluxCtrl":"HandShake",
			"Target"  :"0:0",
			})
		self.Parameters["Common"].update({
			"Service": None,
			"Category":"Application", # or 'Management'
			"Interface":"HandShake",
			"Sources":[], 
			"Resets":collections.OrderedDict(), 
			"Clocks":collections.OrderedDict(), 
			"NetworkInterface":[], 
			"Ports":collections.OrderedDict(), 
			"Libraries":[], 
			"Packages":[], 
			"Generics":collections.OrderedDict(),
			})
	#----------------------------------------------------------------------
	def SetNetworkParameter(self, Parameter, Value):
		"""
		Change value of parameter of NoC and NoC Children.
		"""
		try:
			self.Parameters["Common"][Parameter]=Value
			return True
		except:
			return False
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		if Parameter == "Position":
			try: xNew, yNew = list(map(int, self.Parameters[ParameterType][Parameter].lower().split(':')))
			except: return False
			# Update Matrix state so as to move component to its new coordinates
			if not self.Parent.IPMatrix.MoveInMatrix(self, xNew, yNew): return False
		elif ["FluxCtrl","Category" ].count(Parameter):
			Availables=IPGen.AvailableValues(Parameter)
			Value=self.Parameters[ParameterType][Parameter]
			for AvType in list(Availables.keys()):
				if not Availables[AvType].count(Value):
					return False
		return True

	#----------------------------------------------------------------------
	def AvailableValues(self, Parameter, ParentParam=None):
		"""
		Overloaded function: return available IP parameter values.
		"""
		if ParentParam!=None:#"Resets", "Clocks"
			if ParentParam == "NetworkInterface":
				#Signal=Parameter.split("/")
				#AvSigStr = self.Parent.Parameters["Common"][ParentParam]
				#if self.Parent.Type=="NoC": 
				#	AvSig = map(lambda x: x.split('/'), AvSigStr)
				#	Availables = filter(lambda x: x[1].upper()!=Signal[1].upper(), AvSig)
				#	return {ParentParam:map(lambda x: "/".join(x), Availables)}
				#else: 
				return {ParentParam:[]} # TODO: Propose something
			elif ["Resets", "Ports", "Clocks"].count(ParentParam):
				Signal=Parameter.split("/")
				FPGAList = self.FindFPGA() # Find associated FPGA for each architecture
				PortList = []
				for FPGA in FPGAList: # Consider only FPGA of the first architecture found
					PortList = [x for x in FPGA.Parent.ChildLists["Port"] if x.Parameters["Parent"]["FPGA"]==FPGA.Parameters["Parent"]["Position"]]
					PortDict=collections.OrderedDict()
					for Port in PortList:
						IOMapList = Port.Parameters["Common"]["Pads"]
						PortDict[Port.Parameters["Common"]["Name"]]=IOMapList
					return PortDict
				else: return {ParentParam:[]}
				# Return FPGA's ports list
			elif  ParentParam == "Disconnected":
				Signal=Parameter.split("/")	
				if   Signal[1].upper()=="OUT": return {ParentParam:["Open",]}	
				# TODO: build O, 1 constants from size
				elif Signal[1].upper()=="IN":  return {ParentParam:['HIGH(ALL)','LOW(ALL)']}
			elif  ParentParam == "Clocks":
				TargetFPGA = self.FindFPGA()
				return collections.OrderedDict()# TODO: Manage DCM
				for DCM in TargetFPGA.GetDCM():
					Availables[DCM.Name]=DCM.Interface()
			else:
				return collections.OrderedDict()
		else:
			return IPGen.AvailableValues(Parameter)
	#----------------------------------------------------------------------
	def GetTop(self):
		"""
		return entity name and path of HDL Top source.
		"""
		if "Module" in self.Parameters["Common"]:
			TopEntity, TopPath=self.Parameters["Common"]["Module"].GetTop()
		else:
			logging.warning("No module associated with IP '{0}'".format(self))
			TopEntity, TopPath=None, None
		return TopEntity, TopPath
	#----------------------------------------------------------------------
	def IsInLibrary(self):
		"""
		Parse XML file to find if component is already saved in library.
		"""
		if self.Library.Module(self.Parameters['Common']['Name'])!=None:
			return True 
		else:
			return False 
	#----------------------------------------------------------------------
	def GetModule(self):
		"""
		return SyntheSys.SysGen.module associated with this application.
		"""
		return self.Parameters["Common"]["Module"]
	#----------------------------------------------------------------------
	def SetFromLib(self, Name, Module=None, Position=None, Target=None):
		"""
		Get information from library item and set IP parameters.
		Overloaded function.
		"""
		if isinstance(Module, ICModule.Module): Mod = Module
		elif isinstance(Module, str): Mod=self.Library.Module(Module)
		elif Module is None: Mod=self.Library.Module(Name)
		else:
			logging.error("'{0}' format not recognized. Library import failed.".format(Module))
			return False
		
		if Mod is None: 
			logging.error(" Module '{0}' not found: import aborted.".format(Name if Module is None else Module))
			return False
			
		self.Parameters["Common"]["Service"] = Mod.GetProvidedService() # TODO: select good service
#		self.Parameters["Common"]["Service"].Alias=self.Parameters["Common"]["Name"]
		
		self.Parameters["Common"]["Name"]  = Mod.Name
		self.Parameters["Common"]["Module"]=Mod
#		logging.debug("Set '{0}' to value '{1}' in library.".format(self.Type, Mod))
		
		if Position!=None: self.Parameters['Parent']["Position"] = Position
		else: self.Parameters['Parent']["Position"] = "0:0"
		if Target!=None:   self.Parameters['Parent']["Target"]   = Target
		else: self.Parameters['Parent']["Target"] = self.Parameters['Parent']["Position"]
		
		for LibName, LibPathList in Mod.GetDependencies()['library'].items():
			self.AddChild("Library", LibName) # list of library objects
		self.Sources = []

		self.Parameters["Common"]["Sources"]  = Mod.GetSources(Synthesizable=True, Constraints=None, IsTop=True)
		Resets=collections.OrderedDict()
		for RSig in list(Mod.GetReqServMap("reset").values()):
			Resets[RSig]=Constraints.IOMap(RSig) 
		self.Parameters["Common"]["Resets"]   = Resets
		Clocks=collections.OrderedDict()
		for CSig in list(Mod.GetReqServMap("clock").values()):
			Clocks[CSig]=Constraints.IOMap(CSig)
		self.Parameters["Common"]["Clocks"]   = Clocks
		
		# Fetch interfaces of this service-----------------------------
		Serv = self.Parameters["Common"]["Service"]
		InterfacesList = Serv.Interfaces[:]
		for Itf in InterfacesList:
			if Itf.Name==self.Parameters["Parent"]["FluxCtrl"]:
				self.Parameters["Common"]["NetworkInterface"]+=Itf.DataList+Itf.CtrlList
			else:
				for Port in Itf.DataList+Itf.CtrlList:
					self.Parameters["Common"]["Ports"].update({Port.Name:Constraints.IOMap(Port)})
		#--------------------------------------------------------------
		
		#self.Parameters["Common"]["Libraries"]= # To remove from properties
		#self.Parameters["Common"]["Packages"] = # To remove from properties 
		# Get generics of all offered service
		for ServName, Serv in Mod.ProvidedServ.items():
			if Serv is None: continue
			self.Parameters["Common"]["Generics"].update(Serv.Params)
		
		#self.Parameters["Parent"]["FluxCtrl"]    =
		#self.Parameters["Parent"]["InputQDepth"] =
		#self.Parameters["Parent"]["OutputQDepth"]=
		#self.Parameters["Parent"]["Interface"]   =
		return True
	#----------------------------------------------------------------------
	def AddToLib(self):
		"""
		Remove useless parameters before saving to XML 
		"""
		del self.Parameters["Common"]["Sources"]
		del self.Parameters["Common"]["Resets"]
		del self.Parameters["Common"]["Clocks"]
		del self.Parameters["Common"]["NetworkInterface"]
		del self.Parameters["Common"]["Ports"]
		del self.Parameters["Common"]["Libraries"]
		del self.Parameters["Common"]["Packages"]
		del self.Parameters["Common"]["Generics"]
		del self.Parameters["Common"]["Service"]
		del self.Parameters["Common"]["Module"]
		
		TreeMember.AddToLib(self)
	#----------------------------------------------------------------------
	def FindFPGA(self):
		"""
		Return FPGA object that is associated with IP (that is 'has the same position').
		"""
		FPGAList  = []
		Component = self
		while(Component!=None):
			if Component.Parent:
				if Component.Parent.Type == "Application":# Get IP position
					Pos = Component.Parameters["Parent"]["Position"] 
					for Arch in Component.Parent.ChildLists["Architecture"]:
						for FPGA in Arch.ChildLists["FPGA"]:
							if FPGA.Parameters["Parent"]["Position"] == Pos:
								FPGAList.append(FPGA)
			Component = Component.Parent
		return FPGAList
	#----------------------------------------------------------------------
	def FindArchitectures(self):
		"""
		Return FPGA object that is associated with IP (that is 'has the same position').
		"""
		FPGAList  = []
		Component = self
		while(Component!=None):
			if Component.Parent:
				if Component.Parent.Type == "Application":# Get IP position
					return Component.Parent.ChildLists["Architecture"]
			Component = Component.Parent
		return []
	#----------------------------------------------------------------------
	def Generate(self, NameList, NoCInterfaces, Position, Header, FlitWidth, CommunicationService, OutputPath="./"):
		"""
		Generate synthesized netlist for this IP on a specified FPGA.
		"""
		IPServ=self.Parameters["Common"]["Service"]
		if IPServ is None: return None, None, {}, {}
		IPServ.Alias=InstanceName(IPServ.Name, NameList)
		IPModule=self.Parameters["Common"]["Module"]
		# Connect IP with NoC --------------------------------------
		IPNetworkInterfaces = IPServ.GetInterfaces(self.Parameters["Common"]["Interface"])

		ServMapping=collections.OrderedDict()
		# ===================INTERFACE SYNTHESIS=================== #
		DirectionTable={"IN":"OUT", "OUT":"IN", "INOUT":"INOUT"}
		if len(IPNetworkInterfaces)==0:
			logging.debug("Wrapping '{0}'...".format(self))
			#-----------------------------------------------------------
			Name="Wrapped_{0}".format(IPModule.Name)
			
			SharedIPMod, SharedIPServ = self.SharingService(IPModule.Name, IPServ, FlitWidth)
			if None in (SharedIPMod, SharedIPServ): 
				logging.error("Nothing wrapped. Generation aborted.")
				return None, None, {}, {}
			self.Library.Services.append(SharedIPServ) # Add service to library
			self.Library.Modules.append(SharedIPMod) # Add module to library
#			SharedIPMod.Reload()

#			ClockServ=self.Library.Service("clock")
#			RstServ=self.Library.Service("reset")

#			Library = SysGen.XmlLibManager.XmlLibManager(SysGen.BBLIBRARYPATH)
			AdapterServ=self.Library.Service("NetworkAdapter") 
			WrappedElements=SharedIPServ.GenerateWrapper(
							Mod           = SharedIPMod,
							InterfaceList = [x.GetElmt() for x in NoCInterfaces], 
							Name          = Name, 
							AdapterServ   = AdapterServ,
							ClockServ     = None,#ClockServ, 
							RstServ       = None,#RstServ, 
							OutputPath    = OutputPath
							)
			
			if None in WrappedElements: 
				logging.error("Nothing wrapped. Generation aborted.")
				return None, None, {}, {}
			WrappedServ, WrappedMod, AdapterMod, AdapterServ = WrappedElements
			IPServ.AddWrapper(WrappedServ)
			
										
			if WrappedServ==None:
				logging.warning("Failed to wrap IP '{0}': step ignored.".format(IPServ))
			else:
				logging.debug("Generation of a wrapper for IP '{0}': success.".format(IPServ))
#				self.Library.AddService(AdapterServ) # Update service in library
#				self.Library.AddService(WrappedServ) # Update service in library
				self.Library.Services.append(WrappedServ) # Add Service to library
				self.Library.Services.append(WrappedServ) # Add Service to library
			
#				IPNetworkInterfaces = WrappedServ.GetInterfaces(self.Parameters["Common"]["Interface"])
				IPServ=WrappedServ
				IPServ.Alias=IPServ.Name+"_{0}".format(Position)
#				WrappedMod.Reload()
				self.Library.Modules.append(AdapterMod)
				self.Library.Modules.append(WrappedMod)
#				self.Library.AddModule(AdapterMod) # Update module to library
#				self.Library.AddModule(WrappedMod) # Update module to library

		# Direct connection to the network
		else:
			logging.debug("Direct connection of '{0}'...".format(self))
			# Moi pas comprendre ce que j'ai fait ci-dessous
			if IPServ!=IPNetworkInterfaces[0].Service:
				IPServ=IPNetworkInterfaces[0].Service
				IPServ.Alias=IPServ.Name+"_{0}".format(Position)
#				logging.debug("Use wrapper '{0}' instead of native service.".format(IPServ))
			for PName, P in IPServ.Params.items():
				if PName=='FlitWidth':
					P.Default=FlitWidth
					P.SetValue(FlitWidth)
			WrappedMod=IPModule
		
		IPModule.UsedParams+=list(IPModule.Params.keys())
		for PName, P in IPServ.Params.items():
			ServMapping[PName]=([[None, P.GetName(), None],], True, {})
			
		NoCMap=collections.OrderedDict()
		for NoCI in NoCInterfaces:
			ItfList=IPServ.GetInterfaces(Direction="IN" if NoCI.Direction=="OUT" else "OUT")
			for I in ItfList:
				KeepNames=True if (IPServ is CommunicationService) and CommunicationService.IsOrthogonal() else False
				IMap, Internals=NoCI[Position].Connect(I, KeepNames=KeepNames) 
				NoCMap.update(IMap)

		# Map external ports
#		if IPServ is CommunicationService:
#		print("Module:", IPModule)
#		for EPortName, EPort in IPModule.GetExternalPorts(CalledServ=IPServ).items():
#			ServMapping[EPortName]=([[None, EPortName, None],], True, {})
#			print("Add to map:", EPortName)
#		input()
		return IPModule, IPServ, NoCMap, ServMapping, WrappedMod
	#----------------------------------------------------------------------
	def SharingService(self, Name, IPServ, FlitWidth):
		"""
		Return a service made up of the basic block and sharing component services.
		"""
		logging.debug("Build sharing module")
		#---------------------------------	
		# Create a new module SharedIPMod
		Infos={}
		Infos["Name"]    = "Shared{0}".format(Name)
		Infos["Version"] = IPServ.Version
		Infos["Title"]   = "{0} wrapped to be shared.".format(Name)
		Infos["Purpose"] = "Manage operator sharing between tasks."
		Infos["Desc"]    = "Basic block associated with task management components."
		Infos["Tool"]    = ""
		Infos["Area"]    = ""
		Infos["Speed"]   = ""
		Infos["Issues"]  = ""
		# Empty new module-----------------------------------
		SharedIPMod=LibEditor.NewModule(Infos=Infos, Params=list(IPServ.Params.values()), Ports=[], Clocks=[], Resets=[], Sources=[])
		SharedIPMod.AddResource(Dev="ALL", RName="", Rused=0)

#		SharedIPMod.Connect(InterfaceList, IPServ.Interfaces)

		#---------------------------------
		TaskMgrServ=self.Library.Service("TaskManager") 
#		TaskMgrMod=TaskMgrServ.GetModule()
#		PipelineMgrServ=self.Library.Service("PipelineManager")
#		PipelineMgrMod=PipelineMgrServ.GetModule()
#		FIFOServ=self.Library.Service("FIFO")
#		HeaderFIFOServ=FIFOServ.Copy()
#		HeaderFIFOServ.Alias="HeaderFIFO"
	
		V={"FlitWidth":FlitWidth,}
		for P in list(TaskMgrServ.Params.values()):#+list(PipelineMgrServ.Params.values()):
			P.UpdateVars(V)
			if P.Name.lower()=="flitwidth":
				P.SetValue(FlitWidth)

#		FIFOMod=PipelineMgrServ.GetModule()
		#-- Parameters
		SharedIPMod.Params.update(TaskMgrServ.Params)
		SharedIPMod.Params.pop("BBInputWidth")
		SharedIPMod.Params.pop("BBOutputWidth")
		SharedIPMod.Params.pop("InputSerialization")
		SharedIPMod.Params.pop("OutputSerialization")
#		SharedIPMod.Params.update(PipelineMgrServ.Params) # TODO : Manage different names for parameters (for example: append ServiceName to parameter)
		#---------------------------------
		# ADD SERVICE INTERFACES + MODULE/SERVICE PORTS
		logging.debug("ADD SERVICE INTERFACES + MODULE/SERVICE PORTS")
#		TaskSelection   = TaskMgrServ.GetInterfaces("TaskSelection")
#		HeaderSelection = TaskMgrServ.GetInterfaces("HeaderSelection")
#		PipelineFilling = TaskMgrServ.GetInterfaces("PipelineFilling")
#		BasicBlockLoad  = TaskMgrServ.GetInterfaces("BasicBlockLoad")
		
		#---------------------------------	
		# SERVICE CREATION
		logging.debug("SERVICE CREATION")
		Infos={}	
		Infos["Name"]     = SharedIPMod.Name
		Infos["Type"]     = IPServ.Type
		Infos["Version"]  = IPServ.Version
		Infos["Category"] = IPServ.Category
		
		#------
		# Get interfaces
		OffMapping=collections.OrderedDict()
		BBITFList = IPServ.GetInterfaces("BasicBlock", Direction="OUT")
		if len(BBITFList)==0:
			logging.error("Service '{0}' do not have a 'BasicBlock' interface. Unable to Wrap it for NoC interfacing.".format(IPServ))
			return None, None
		BasicBlockOutputItf=BBITFList[0]
#		PipelineStatus      = PipelineMgrServ.GetInterfaces("PipelineStatus", Direction="OUT")[0]
		DataManager         = TaskMgrServ.GetInterfaces("FIFO_Light")[0]
		NetworkInput        = TaskMgrServ.GetInterfaces("FIFO_Light")[0]
#		FIFOInput           = FIFOServ.GetInterfaces("FIFO_Light", Direction="IN")[0]
#		FIFOOutput          = FIFOServ.GetInterfaces("FIFO_Light", Direction="OUT")[0]
		
		
		#========
		# Data width adaptation
		BBOutputs=[x for x in BasicBlockOutputItf.DataList if x.Direction=="OUT"]
		
		SerialCtrlSigs={}
		for Ctrl in  BasicBlockOutputItf.CtrlList:
			if Ctrl.Name=="Start":    SerialCtrlSigs["Start"]=Ctrl
			if Ctrl.Name=="DataRead": SerialCtrlSigs["DataRead"]=Ctrl

		DataSize="+".join([str(FlitWidth) for x in BBOutputs])
		DataVars={}
		for DV in [x.GetUsedParam() for x in BBOutputs]:
			DataVars.update(DV)
		OutDataSignal=Signal("OutputData", Type="logic", Size=FlitWidth, Default=0, Dir="OUT", ParamVars=DataVars)
		OutReadSignal=Signal("OutputRead", Type="logic", Size=1, Default=0, Dir="IN")
		OutDataPendingSignal=Signal("OutputFifoEmpty", Type="logic", Size=1, Default=0, Dir="OUT", ParamVars={})
#		HeaderReceivedSignal=TaskMgrServ.Ports["HeaderReceived"].Copy()
		HeaderValidSignal=TaskMgrServ.Ports["HeaderValid"].Copy()
		
#		PayloadReceivedSignal=TaskMgrServ.Ports["PayloadReceived"].Copy()
		PayloadValidSignal=TaskMgrServ.Ports["PayloadValid"].Copy()
		
		HeaderTransmittedSignal=TaskMgrServ.Ports["HeaderTransmitted"].Copy()
		PayloadTransmittedSignal=TaskMgrServ.Ports["PayloadTransmitted"].Copy()
		TransmittedSignal=TaskMgrServ.Ports["Transmitted"].Copy()
		for P in [OutDataSignal, OutReadSignal, OutDataPendingSignal, HeaderTransmittedSignal, PayloadTransmittedSignal, TransmittedSignal, PayloadValidSignal, HeaderValidSignal]:
			SharedIPMod.AddPortAsSignal(P)
			
#		PayloadTransmittedSignal=HeaderTransmittedSignal.Copy()
#		PayloadTransmittedSignal.SetName("PayloadTransmitted")
#		PayloadTransmittedSignal.SetValue(1)
#		SharedIPMod.Params["PayloadTransmitted"]=PayloadTransmittedSignal
		#========
		NetInputs=[x for x in NetworkInput.DataList if x.Direction=="IN"]
		DataSize="+".join([str(FlitWidth) for x in NetInputs])#x.Size
		DataVars={}
		for DV in [x.GetUsedParam() for x in NetInputs]:
			DataVars.update(DV)
		InDataSignal         = Signal("InputData", Type="logic", Size=DataSize, Default=0, Dir="IN", ParamVars=DataVars)
		InDataPendingSignal  = Signal("InputDataValid", Type="logic", Size=1, Default=0, Dir="IN", ParamVars={})
		ReadHeaderFifoSignal = Signal("ReadHeaderFifo", Type="logic", Size=1, Default=0, Dir="IN", ParamVars={})
		SendBackSignal       = Signal("SendBack", Type="logic", Size=1, Default=0, Dir="OUT", ParamVars={})
		TerminalBusySignal   = Signal("TerminalBusy", Type="logic", Size=1, Default=0, Dir="OUT", ParamVars={})
#		HeaderFIFOWriteSignal=Signal("HeaderFIFO_Write", Type="logic", Size=1, Default=0, Dir="INOUT", ParamVars={})
		for P in [InDataSignal, ReadHeaderFifoSignal, InDataPendingSignal, SendBackSignal, TerminalBusySignal]:
			SharedIPMod.AddPortAsSignal(P)
		#========
		SharedIPMod.UpdateXML()
		SharedIPServ = LibEditor.ProvidedServiceXml(Mod=SharedIPMod, Interfaces=[], Infos=Infos)
		#---------------------------------
		logging.debug("INTERFACE DECLARATION")
		# INTERFACE DECLARATION
		#------
		Infos={}
		Infos["Name"]= ""
		Infos["Size"]=1 # Number of possible connections for this interface
		Infos["Direction"]="IN"
		Infos["DataList"]=[InDataSignal,]
		Infos["CtrlList"]=[]
		Infos["Mapping"]={"InputData":"OutputData", "InputDataValid":"OutputFifoEmpty"}
		Infos["Protocol"]=None
		Infos["Registers"]={}
		Infos["Tags"]={}
		I=Interface(Service=SharedIPServ, Infos=Infos)
		I.Name="FIFO_Light"
		P=DirectedProtocol(Interface=I, Name=I.Name+"_Protocol")
		P.AddNewStep(Label="Get Data", SigList=["InputData", "InputDataValid"], ValList=[1, 1])
		I.SetProtocol(P)
		SharedIPServ.AddInterface(I)
		#------
		Infos={}
		Infos["Name"]= ""
		Infos["Size"]=1 # Number of possible connections for this interface
		Infos["Direction"]="OUT"
		Infos["DataList"]=[OutDataSignal,]
		Infos["CtrlList"]=[OutDataPendingSignal,OutReadSignal, TransmittedSignal]
		Infos["Mapping"]={"OutputData":"OutputData", "OutputFifoEmpty":"OutputFifoEmpty", "OutputRead":"OutputRead", "Transmitted":"Transmitted"}
		Infos["Protocol"]=None
		Infos["Registers"]={}
		Infos["Tags"]={}
		I=Interface(Service=SharedIPServ, Infos=Infos)
		I.Name="FIFO_OUT"
		P=DirectedProtocol(Interface=I, Name=I.Name+"_Protocol")
		P.AddNewStep(Label="Request Data from FIFO", SigList=["OutputFifoEmpty:OutputRead", "OutputFifoEmpty"], ValList=["0:1", 0])
		P.AddNewStep(Label="Data available", SigList=["OutputData", "Transmitted"], ValList=[0, 1])
		I.SetProtocol(P)
		SharedIPServ.AddInterface(I)
#		CompI=I.Complement(Service=SharedIPServ)
#		CompI.AddSignal(Signal=ReadSignal, Target=ReadSignal.GetName(), Ctrl=True)
#		for Step in CompI.GetProtocol().IterSteps():
#			Step.Ctrl["OutputRead"]=ReadSignal
#		SharedIPServ.AddInterface(CompI)
		
		SharedIPServ.UpdateXML()
		#---------------------------------
		# ADD OFFERED SERVICE MAPPING
		logging.debug("ADD OFFERED SERVICE MAPPING")
		OffMapping={
			"FlitWidth"         : "FlitWidth",
			"ComHeader"         : "ComHeader",
			"OutputRead"        : "OutputRead",
			"OutputData"        : "OutputData",
			"OutputFifoEmpty"   : "OutputFifoEmpty",
			"OutputFifoFull"    : "OutputFifoFull",
			"OutputData"        : "OutputData",
			"InputData"         : "InputData",
			"InputDataValid"    : "InputDataValid",
			"Transmitted"       : "Transmitted",
#			"HeaderReceived"    : "HeaderReceived",
			"HeaderValid"       : "HeaderValid",
#			"PayloadReceived"   : "PayloadReceived",
			"PayloadValid"      : "PayloadValid",
			"HeaderTransmitted" : "HeaderTransmitted",
			"PayloadTransmitted": "PayloadTransmitted",
			"ReadProgram"       : "ReadProgram",
			"ReadHeaderFifo"    : "ReadHeaderFifo",
			"SendBack"          : "SendBack",
			"TerminalBusy"      : "TerminalBusy",
#			"SendData"          : "SendData",
			}
		for P in list(SharedIPMod.Params.values()):
			OffMapping[P.GetName()]=P.GetName()
		SharedIPMod.AddProvServ(SharedIPServ.Name, SharedIPServ.Name, OffMapping)
		#---------------------------------
		# SUBSERVICE INSTANCIATION
		logging.debug("SUBSERVICE INSTANCIATION")
		for S in [TaskMgrServ,]: #IPServ, ,PipelineMgrServ, FIFOServ
			S.Alias=S.Name
		IPServ.Alias=Name
		# Map internal signals
		TaskMgrServMapping, IPServMapping, PipelineMgrServMapping, FIFOMapping, HeaderFIFOMapping=[collections.OrderedDict() for i in range(5)]
		TaskMgrServMapping=collections.OrderedDict()
		BasicBlockInputItf=IPServ.GetInterfaces("BasicBlock", Direction="IN")[0]
		
		Structure=[BasicBlockInputItf.SerializationFactors[D.Name] for D in BasicBlockInputItf.DataList if D.Direction=="IN"] 
		InputSerialization=[]
		for SF in Structure:
			if SF is None:
				InputSerialization.append( str(1) ) 
			else:
				InputSerialization.append( str(SF) ) # TODO manage VHDL types from list
		InputSerializations=[]
		for i, IS in enumerate(InputSerialization):
			InputSerializations.append("{0}=>{1}".format(i, IS))
		
		BBInputs=[x for x in BasicBlockInputItf.DataList if x.Direction=="IN"]
		BBInDataSize="+".join([str(FlitWidth) for x in BBInputs])
		
		BasicBlockOutputItf=IPServ.GetInterfaces("BasicBlock", Direction="OUT")[0]
		BBOutputs=[x for x in BasicBlockOutputItf.DataList if x.Direction=="OUT"]
		BBOutDataSize="+".join([str(FlitWidth) for x in BBOutputs])
		
		# Task manager Parameters mapping
		for PName, P in TaskMgrServ.Params.items():
			TaskMgrServMapping[PName]           = ([[None, PName, None],], True, {})
			
#		TaskMgrServMapping["FlitValid"]          = ([[None, "InputDataPending", None],], True, {})
		TaskMgrServMapping["BBInputs"]           = ([[None, "BBInputs", None],], True, {}) #[(IPServ.Alias, x.Name, None) for x in BBInputs]
#		TaskMgrServMapping["BBInputValid"]       = ([["PipelineManager", "BBInputValid", None],], True, {})
#		TaskMgrServMapping["BBOutput"]     = ([["TaskManager", "BBOutput", None],], True, {})
		TaskMgrServMapping["BBInputWidth"]       = ([[None, BBInDataSize, None],], True, {})
		TaskMgrServMapping["BBOutputWidth"]      = ([[None, BBOutDataSize, None],], True, {})
		TaskMgrServMapping["InputSerialization"]       = ([[None, '({0})'.format(','.join(InputSerializations)), None],], True, {})
		TaskMgrServMapping["InputData"]          = ([[None, "InputData", None],], True, {})
#		TaskMgrServMapping["HeaderReceived"]     = ([[None, "HeaderReceived", None],], True, {})
#		TaskMgrServMapping["HeaderTransmitted"]  = ([["PipelineManager", "InputHeader", None],], True, {})
		TaskMgrServMapping["HeaderTransmitted"]  = ([[None, "HeaderTransmitted", None],], True, {})
		TaskMgrServMapping["PayloadTransmitted"] = ([[None, "PayloadTransmitted", None],], True, {})
		TaskMgrServMapping["Transmitted"]        = ([[None, "Transmitted", None],], True, {})
		TaskMgrServMapping["ComHeader"]          = ([[None, "ComHeader", None],], True, {})
#		TaskMgrServMapping["ReadProgram"]        = ([[None, "ReadProgram", None],], True, {})
		TaskMgrServMapping["OutputData"]         = ([[None, "OutputData", None],], True, {})
		TaskMgrServMapping["SendBack"]           = ([[None, "SendBack", None],], True, {})
		TaskMgrServMapping["TerminalBusy"]       = ([[None, "TerminalBusy", None],], True, {})
		TaskMgrServMapping["ReadHeaderFifo"]     = ([[None, "ReadHeaderFifo", None],], True, {})
		TaskMgrServMapping["OutputRead"]         = ([[None, "OutputRead", None],], True, {})
		
		#---------------------------------------------------
		IPMod = IPServ.GetModule()
		PipeLength=2 if IPMod.Latency is None else IPMod.Latency
		TaskMgrServMapping["PipelineLength"] = ([[None, str(PipeLength), None],], True, {})

		#---------------------------------------------------
		Structure=[BasicBlockOutputItf.SerializationFactors[D.Name] for D in BasicBlockOutputItf.DataList if D.Direction=="OUT"] 
		OutputSerialization=[]
		for SF in Structure:
			if SF is None:
				OutputSerialization.append( str(1) ) 
			else:
				OutputSerialization.append( str(SF) ) # TODO manage VHDL types from list
		OutputSerializations=[]
		for i, IS in enumerate(OutputSerialization):
			OutputSerializations.append("{0}=>{1}".format(i, IS))
		TaskMgrServMapping["OutputSerialization"] = ([[None, '({0})'.format(','.join(OutputSerializations)), None],], True, {})
		#---------------------------------------------------
		
		for CtrlName, CtrlSig in SerialCtrlSigs.items():
			TaskMgrServMapping[CtrlName]     = ([[IPServ.Alias, CtrlSig.Name, None],], True, {})

		IPServMapping[BBOutputs[0].GetName()]=([["TaskManager", "BBOutput", None],], True, {}) # TODO: FOR EACH OUTPUT
		TM_BBinput=TaskMgrServ.Ports["BBInputs"].Copy()
		
		for i, BBinput in enumerate(BBInputs):
			if i>0:
				Actual=str(TM_BBinput[str(i+1)+"*"+str(FlitWidth)+"-1":str(i)+"*"+str(FlitWidth)])
			else:
				Actual=str(TM_BBinput[str(FlitWidth)+"-1":0])
			IPServMapping[BBinput.GetName()]=([["TaskManager", Actual, None],], True, {})
		
		if not (BasicBlockInputItf.DataWidth is None):
			IPServMapping[BasicBlockInputItf.DataWidth]=([[None, "FlitWidth", None],], True, {})
			SharedIPMod.Params.pop(BasicBlockInputItf.DataWidth)
			SharedIPServ.Params.pop(BasicBlockInputItf.DataWidth)
		#----------
		SubServices = [TaskMgrServ, IPServ, ]#PipelineMgrServ, FIFOServ, HeaderFIFOServ]
		Mappings    = [TaskMgrServMapping, IPServMapping,]#, PipelineMgrServMapping, FIFOMapping, HeaderFIFOMapping]
		#----------
		XMLElmt=SharedIPMod.UpdateXML()
		SharedIPMod.MapSubServices(Services=SubServices, Mappings=Mappings)
		SharedIPMod.Reload()
		SharedIPMod.IdentifyServices([SharedIPServ, TaskMgrServ, IPServ,])#, PipelineMgrServ, FIFOServ])
		#---------------------------------
		return SharedIPMod, SharedIPServ
	#----------------------------------------------------------------------
	def GenConstraints(self, Format):
		"""
		Return a constraint file string from pads/signals in parameters.
		"""
		return "".join([x.FormatedConstraints(Format="ucf") for x in list(self.Parameters["Common"]["Ports"].values())])
	#----------------------------------------------------------------------
	def UpdateResources(self, TargetFPGA, ImplementDir):
		"""
		Update resources parameters for each FPGA in application architectures.
		Parse *_map.map file and return dictionary of resources.
		FPGAList is a list of FPGABuilder objects.
		IP and FPGA must be in library.
		"""
		logging.warning("[UpdateResources] TO BE DONE")
		HwModel()
		return None
	#----------------------------------------------------------------------
	def Parse(self):
		SrcList=[os.path.join(self.Library,x) for x in self.Parameters["Common"]["Sources"]]
		ModuleName, Signals, Sources, Generics = Parse(SrcList)
		#self.Parameters["Common"]["Module"]  = Module
		self.Parameters["Common"]["Name"] = ModuleName
		self.Parameters["Common"]["Sources"] = Sources
		GenericDict=collections.OrderedDict()
		for G in Generics:
			GenericDict[G.Name]=G
		self.Parameters["Common"]["Generics"]=GenericDict
#		logging.debug("{0} parsed: {1}".format(self, ModuleName))
		return Signals
	#----------------------------------------------------------------------
	def MapSignals(self, SigDict):
		"""
		Fill parameters types of signals information.
		"""	
		for Mapping in list(SigDict.keys()):
			self.Parameters["Common"][Mapping]=collections.OrderedDict()
			for Signal in SigDict[Mapping]:
				self.Parameters["Common"][Mapping]["/".join(map(str, Signal))]=""
	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, FromLib=False):
		"""
		Add child component to this IP.
		"""
		if not Name: Name = NewName(Type, [item.Parameters["Common"]["Name"] for item in self.ChildLists[Type]])
		if Type == "Library":   
			Child = Lib(self.Library, Name, Parent=self)
			if FromLib: Child.SetFromLib(Name)
		else:
			logging.warning("Wrong child type '{0}' : child creation aborted.".format(Type))
			raise TypeError
			return None
		self.ChildLists[Type].append(Child)
#		logging.info("Add child '{0}' to '{1}': succeeded.".format(Child, self))
		return Child
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if isinstance(self, NoC): return 0, 0
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.IP(Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0
	#----------------------------------------------------------------------
	def Remove(self): # Overload of treemember method
		# Don't forget to remove item from the NoC matrix
		if(isinstance(self.Parent, NoC)):
			self.Parent.IPMatrix.RemoveFromMatrix(self)
		# Now we can remove serenely the treemember
		TreeMember.Remove(self)
		
#======================================================================
class Lib(TreeMember):
	"""
	Library tree member.
	"""
	#----------------------------------------------------------------------
	def __init__(self, Library, Name = "Lib_0", Parent = None, Bundle=None):
		TreeMember.__init__(self, Library, "Library", Name, Parent, Bundle)
		self.SetIcon()
		self.InitParameters()
			
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("Lib.png")
		except: self.Icon = ""
		self.IconSize = (20, 20)

	#----------------------------------------------------------------------
	def InitParameters(self): # Overloaded method
		self.Parameters["Parent"].update({ 
			})
		self.Parameters["Common"].update({ 
			})
		self.Parameters["Resources"].update({
			"Sources":[] 
			})

	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1): # Overloaded method
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.Lib(Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0


#======================================================================
class NoC(IP):
	"NoC design object"
	#----------------------------------------------------------------------
	def __init__(self, Name = "Unknown NoC", Module=None, Parent = None):
		IP.__init__(self, Name, Icon="NoC.svg", Parent=Parent)
		self.Type="NoC"
		self.ChildLists["IP"] = []
		self.ChildLists["NoC"]=[] # list NoC children
		self.IPMatrix = Matrix.Matrix() # According to Dimensions parameter
		self.InitParameters(Name = Name, Module=Module)
#		self.ImplementParameters=None

	#----------------------------------------------------------------------
	def InitParameters(self, Name = "Unknown NoC", Module=None): # Overloaded method
		IP.InitParameters(self)
		del self.Parameters["Common"]["Sources"] # From IP parameters
		del self.Parameters["Parent"]["Target"] # From IP parameters
		self.Parameters["Parent"].update({ 
			})
		self.Parameters["Resources"].update({
			})
		self.Parameters["Common"].update({
#			"Module":"AdOCNet",
			"Service":"NoC",
			"Dimensions":"3x3",
			"FlitWidth":"8", 
			"InputFifoDepth_Table":[32,32],
			"OutputFifoDepth_Table":[32,32],
			"NbOutputs_Table":[5,5],
			"NbInputs_Table":[5,5],
			"Lanes":"1",
			"Routing":"XY",
			"Scheduling":"Priority",
			"Packages":  "",
			"Libraries": "",
			"Resets":[],
			"Clocks":[],
			"NetworkInterface":[],
			"Ports":collections.OrderedDict(), # Association of signal and IO Port/pad mapping
			"Module": Module, # SyntheSys.SysGen module
			})
#		logging.debug("Reloading IO from type parameter.")
		#self.TestParameter("Common", "Type")
	#----------------------------------------------------------------------
	def SetParameter(self, Parameter, Value):
		"""
		Change value of parameter of NoC and NoC Children.
		"""
		self.Parameters["Common"][Parameter]=Value
		# Optimize FlitWidth
		for IP in self.ChildLists["IP"]: # list IP objects
			IP.Parameters["Parent"][Parameter]=Value
		return
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		Value=self.Parameters[ParameterType][Parameter]
		Availables=self.AvailableValues(Parameter)
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		if Parameter == "Dimensions":
			try: x,y=list(map(int, Value.lower().split('x')))
			except: return False
			if not self.IPMatrix.EnlargeMatrix(x, y): return False
		elif ["Module", "FluxCtrl", "Scheduling", "Dimensions"].count(Parameter):			
			if not Value in Availables[Parameter]:
				return False
			else: 
				SigDict = NoCGen.GetIO( # TODO: update this
						Type=self.Parameters["Common"]["Module"], 
						FlitWidth=self.Parameters["Common"]["FlitWidth"], 
						FluxCtrl=self.Parameters["Parent"]["FluxCtrl"], 
						Dimensions=self.Parameters["Common"]["Dimensions"])
				for SigType in list(SigDict.keys()):
					self.Parameters["Common"][SigType]=['/'.join(map(str, x)) for x in SigDict[SigType]]
					
#				logging.info("Parameter '{0}' changed: update IOs.".format(Parameter))
			if Parameter=="Module":
				NewMod = self.Library.Module(Value)
				if NewMod: return True
				else: 
					logging.error("NoC module '{0}' not found : Keep old type value.".format(Value))
					return False
				
		elif ["FlitWidth", "DataWidth"].count(Parameter):
			self.Parameters["Common"]["Module"].Params[Parameter].Default=Value
		elif ["InputFifoDepth_Table", "OutputFifoDepth_Table"].count(Parameter):
			V=eval("list({0})".format(Value))
			if not len(V)==eval(self.Parameters["Common"]["Dimensions"]):
				return False
			else:
				self.Parameters["Common"]["Module"].Params[Parameter].Default=Value
				return True
		elif ["Lanes", "Routing"].count(Parameter):
			if not Availables[Parameter].count(Value):
				return False
		return True
		
	#----------------------------------------------------------------------
	def UpdateModuleParameters(self):
		"""
		Overloaded
		"""
		FlitWidth=int(self.Parameters["Common"]["FlitWidth"])
		DimX, DimY = list(map(int, self.Parameters["Common"]["Dimensions"].lower().split('x')))
				
		# Change default value of module parameters in XML representation
		self.Parameters["Common"]["Module"].EditParam("DimX", DimX)
		self.Parameters["Common"]["Module"].EditParam("DimY", DimY)
		self.Parameters["Common"]["Module"].EditParam("FlitWidth", FlitWidth)
		for Serv, Mapping, IsOrtho, Constraints in list(self.Parameters["Common"]["Module"].ReqServ.values()):
			if Serv is None: 
				logging.error("Required service not found in library in '{0}'".format(self))
			if "FlitWidth" in Mapping:
				Serv.Params[Mapping["FlitWidth"][0][0][1]].Default=FlitWidth
				SubMod=Serv.GetModule(
						Constraints=None) 
				if SubMod != None: SubMod.EditParam("FlitWidth", FlitWidth)
				
		self.Parameters["Common"]["Module"].Reload() # For loops regeneration
		
		if self.Library is None: logging.error("Library of Xmlself.Library module not loaded !")
		else: self.Parameters["Common"]["Module"].IdentifyServices(self.Library.Services)
				
#		for P in self.Parameters["Common"]["Module"].Params.values():
#			P.Vars.update({PName:P.GetValue() for PName,P in self.Parameters["Common"]["Module"].Params.iteritems()})
#		for P in self.Parameters["Common"]["Module"].Ports.values():
#			P.Vars.update({PName:P.GetValue() for PName,P in self.Parameters["Common"]["Module"].Params.iteritems()})
	#----------------------------------------------------------------------
	def AvailableValues(self, Parameter):
		"""
		Overloaded function: return available NoC parameter values.
		"""
#		NoCAvVal = NoCGen.AvailableValues(Parameter)
#		IPAvVal  = IP.AvailableValues(self, Parameter)
#		return {Parameter: NoCAvVal[Parameter]+IPAvVal[Parameter]}
		return {Parameter: []}
	#----------------------------------------------------------------------
	def SetFromLib(self, NoCName, NoCModule=None, Position=None):
		"""
		Get information from library item and set Noc parameters.
		"""
		self.IPMatrix=Matrix.Matrix()
		# Move each child to its recorded position if not already
		for Type, ChildrenList in self.ChildLists.items():
			for Child in ChildrenList:
				xChild, yChild = list(map(int, Child.Parameters["Parent"]["Position"].split(':')))
				xCur, yCur = self.IPMatrix.AddToMatrix(Child)
				if xChild!=xCur or yChild!=yCur:
					self.IPMatrix.MoveInMatrix(Child, xChild, yChild)
		self.IPMatrix.Shrink()
		#------------------------
		if isinstance(NoCModule, ICModule.Module): Mod = NoCModule
		elif isinstance(NoCModule, str): Mod=self.Library.Module(NoCModule)
		elif NoCModule is None: 
			Serv=self.Library.Service("NoC", ServiceAlias=NoCName)
			Mod=Serv.GetModule()
		else:
			logging.error("[Component.Application.SetFromLib] NoCModule format '{0}' not recognized. Library import failed.".format(NoCModule))
			return False
			
#		logging.debug("Set '{0}' as module '{1}' in library.".format(NoCName, Mod))
		# Get module for this NoC
		self.Parameters["Common"]["Module"] = Mod
		
		if Position!=None: self.Parameters['Parent']["Position"] = Position
		else: self.Parameters['Parent']["Position"] = "0:0"
		
#		for LibName, LibPathList in Mod.GetDependencies()['library'].items():
#			self.AddChild("Library", LibName) # list of library objects
		self.Sources = []

		self.Parameters["Common"]["Sources"]  = Mod.GetSources(Synthesizable=True, Constraints=None, IsTop=True)
		self.Parameters["Common"]["Resets"]   = list(Mod.GetReqServMap("reset").values())
		self.Parameters["Common"]["Clocks"]   = list(Mod.GetReqServMap("clock").values())
		self.Parameters["Common"]["NetworkInterface"]= list(Mod.GetPortsDict().values())
		Ports = list(Mod.GetReqServMap("FPGA_Input").values())
		Ports+=list(Mod.GetReqServMap("FPGA_Output").values())
		IOMappings = [Constraints.IOMap(x) for x in Ports]
		self.Parameters["Common"]["Ports"]    = IOMappings
		#self.Parameters["Common"]["Libraries"]= # To remove from properties
		#self.Parameters["Common"]["Packages"] = # To remove from properties 
		self.Parameters["Common"]["Generics"] = Mod.GetParametersDict()
		
		#self.Parameters["Parent"]["FluxCtrl"]    =
		
		self.Parameters["Common"]["Service"]     = Mod.ProvidedServ[NoCName] # TODO: select good service
		self.Parameters["Common"]["Service"].Alias=self.Parameters["Common"]["Name"]
		#self.Parameters["Common"]["InputQDepth"] =
		#self.Parameters["Common"]["OutputQDepth"]=
		#self.Parameters["Common"]["Interface"]   =
		return True		
	#----------------------------------------------------------------------
	def Generate(self):
		"""
		Return Builder AppNoC Child object set with all NoC attributes
		"""	
		raise TypeError("Function call not expected")
		# Old version	
#		Network = Builder.NoCBuilder(
#			Name    = self.Parameters["Common"]["Name"], 
#			Module  = self.Parameters["Common"]["Module"], 
#			SigDict = self.GetSigDict(),
#			FluxCtrl= self.Parameters["Parent"]["FluxCtrl"],
#			Position= self.Parameters["Parent"]["Position"], 
#			LibPath = self.Library,
#			HDL     = "VHDL" 
#			)
#			
#		Network.SetNoCFormat(
#			Type        = self.Parameters["Common"]["Type"], 
#			Config      = "Mesh", # TODO: Add other topologies
#			Dimensions  = self.Parameters["Common"]["Dimensions"], 
#			FlitWidth   = int(self.Parameters["Common"]["FlitWidth"]), 
#			BufferDepth = int(self.Parameters["Common"]["Buffers"]), 
#			VC          = int(self.Parameters["Common"]["Lanes"]), 
#			Routing     = self.Parameters["Common"]["Routing"],
#			Scheduling  = self.Parameters["Common"]["Scheduling"],
#			)
#		for IP in self.ChildLists["IP"]+self.ChildLists["NoC"]:
#			Network.AddChild(IP.Generate())

		return self.Library.Module("AdOCNet", [self.Library,])
	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, FromLib=False):
		"""
		Add a element tree as child corresponding to allowed type.
		Here only NoC and IP types are accepted as children.
		If FromLib is given, fetch item from library.
		"""
		if not Name: Name = NewName(Type, [item.Parameters["Common"]["Name"] for item in self.ChildLists[Type]])
		if Type == "NoC":   
			Child = NoC(Name, Parent=self)
			Serv=self.Library.Module("NoC")
			print("Serv:", Serv)
			Mod=Serv.GetModule()
			print("Mod:", Mod)
			input()
			if FromLib: Child.SetFromLib(Name, Mod)
		elif Type == "IP":  
			Child = IP(Name, Parent=self)
			Mod=self.Library.Module(Name)
			if FromLib: Child.SetFromLib(Name, Mod)
			Child.Parameters["Parent"]["FlitWidth"]=self.Parameters["Common"]["FlitWidth"]
		else:
			logging.warning("Wrong child type '{0}' : child creation aborted.".format(Type))
			raise TypeError
			return None
		self.ChildLists[Type].append(Child)
		self.IPMatrix.AddToMatrix(Child)
#		logging.info("Add child '{0}' to '{1}': succeeded.".format(Child, self))
		return Child
	#----------------------------------------------------------------------
	def GetAllFiles(self):
		"""
		Return a list of all source files previously generated.
		"""
		TotalFiles=[]+self.Sources
		for IPChild in self.ChildLists["IP"]:
			TotalFiles+=IPChild.Sources
		return TotalFiles
	#----------------------------------------------------------------------
	def GenHeader(self, TargetPosition=None):
		"""
		Build a packet header according to target position.
		return value is a integer.
		"""	
		FlitWidth    = int(self.Parameters["Common"]["FlitWidth"])
		return NoCFunctions.GenHeader(TargetPosition, FlitWidth)
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Selected=(-1,-1), Ratio=1): # Overloaded method
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.NoC(Parameters, self.IPMatrix, Width=Width, Height=Height, Selected=Selected, Ratio=Ratio)
			return W, H
		else:
			return 0, 0
			
#======================================================================
class Arch(TreeMember):
	"Design architecture"
	#----------------------------------------------------------------------
	def __init__(self, Name = "Arch_0", Model=None, Parent = None, Bundle=None):
		self.Model=Model
		if Model is None:
			TreeMember.__init__(self, None, "Architecture", Name, Parent, Bundle)
		else: 
			TreeMember.__init__(self, None, "Architecture", Model.Name, Parent, Bundle)
			self.SetFromModel()
		self.SetIcon()
		self.ChildLists["FPGA"]=[] # list of FPGA objects
		self.ChildLists["Port"]=[] # list of Port objects
		self.FPGAMatrix = Matrix.Matrix() # Empty matrice
		#self.ClockList  = self.ListClock() # list of available clocks
		self.InitParameters(Name)
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("Arch.png")
		except: self.Icon = ""
		self.IconSize   = (30, 20)
	#----------------------------------------------------------------------
	def InitParameters(self, Name):
		self.Parameters["Common"].update({
			})
	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		if Parameter == "Dimensions":
			try: x,y=list(map(int, self.Parameters[ParameterType][Parameter].lower().split('x')))
			except: return False
			if not self.FPGAMatrix.EnlargeMatrix(x, y): return False
		return True
	#----------------------------------------------------------------------
	def SetFromLib(self, Value):
		"""
		Get information from library item and set IP parameters.
		"""
#		TreeMember.SetFromLib(self, Value) # Add all children
		self.Model(Model=HwModel(Value))
		return True
	#----------------------------------------------------------------------
	def SetFromModel(self):
		"""
		Get information from model and set IP parameters.
		"""
		self.FPGAMatrix = Matrix.Matrix(NbElement=1) # TODO : Make it generic
		self.ChildLists["FPGA"]=[]
		ChildFPGA=self.AddChild(Type="FPGA", Name=self.Model.GetFPGA(), FromLib=False)
		ChildFPGA.Parameters["Common"].update(self.Model.AvailableRsc.RscDict)
		xChild, yChild = tuple(map(int, ChildFPGA.Parameters["Parent"]["Position"].split(':')))
		xCur, yCur = self.FPGAMatrix.AddToMatrix(ChildFPGA)
		if xChild!=xCur or yChild!=yCur:
			self.FPGAMatrix.MoveInMatrix(ChildFPGA, xChild, yChild)
		self.FPGAMatrix.Shrink()
		
		return True
	#----------------------------------------------------------------------
	def GetPorts(self, FPGA):
		"""
		Parse constraints file of each FPGA and create children port objects.
		"""
		# Clean port child list
		del self.ChildLists["Port"][:]
		ConstFileName=FPGA.Parameters["Parent"]["Constraints"]
		if ConstFileName==None: return
		CFile    = os.path.join(self.Library, ConstFileName)
		PortDict = Constraints.PortPads(CFile)
		for PortName in list(PortDict.keys()):
			PortChild = self.AddChild("Port", PortName)
			PortChild.Parameters["Parent"]["FPGA"]=FPGA.Parameters["Parent"]["Position"]
			for IOMap in PortDict[PortName]:
				PortChild.Parameters["Common"]["Pads"].append(IOMap)
	#----------------------------------------------------------------------
	def GetAvailablePads(self, Type=None):
		"""
		return pads from '.co' as dictionaries (basic IOs). 
		Type are one of the following:
			'CLOCK'
			'IN'
			'OUT'
			'INOUT'
		"""
		InterfaceDict=self.Model.GetInterface()
		if Type is None:
			return InterfaceDict
		elif Type in InterfaceDict:
			return InterfaceDict[Type]
		else:
			logging.error("No such type '{0}' in {1} interface. Available: {2}.".format(Type, self.Model.Name, list(InterfaceDict.keys())))
	#----------------------------------------------------------------------
	def Synthesize(self, Mod, SrcDirectory, OutputPath, ControlHW=None, RemoteHost=None):
		"""
		Generate a binary for each FPGA of this architecture.
		Return a generator of Synthesis flow object.
		"""
		SynthesisPath=os.path.abspath(os.path.join(OutputPath, self.Model.Name+"_"+Timer.TimeStamp()))
		if not os.path.isdir(SynthesisPath):
			os.makedirs(SynthesisPath)
		
		Serv=LibEditor.ProvidedServiceXml(Mod, Interfaces=[], Infos={"Name": Mod.Name, "Type": "", "Version": "", "Category": ""}, OutputPath=SrcDirectory)
		
		ConstraintFilePath, ModuleWrapper, NewClockSigs=self.Model.GetPadConstraints(Module=Mod, Library=self.Library, OutputPath=SrcDirectory, ControlHW=ControlHW) # ControlHW=ML605
		if ConstraintFilePath is None:
			logging.error("[Synthesize] No FPGA pad constraints generated: Synthesis aborted.")
			Misc.CleanTempFiles(SynthesisPath)
			return None
		
		TopName, TopSource=Mod.GetTop()
		if None in [TopName, TopSource]:
			Mod.GenSrc(Synthesizable=True, OutputDir=OutputPath, TestBench=False, ProcessedServ=dict(), IsTop=True, NewPkg=False, Recursive=True)
			TopName, TopSource=Mod.GetTop()
			
		ModuleWrapper.GenSrc(Synthesizable=True, OutputDir=os.path.dirname(TopSource), TestBench=False, ProcessedServ={Serv.Name:Mod.GetLastCreatedInstance()}, IsTop=True, NewPkg=False, Recursive=True)
		SynthMod=ModuleWrapper
		
		ResultFilesDict=self.Model.Synthesize(Mod=SynthMod, ConstraintFilePath=ConstraintFilePath, SrcDirectory=SrcDirectory, OutputPath=SynthesisPath, RemoteHost=RemoteHost)
		if len(ResultFilesDict)==0: Misc.CleanTempFiles(SynthesisPath)
		return ResultFilesDict
	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, FromLib=False):
		"""
		Add a element as child corresponding to allowed type.
		If FromLib is True, fetch item from library.
		"""
		if not Name: Name = NewName(Type, [item.Parameters["Common"]["Name"] for item in self.ChildLists[Type]])
		if Type == "FPGA": 
			Child=FPGA(Name, Parent=self)
			if FromLib: Child.SetFromLib(Name)
		elif Type == "Port": 
			Child = Port(Name, Signal=None, Pad=None, Alias="", Comments="", Parent=self)
			if FromLib: Child.SetFromLib(Name)
		else:
			logging.warning("Wrong child type '{0}' : child creation aborted.".format(Type))
			raise TypeError
			return None
		self.ChildLists[Type].append(Child)
#		logging.info("Add child '{0}' to '{1}': succeeded.".format(Child, self))
		return Child
	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.Arch(Parameters, self.FPGAMatrix, self.ChildLists["Port"], Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0

#======================================================================
class FPGA(TreeMember):
	"FPGA component of an architecture"
	#----------------------------------------------------------------------
	def __init__(self, Name = "Unkown_FPGA", Parent = None, Bundle=None):
		TreeMember.__init__(self, None, "FPGA", Name, Parent, Bundle=Bundle)
		self.SetIcon()
		self.InitParameters()
		# Allocate position in architecture
		#xmax, ymax = map(int, self.Parent.Parameters["Dimensions"].split(" x "))
#		self.ImplementParameters=None
			
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("FPGA.svg")
		except: self.Icon = ""
		self.IconSize = (20, 20)

	#----------------------------------------------------------------------
	def InitParameters(self):
		self.Parameters["Common"].update({ # Value => list of choices
			"Family": "Spartan6",
			"Brand" : "Xilinx",
			"ChipPackage":"ff1156", 
			"SpeedGrade" : 1,
			})
		self.Parameters["Parent"].update({
			"Position": "0:0",
			"Constraints": None,
			})
		self.Parameters["Resources"].update({})

	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		if Parameter == "Constraints":
			ConstFilePath=os.path.join(self.Library, self.Parameters[ParameterType][Parameter])
			if ConstFilePath==None or ConstFilePath=="": return True
			# Test if Constraints is a valid file
			if not os.path.isfile(ConstFilePath): return False
			# Get the updated port pads from constraints file
			self.Parent.GetPorts(self)
		elif Parameter == "Position":
			try: xNew, yNew = list(map(int, self.Parameters[ParameterType][Parameter].lower().split(':')))
			except: return False
			# Update Matrix state so as to move component to its new coordinates
			if not self.Parent.FPGAMatrix.MoveInMatrix(self, xNew, yNew): return False
		else:
			if not re.match("[a-zA-Z0-9_]\w*", self.Parameters[ParameterType][Parameter]):
				return False
		return True
		
	#----------------------------------------------------------------------
	def SetFromLib(self, Value):
		"""
		Overloaded function.
		Create Ports for Architecture parent after a library import.
		"""
		TreeMember.SetFromLib(self, Value)
		if self.Parent!=None: self.Parent.GetPorts(self)
		
	#----------------------------------------------------------------------
	def Generate(self):
		"Generate project files for this FPGA."
		return Builder.FPGABuilder(
			Name   = self.Parameters["Common"]["Name"], 
			Brand  = self.Parameters["Common"]["Brand"], 
			Family = self.Parameters["Common"]["Family"],
			Position = self.Parameters["Parent"]["Position"], 
			ChipPackage = self.Parameters["Common"]["ChipPackage"], 
			SpeedGrade  = self.Parameters["Common"]["SpeedGrade"],
			Constraints = os.path.join(self.Library, self.Parameters["Parent"]["Constraints"])
			)	

	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, FromLib=False):
		if not Name: Name = NewName(Type, [item.Parameters["Common"]["Name"] for item in self.ChildLists[Type]])
		logging.error("FPGA component cannot have child : aborted.".format(Child, self))
		return None
#		if Type == "Port": 
#			Child = Port(Name, Parent=self)
#		self.ChildLists[Type].append(Child)
#		if LibPath: Child.SetFromLib(Name, LibPath)
#		logging.info("Add child '{0}' to '{1}': succeeded.".format(Child, self))
#		return None

	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.FPGA(Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0

	#----------------------------------------------------------------------
	def Remove(self): # Overload of treemember method
		# Don't forget to remove item from the architecture matrix
		self.Parent.FPGAMatrix.RemoveFromMatrix(self)
		# Now we can remove serenely the treemember
		TreeMember.Remove(self)
		# Update Arch dimensions
		self.Parent.Parameters["Parent"]["Dimensions"]=" x ".join([str(x+1) for x in self.Parent.FPGAMatrix.Dimensions()])+" ({0})".format(len(self.Parent.ChildLists["FPGA"])) # Update Arch dimensions

#======================================================================
class Port(TreeMember):
	"Design architecture"
	#----------------------------------------------------------------------
	def __init__(self, Name = "Arch_0", Signal=None, Pad=None, Alias="", Comments="", Parent = None, Bundle=None):
		TreeMember.__init__(self, None, "Port", Name, Parent, Bundle)
		self.SetIcon()
		self.ChildLists["Peripheral"]=[] # list of child objects
		self.InitParameters(Name)
		self.SaveXML=False
		self.IOMap=None
			
	#----------------------------------------------------------------------
	def SetIcon(self):
		"""
		Set icons from bundle.
		"""
		try: self.Icon = self.Bundle.Get("Port.png")
		except: self.Icon = ""
		self.IconSize   = (30, 20)

	#----------------------------------------------------------------------
	def InitParameters(self, Name):
		self.Parameters["Common"].update({ # Value => list of choices
			"Direction": "INOUT",
			"Pads":[],
			})
		self.Parameters["Parent"].update({
			"FPGA":      "0:0", 
			"Peripheral":"Debug",
			"Size":1,
			})
		self.Parameters["Resources"] = {}

	#----------------------------------------------------------------------
	def TestParameter(self, ParameterType, Parameter):
		"""
		Evaluate if the new parameter value is valid.
		Then execute processing functions according to edited parameter.
		File paths are relative to library path.
		"""
		if not TreeMember.TestParameter(self, ParameterType, Parameter): return False
		if Parameter == "FPGA":
			try: list(map(int, self.Parameters[ParameterType][Parameter].lower().split(':')))
			except: return False
		elif Parameter == "Direction":
			if not self.Parameters[ParameterType][Parameter].upper() in ["IN", "OUT", "INOUT"]:
				return False
		elif Parameter == "Signals":
			if not re.match("[a-zA-Z0-9_/)(]\w*", self.Parameters[ParameterType][Parameter]):
				return False
		return True

	#----------------------------------------------------------------------
	def Generate(self, OutputPath=None):
		"Port: Generate nothing."
		pass

	#----------------------------------------------------------------------
	def AddChild(self, Type, Name=None, FromLib=False):
		logging.warning("'{0}' cannot have child: aborted.".format(self.Type))
		return None

	#----------------------------------------------------------------------
	def Display(self, Ctx, Width, Height, Ratio=1):
		super().Display(Ctx, Width, Height)
		if(self.Drawing):
			Parameters=self.Parameters["Common"].copy()
			Parameters.update(self.Parameters["Parent"])
			Parameters.update(self.Parameters["Resources"])
			W, H = self.Drawing.Port(Parameters, Width=Width, Height=Height, Ratio=Ratio)
			return W, H
		else:
			return 0, 0
		
#======================================================================
def NewName(BaseName, NameList, ForceID=True):
	"""
	Return a Name that is unique to the list, based on the pattern Base-Name + number
	"""
	NameList=list(NameList)
	NB = 0
	if NameList.count(BaseName)>0 or ForceID==True:
		while NameList.count("{0}_{1}".format(BaseName, NB)):
				NB+=1
		NameList.append("{0}_{1}".format(BaseName, NB))
		return 	"{0}_{1}".format(BaseName, NB)
	else:
		NameList.append(BaseName)
		return 	BaseName
		
#=======================================================================
def InstanceName(BaseName, NameList):
	"""
	Return a new name that is not in the list.
	"""
	N=0
	while(BaseName+'_'+str(N) in NameList): N+=1
	return BaseName+'_'+str(N)
		
#======================================================================
#def NewName(BaseName, NameList):
#	"Return a Name that is unique to the list, based on the pattern Base-Name + number"
#	NameList=list(NameList)
#	NB = 0
#	while NameList.count("{0}_{1}".format(BaseName, NB)):
#			NB+=1
#	return 	"{0}_{1}".format(BaseName, NB)

#======================================================================
# XML PROCESSING
#======================================================================
def ToXMLAttributes(Dictionnary):
	"""
	Convert a parameter dictionnary into one compatible with XML (pure string).
	Change all lists into coma joined elements (string).
	Ignore comment key.
	"""
	ChildDict={} # Will contain all subdictionaries
	Attributes={}
	for Key, Val in Dictionnary.items():
		if isinstance(Val, dict):
			ChildDict[Key]=Val
		else:
			XMLKey = GetXMLstringFormat(Key)
			Attributes[XMLKey]=GetXMLstringFormat(Dictionnary[Key])
	return Attributes, ChildDict
	
#======================================================================
def GetXMLstringFormat(Item):
	"""
	Return string representation for specified Item.
	"""
	FormatedString=""
	if isinstance(Item, str):
		FormatedString=Item
	elif isinstance(Item, list):
		if Item!=[]:
			FormatedString=",".join([GetXMLstringFormat(x) for x in Item])+","
		else:
			# Keep a coma so as to recognize it is a list
			FormatedString=","
	elif isinstance(Item, SyntheSys.SysGen.Service):
		FormatedString="$Service={0}:Version={1}".format(Item.Name, Item.Version)
	elif isinstance(Item, SyntheSys.SysGen.Module):
		FormatedString="$Module={0}:Version={1}".format(Item.Name, Item.Version)
	elif isinstance(Item, SyntheSys.SysGen.Signal):
		FormatedString="$Signal={0}:Type={1}:PTypeImport={1}:Size={1}:Default={1}:Dir={1}:Modifier={1}:share={1}".format(Item.Name, Item.Type, Item.TypeImport, Item.Size, Item.Default, Item.Direction, Item.Modifier, Item.share)
		FormatedString = FormatedString.replace('/', '__') # For signals special properties
		FormatedString = FormatedString.replace(')', '...') # For signals special properties
		FormatedString = FormatedString.replace('(', '..') # For signals special properties
		FormatedString = FormatedString.replace(' ', '.') # For signals special properties
	elif Item==None:
		return ""
	else:
		return str(Item)
	return FormatedString
	
#======================================================================
def DecodeXMLstring(XMLString):
	"""
	Return item represented in an XML format string.
	"""
	if XMLString.startswith('$'):
		PropertiesList = [x.split('=') for x in XMLString[1:].split(':')]
		ItemType, Name = PropertiesList[0]
		if ItemType=="Service":
			V, Version=PropertiesList[1]
		elif ItemType=="Module":
			V, Version=PropertiesList[1]
		elif ItemType=="Signal":
			for PropName, Prop in PropertiesList:
				Prop = Prop.replace('__', '/') # For signals special properties
				Prop = Prop.replace('...', ')') # For signals special properties
				Prop = Prop.replace('..', '(') # For signals special properties
				Prop = Prop.replace('.', ' ') # For signals special properties
			Toto, Type=PropertiesList[1]
			Toto, PTypeImport=PropertiesList[2]
			Toto, Size=PropertiesList[3]
			Toto, Default=PropertiesList[4]
			Toto, Dir=PropertiesList[5]
			Toto, Modifier=PropertiesList[6]
			Toto, Share=PropertiesList[7]
			Item = SyntheSys.SysGen.Service()
	else: Item = XMLString
	return Item

	
#======================================================================
def XMLElmt(ElmtTag, ParamDict, Parent=None):
	"""
	Return a XML element built from ParamDict (and optional comment).
	"""
	Attr, ParamChildDict = ToXMLAttributes(ParamDict)
	if Parent!=None:
		NewElement = etree.SubElement(Parent, ElmtTag, **Attr)
	else:
		NewElement = etree.Element(ElmtTag, **Attr)
	#NewElement=etree.Element(ElmtName, **Attr)
	#if "Comments" in ParamDict: NewElement.text=ParamDict["Comments"]
	for ParamChild in list(ParamChildDict.keys()):
		XMLElmt(ParamChild, ParamChildDict[ParamChild], NewElement)
		#NewElement.append(XMLElmt(ParamChild, ParamChildDict[ParamChild]))
	return NewElement

#======================================================================
def FromXMLAttribute(Attributes):
	"""
	Convert a xml attributes dictionary into one compatible with tool.
	Change all coma joined elements (string) into lists.
	"""
	Dictionnary={}
	for Key, Val in Attributes.items():
		if Attributes[Key].count(','):
			# Keep only non empty strings
			StrList=[x for x in Attributes[Key].split(',') if x!=""]
			ItemList = [DecodeXMLstring(x) for x in StrList]
			Dictionnary[DecodeXMLstring(Key)]=ItemList
		else:
			Dictionnary[DecodeXMLstring(Key)]=DecodeXMLstring(Val)
	return Dictionnary
	
#======================================================================
def Elmt2Dict(XMLElement):
	"""
	Return a Dictionary (and comment) built from XML elementTree object.
	"""
	Comment=""
	ElmtDict = FromXMLAttribute(XMLElement.attrib)
	for ElmtChild in XMLElement:
		ChildElmtDict = Elmt2Dict(ElmtChild) # Recursive
		#if Comments!=None and ChildElmtDict.get("Comments")!=None: 
		#	Comment += ChildElmtDict.get("Comments")
		ElmtDict[ElmtChild.tag] = ChildElmtDict
	#if XMLElement.text!="":
	#	Comment+='\n'+str(XMLElement.text).strip().strip('\n').strip()
	return ElmtDict#, Comment

	
#======================================================================
# XML PROCESSING
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
	

#======================================================================
# SOURCE SORTING
#======================================================================
def Parse(SrcList):
	"""
	Use C++ HDL parser to get Module, Signals, and ordered Source list.
	"""
	Module, Signals, Sources, Generics = IPGen.Parse(SrcList)
	return Module, Signals, Sources, Generics
	
	
	
	
	
	
	
	
	
	
	
	
	

