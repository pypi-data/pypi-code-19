#!/usr/bin/python


import os, sys, logging, shutil, math
import collections
from lxml import etree

from SysGen.PackageBuilder import PackageBuilder
from SysGen.Signal import Signal
from SysGen.Condition import Condition
from SysGen.Interface import Interface
from SysGen.Module import Module
from SysGen import HDLEditor as HDL
from SysGen import LibEditor

from SysGen.FiniteStateMachine import FSM, FSMState
from SysGen.Assignment import AssignmentStatement

from Utilities.Misc import SyntheSysError

#=======================================================================
class Service(PackageBuilder):
	#---------------------------------------------------------------
	def __init__(self, XMLElmt):
		"""
		Set global service definition parameters from an XML Element.
		"""
		super().__init__()
		self.Name    = ""
		self.Alias   = ""
		self.Type    = "" # Orthogonal / simple 
		self.Version = ""
		self.Category  = ""
		self.Shared  = False
		self.IsCommunication = False
		self.Params  = collections.OrderedDict() # Dictionary of service parameters
		self.Vars    = {}
		self.Ports   = collections.OrderedDict() # Dictionary of service ports interface
		self.ModList = [] # List of modules offering this service
		self.Interfaces=[]
		self.Wrappers=[]
		#self.NoCMap={"Position":"", "Target":"",}
		self.XMLElmt = XMLElmt
		
		try: 
			if not self.SetFromXML(XMLElmt): logging.error("Unable to parse service XML content.")
		except SyntheSysError: 
			logging.error("Service '{0}' parsing failure.".format(self.Name))
			raise SyntheSysError
	#---------------------------------------------------------------
	def DumpToFile(self, OutputPath):
		"""
		Write XML informations to specified file.
		"""
		ServiceFilePath=os.path.join(OutputPath, "Service_{0}.xml".format(self.Name))
		with open(ServiceFilePath, "wb+") as XMLFile:
			XMLFile.write(etree.tostring(self.XMLElmt, encoding="UTF-8", pretty_print=True))
		return ServiceFilePath
	#---------------------------------------------------------------
	def GetXMLElmt(self):
		"""
		return XML representation of Service.
		"""
		return self.XMLElmt
	#---------------------------------------------------------------
	def Copy(self):
		"""
		Return a copy of the object.
		"""
		S=Service(self.XMLElmt)
		S.Alias=self.Alias
		S.ModList=self.ModList[:] # List of modules offering this service
		S.Wrappers=self.Wrappers[:]
		return S
	#---------------------------------------------------------------
	def UpdateXML(self):
		"""
		Return XML representation of attributes.
		"""
		self.XMLElmt=LibEditor.ServiceXml(self)
	#---------------------------------------------------------------
	def SetFromXML(self, XMLElmt):
		"""
		Parse XML content and extract service information.
		"""
		if XMLElmt.tag!="service":
			logging.error("XML content do not describe a service.") 
			raise SyntheSysError("XML content do not describe a service.") 
		# Build a service object from Service name, Type, Version
		self.Name      = XMLElmt.attrib.get("name")
		self.Alias     = self.Name+"_0"
		self.Type      = XMLElmt.attrib.get("type")
		self.Version   = XMLElmt.attrib.get("version")
		self.Category  = XMLElmt.attrib.get("category")
		self.Shared    = XMLElmt.attrib.get("shared")
		self.IsCommunication=False
		if "communication" in XMLElmt.attrib:
			if XMLElmt.attrib.get("communication").lower()=="true":
				self.IsCommunication=True
#		logging.info("Found service: '{0}'".format(self.Name))
		# Get each parameter
		# First get default value for each parameter
		for ParamElmt in XMLElmt.iterchildren("parameter"):
			Attr = ParamElmt.attrib
			self.Vars[Attr.get("name")]=Attr.get("default")
		# Then get every parameter than can depend of previous or following parameters
		for ParamElmt in XMLElmt.iterchildren("parameter"):
			Attr = ParamElmt.attrib
			P=self.AddParameter(Attr.get("name"), Attr.get("type"), Attr.get("typeimport"), Attr.get("size"), Attr.get("default"))
		# Get each input
		for InputElmt in XMLElmt.iterchildren("input"):
			Attr = InputElmt.attrib
			self.AddPort(Attr.get("name"), "IN", Attr.get("type"), Attr.get("typeimport"), Attr.get("size"), Attr.get("default"), Attr.get("modifier"))
		# Get each output
		for OutputElmt in XMLElmt.iterchildren("output"):
			Attr = OutputElmt.attrib
			self.AddPort(Attr.get("name"), "OUT", Attr.get("type"), Attr.get("typeimport"), Attr.get("size"), Attr.get("default"), Attr.get("modifier"))
			
		# Get each Interface
		del self.Interfaces[:]
		self.Interfaces=[]
		for InterfaceElmt in XMLElmt.iterchildren("interface"):
			self.AddInterface(InterfaceElmt)
			
		# Update modifier of all ports
		for P in list(self.Ports.values()):
			if P.Modifier!=None:
				if P.Modifier=="": P.Modifier=None
				else: P.Modifier=self.Params[P.Modifier]
			
		return True
	#---------------------------------------------------------------
	def AddParameter(self, PName, PType, PTypeImport, PSize, PDefault, IdxDict={}):
		"""
		Add a parameter (defined by Name/type/TypeImport/size/default_value) to this service.
		"""
		Variables=self.Vars.copy()
		Variables.update(IdxDict)
		try: P=Signal(Name=PName, Type=PType, PTypeImport=PTypeImport, Size=PSize, Default=PDefault, ParamVars=Variables.copy())
		except:
			logging.error("Cannot evaluate parameter '{0}' in service '{1}'.".format(PName, self.Name))
			raise SyntheSysError
		self.Params[PName] = P
		self.Params[PName].IsParam = True
		self.Vars[PName]=self.Params[PName].integers(Base=10, Variables=Variables)
		return P
	#---------------------------------------------------------------
	def UpdateAllValues(self, ValueDict):
		"""
		Change values of each port/params and their respective "usedparam" dictionary.
		"""
		for PName, PVal in ValueDict.items():
			if PName in self.Params:
				self.Params[PName].SetValue(PVal)
		for PName, PSig  in self.Params.items():
				PSig.UpdateAllValues(ValueDict)
		
		for M in self.GetModules(Constraints=None):
			M.UpdateAllValues(ValueDict)
			
		for I in self.Interfaces:
			I.UpdateAllValues(ValueDict)
		return
	#---------------------------------------------------------------
	def AddPort(self, PName, PDir, PType, PTypeImport, PSize, PDefault, PModifier=None, IdxDict={}):
		"""
		Add a port (defined by Name/type/TypeImport/size/default_value) to this service.
		"""
		Variables=self.Vars.copy()
		Variables.update(IdxDict)
		self.Ports[PName] = Signal(Name=PName, Type=PType, PTypeImport=PTypeImport, Size=PSize, Default=PDefault, Dir=PDir, Modifier=PModifier, ParamVars=Variables.copy())
#		self.Ports[PName]._UsedParams.update(self.Vars.copy())
	#---------------------------------------------------------------
	def GetPortsDict(self):
		"""
		Return the dictionary of module ports.
		"""
		return self.Ports.copy()
	#---------------------------------------------------------------
	def AddInterface(self, Itf):
		"""
		Add an interface object to this service.
		"""
		ServVar={}
		for Param in list(self.Params.values()):
			ServVar[Param.Name]=Param.Default if Param.Default!='' else 0
		if isinstance(Itf, etree._Element):
			NewITF = Interface(Service=self, XMLElmt=Itf)
		elif isinstance(Itf, dict):
			NewITF = Interface(Service=self, Infos=Itf)
		elif isinstance(Itf, Interface):
			NewITF = Itf.Copy()
		else:
			logging.error("[AddInterface] Bad format '{0}' for interface '{1}'. Unable to add it to service '{2}'.".format(type(Itf), repr(Itf), self))
			return
		NewITF.ParamVars.update(self.Vars.copy())
		self.Interfaces.append(NewITF)
	#---------------------------------------------------------------
	def AddWrapper(self, WrappedServ):
		"""
		Add wrapper in a list for this service.
		=> mean new interfaces.
		"""
		self.Wrappers.append(WrappedServ)
		return True
	#---------------------------------------------------------------
	def AddModule(self, Mod):
		"""
		Add a module implementing this service.
		"""
		self.ModList.append(Mod)
	#---------------------------------------------------------------
	def GetModule(self, Constraints=None):
		"""
		Return the best (in terms of area) module implementing this service.
		"""
		Candidates=self.GetModules(Constraints=Constraints)
		return Candidates[0] if len(Candidates) else None
	#---------------------------------------------------------------
	def GetModules(self, Constraints=None, Task=None):
		"""
		Return a module implementing this service.
		"""
#		if self.IsOrthogonal(): self.SpecialModule=True
		# TODO: manage constraints
		if self.Name=="clock" or self.Name=="reset": Constraints = None
#			print("sConstraints:",Constraints)
#			print("self.ModList:",self.ModList)
		if Constraints is None:
			SelectedMod=self.ModList
		else:
#			MatchedList=self.ModList[:]
#			for Adj, AdjVal in Constraints["Adjustable"].items():
#				for Mod in self.ModList:
#					if Adj not in Mod.ProvidedServMap[self.Name]:
#						MatchedList.remove(Mod)
#					else:
#						Mod.Params[Adj].Default=AdjVal
#			for Fixed, FVal in Constraints["Fixed"].items():
#				for Mod in MatchedList[:]:
#					if Fixed not in Mod.ProvidedServMap[self.Name]:
#						MatchedList.remove(Mod)
#					elif Mod.Params[Fixed].Default!=FVal:
#						MatchedList.remove(Mod)
			SelectedMod=[M for M in self.ModList if Constraints.SatisfiedFor(Module=M)]
			if not (self.Name in ["Reduce", "clock", "reset", "Switch", 'Select']):
				if not (Task is None):
	#				print("Task:", Task)
	#				print("Task.Inputs:", Task.Inputs)
	#				print("Task.Inputs vars:", [t.SyntheSys__PythonVar for t in Task.Inputs])
					NewList=[]
					for M in SelectedMod:
#						print("M.TypeSignature:", M.TypeSignature)
#						print("Task.TypeSignature():", Task.TypeSignature())
						if M.TypeSignature==Task.TypeSignature():
							NewList.append(M)
					if len(NewList)==0:
						Msg="No module matches task '{0}' type signature '{1}'".format(Task, Task.TypeSignature());logging.error(Msg)
						raise SyntheSysError(Msg)
					SelectedMod=NewList
#			if self.Name=="clock":
#				print("SelectedMod:", SelectedMod)
		
		for M in SelectedMod:
			M.PropagateServDefaultParam(self)
		
		return SelectedMod
	#---------------------------------------------------------------
	def PropagateModDefaultParam(self, Mod, ModMap):
		"""
		Set default value for each parameters/port from module that requires this service.
		"""
		for PName, P in Mod.Params.items():
			if PName in ModMap:
				SignalName=ModMap[PName][1] # ModMap[ParameterName] => Actual=[Instance, SignalName, Index]
				if SignalName!=PName:
					if PName in self.Params:
						self.Params[PName].SetValue(SignalName)
						self.Params[PName].SetValue(SignalName)
		return
	#---------------------------------------------------------------
	def GetInterfaces(self, InterfaceName=None, Direction=None):
		"""
		Return the interface object corresponding to the name if present, None otherwise.
		"""
		if (InterfaceName is None):
			if (Direction is None): 
				return self.Interfaces
			else:
				for ITF in self.Interfaces:
					if ITF.Direction==Direction: 
						return [ITF,] 
		
		Interfaces=[]
		for ITF in self.Interfaces:
			if ITF.Name==InterfaceName:
				Interfaces.append(ITF) 
		
		if len(Interfaces)==0:
			# Seek for wrapped interfaces
			for W in self.Wrappers:
				for ITF in W.Interfaces:
					if ITF.Name==InterfaceName:
						Interfaces.append(ITF) 
			
		return Interfaces
	#---------------------------------------------------------------
	def GetOutputDataSize(self):
		"""
		Return the number of bits for output data.
		"""
		GetSize=lambda Sig: eval(str(Sig.Size), Sig.GetUsedParam())
		Sizes=[]
		for ITF in self.Interfaces:
			if "OUT" in ITF.Direction: 
				Sizes+=[GetSize(x) for x in [x for x in ITF.DataList if x.Direction=="OUT"]]
		return sum(Sizes)
	#---------------------------------------------------------------
	def GenInputStim(self, TaskValues, **ParamDict):
		"""
		Return sequence of stimuli values corresponding to stimuli names for service interface.
		"""
#		StimNames=map(lambda x: str(x), filter(lambda x: x.Direction=="OUT", self.Ports.values()))
		InputITF=self.GetInterfaces(Direction="IN")[0] # TODO: Manage multi input interfaces
		
		StimValueDict={}
		ValueDict={}

		AddedValues={}
		for InputStim, Comment in InputITF.GenStim(TaskValues, **ParamDict):
#			print("InputStim:", InputStim)
			for Name, Value in InputStim.items():
#				print("   Name:", Name)
#				print("   Value:", Value)
				if Name in AddedValues:
					AddedValues[Name].append(Value)
				else:
					AddedValues[Name]=[Value,]

		for Name in AddedValues:
			NormalizedValues=[]
			NbData=len(AddedValues[Name])
			i=0
			Tab=AddedValues[Name]
			while(i<NbData):
				if isinstance(Tab[i], list) or isinstance(Tab[i], tuple):	
					Start=i
					while(isinstance(Tab[i], list) or isinstance(Tab[i], tuple)):
						i+=1
						if i>=NbData: break
					for Elements in zip(*Tab[Start:i]):
						for Element in Elements:
							NormalizedValues.append(Element)
				else:
					NormalizedValues.append(Tab[i])
					i+=1
		
			if Name in StimValueDict: 
				StimValueDict[Name]+=NormalizedValues
			else: 
				StimValueDict[Name]=NormalizedValues
		
		InputITF.Protocol
		for Name, Values in StimValueDict.items():
			ValueDict[Name]=[]
			for i in range(0, len(Values), InputITF.Protocol.NbSteps()):
				ValueDict[Name].append(Values[i])
					
#		print("StimValueDict:", StimValueDict)
#		print("ValueDict:", ValueDict)
#		input()
		return StimValueDict, ValueDict
	#---------------------------------------------------------------
	def GetCompatibleItf(self, TargetItf):
		"""
		Return list of interfaces that fullfill compatibility constraints with TargetItf.
		"""
		if len(TargetItf.Dirs):
			if "IN" in TargetItf.Dirs:
				for I in self.Interfaces:
					if "IN" in I.Dirs:
						return [I,]
			else: # Out
				for I in self.Interfaces:
					if "OUT" in I.Dirs:
						return [I,]
				
		else:
			CompatibleItf=[]
			for I in self.Interfaces:
				if "IN" in I.Dirs and "OUT" in I.Dirs:
					return [I,]
				elif "IN" in I.Dirs:
					if "IN" not in [x.Dirs[0] for x in CompatibleItf]:
						CompatibleItf.append(I)
				else: # Out
					if "OUT" not in [x.Dirs[0] for x in CompatibleItf]:
						CompatibleItf.append(I)
				if len(CompatibleItf)==2:
					return CompatibleItf
		return []
		
	#---------------------------------------------------------------
	def GenerateWrapper(self, Mod, InterfaceList, Name, AdapterServ, ClockServ, RstServ, OutputPath=None):
		"""
		Return the interface object corresponding to the name if present, None otherwise.
		"""
		GeneratedAdapters=[]
#		AdapterMod, AdapterServ=self.GenerateAdapter(self.Name+"_{0}_Adapter".format(InterfaceList[0].Name), InterfaceList, ClockServ=ClockServ, RstServ=RstServ, OutputPath=OutputPath)

		#---------------------------------
		AdapterServ.Alias="NetworkAdapter"
		#---------------------------------
		AdapterMod = AdapterServ.GetModule()
		
		if AdapterMod!=None:
			#---------------------------------	
			# Mark service as wrapped !
			# Create a new wrapper module
			Infos={}
			Infos["Name"]    = "{0}".format(Name)
			Infos["Version"] = ""
			Infos["Title"]   = "Wrapper for adaptation to interfaces {0}".format(list(map(str, InterfaceList)))
			Infos["Purpose"] = "Wrapper for adaptation to interfaces {0}".format(list(map(str, InterfaceList)))
			Infos["Desc"]    = "Wrapper for adaptation to interfaces {0}".format(list(map(str, InterfaceList)))
			Infos["Tool"]    = "ISE 13.1"
			Infos["Area"]    = ""
			Infos["Speed"]   = ""
			Infos["Issues"]  = ""
			# Empty new module-----------------------------------
			Ports=[]
			for I in InterfaceList:
				Ports+=I.GetSignals(Ctrl=True, Data=True, Directions=["IN", 'OUT'])
			Params=collections.OrderedDict()
			Params.update(AdapterMod.Params)
			Params.update(self.Params)
			WrappedMod=LibEditor.NewModule(Infos=Infos, Params=list(Params.values()), Ports=Ports, Clocks=[], Resets=[], Sources=[])
			WrappedMod.AddResource(Dev="ALL", RName="", Rused=0)
#			WrappedMod.Params.update(self.Params)
#			WrappedMod.Params.update(InterfaceList[0].Service.Params)
#			# Set Adapter service parameters --------------------
#			for PName in Parameters:
#				if PName in AdapterServ.Params:
#					WrappedMod.MapServParam(AdapterServ, PName, Parameters[PName].Default)
			Mapping=collections.OrderedDict()
			ComponentMapping=collections.OrderedDict()
					
			for PName, P in self.Params.items():
				if PName in ComponentMapping: logging.debug("[GenerateWrapper] Parameter '{0}' already mapped: overwritten.".format(PName))
				ComponentMapping[PName]=([[None, PName, None],], True, {})
				
			for I in InterfaceList:
				for Sig, Target in I.Mapping.items():
					Mapping[Sig]=([[AdapterServ.Alias, Target, None],], True, {})
					
			for PName, P in AdapterServ.Params.items():
				if PName in Mapping: logging.debug("[GenerateWrapper] Parameter '{0}' already mapped: overwritten.".format(PName))
				Mapping[PName]=([[None, PName, None],], True, {})
				
#			ClockResetSigs=self.GetClockNames()+self.GetResetNames()
#			print("ClockResetSigs:", ClockResetSigs)
#			input()
			for P in Ports:
#				if PName in ClockResetSigs: continue
				if P.Name in Mapping: logging.debug("[GenerateWrapper] Port '{0}' already mapped: overwritten.".format(P.Name))
				Mapping[P.Name]=([[None, P.Name, None],], True, {})
				
			for PName, P in AdapterServ.Ports.items():
				if PName in Mapping: continue
				ComponentMapping[PName]=([[AdapterServ.Alias, PName, None],], True, {})
				
			if not (ClockServ is None or RstServ is None):
				WrappedMod.IdentifyServices([ClockServ, RstServ])
#			AdapterMod.IdentifyServices([ClockServ, RstServ])
#			WrappedMod.Connect(InterfaceList, self.Interfaces)
			####################################
			Infos={}	
			Infos["Name"]     = "{0}_Service".format(Name)
			Infos["Type"]     = self.Type
			Infos["Version"]  = self.Version
			Infos["Category"] = self.Category
			#---------------------------------
			WrapperInterfaces=[x.Copy() for x in InterfaceList]	
			WrappedService = LibEditor.ProvidedServiceXml(Mod=WrappedMod, Interfaces=WrapperInterfaces, Infos=Infos, OutputPath=OutputPath)
			#---------------------------------
			for Item in WrapperInterfaces:
				Item.ServiceAlias=WrappedService
				Item.Service=WrappedService
			WrappedService.Params.update(self.Params)
			#---------------------------------
#			WrappedMod.DumpToFile(os.path.join(OutputPath, "Module_{0}.xml".format(WrappedMod.Name)))
#			WrappedService.DumpToFile(os.path.join(OutputPath, "Service_{0}.xml".format(WrappedService.Name)))
			
			self.AddWrapper(WrappedService)
			for Item in (WrappedService, WrappedMod):
				Item.UpdateXML()
				
			WrappedMod.MapSubServices(Services=[AdapterServ, self], Mappings=[Mapping, ComponentMapping])
			
			WrappedMod.Reload()
			WrappedMod.IdentifyServices([AdapterServ, WrappedService, self])

			return WrappedService, WrappedMod, AdapterMod, AdapterServ # Must be referenced in the library
		else: 	
			return None, None, None, None
			# TODO: Functions to implement: 
#				TargetItf.GenerateAdapter(Itf), 
	#---------------------------------------------------------------
	def GenerateAdapter(self, AdapterName, Interfaces, ClockServ, RstServ, OutputPath="./"):
		"""
		Generate a new module and service associated for 
		wrapping ITF to be compatible with this interface.
		"""
		# Then determine the number of states for IN and OUT transfert protocol
		if len(Interfaces)==0: 
			logging.error("No interfaces to adapt to. Aborted.")
			return None, None
			
		StateGraphs, Ports, FSMParams, Internals, AbsoluteAssignments = self.GetProtocolStates(AdapterName, Interfaces)
		if StateGraphs is None:
			logging.error("No state graphs generated. Aborted.")
			return None, None 

		ClkName="Clk"
		RstName="Rst"
		Clock = Signal(Name=ClkName, Type="logic", PTypeImport=None, Size=1, Default=0, Dir="IN", Modifier=None)
		Reset = Signal(Name=RstName, Type="logic", PTypeImport=None, Size=1, Default=0, Dir="IN", Modifier=None)
		
		#-------------------------
		Declarations, Content= "", ""
		for StateGraph in StateGraphs:
			D, C = HDL.FSM_2Blocks(
					StateGraph, 
					Name=str(StateGraph),#"FSM".format(self, "_".join(map(str, Interfaces))), 
					Clock=Clock, 
					Reset=Reset
					)
			Declarations+=D
			Content+=C
	
		
			PNGPath=StateGraph.ToPNG(OutputPath)
			logging.info("Generate PNG for adapter FSM ('{0}')".format(PNGPath))
			
		PortNames=[x.GetName() for x in Ports]
		for Name, Sig in Internals.items():
			if Sig.GetName() in PortNames: continue
			HDLSig=Sig if isinstance(Sig, HDL.Signal) else Sig.HDLFormat()
#			if Name in FSMParams:
#				HDLSig.SetInitialValue(FSMParams[Name])
			Declarations+=HDLSig.Declare()
			
		Content+=HDL.AbsoluteAssignment(AssignmentList=AbsoluteAssignments)
		#-------------------------
			
		#--------Write HDL file--------
		I1, I2 = "_".join(map(str, Interfaces)), str(self)
	
		Infos={}
		Infos["Name"]    = AdapterName
		Infos["Version"] = "Automatically Generated"
		Infos["Title"]   = "Adapter for {0} adaptation to interface {1}".format(I1, I2)
		Infos["Purpose"] = "Protocol conversion"
		Infos["Desc"]    = "Adapter that Convert {0} protocol to {1}.".format(I1, I2)
		Infos["Tool"]    = "ISE 13.1"
		Infos["Area"]    = ""
		Infos["Speed"]   = ""
		Infos["Issues"]  = ""
		TargetFile=os.path.join(OutputPath, AdapterName)
		logging.info("Write HDL to file '{0}'.".format(TargetFile))
	
		UsedParam=[]
		for PName, P in Interfaces[0].GetUsedParam(GetSignals=True).items():
			UsedParam.append(P)
		Parameters=UsedParam
		ClockNames=[ClkName,]
		ResetNames=[RstName,]
	
		AdapterMod=LibEditor.NewModule(
					Infos=Infos, 
					Params=Parameters+list(FSMParams.values()), 
					Ports=Ports+[Clock, Reset], 
					Clocks=ClockNames, 
					Resets=ResetNames, 
					Sources=[])

		AdapterMod.UsedParams+=[x.GetName() for x in list(FSMParams.values())]
		
		if not os.path.isdir(OutputPath):
			os.makedirs(OutputPath)
		
		AdapterMod.IdentifyServices([ClockServ, RstServ])#Mod.GetReqServ("Reset")+Mod.GetReqServ("Clock")) 
		AdapterMod.UpdateXML()
		logging.info("Generate HDL for adapter...")
		Packages=["IEEE.std_logic_1164", "IEEE.std_logic_signed", "IEEE.numeric_std"]
		TargetFile = LibEditor.HDLModule(	
						OutputPath   = OutputPath, 
						Mod          = AdapterMod, 
						Packages     = Packages, 
						Libraries    = ["IEEE",], 
						Declarations = Declarations, 
						Content      = Content)
		AdapterMod.Sources["RTL"].append(TargetFile)
		AdapterMod.UpdateXML()
		AdapterMod.Reload()
		AdapterMod.IdentifyServices([ClockServ, RstServ]) 
		#---------------------------------	
#		InstanceMapping={}
		ResetNames=AdapterMod.GetResetNames()
		ClockNames=AdapterMod.GetClockNames()
		ImplicitSignals=ResetNames+ClockNames
		AMap=collections.OrderedDict()
		for PName, P in AdapterMod.Ports.items():
			if PName in ImplicitSignals: continue
			AMap[PName]=PName
		for PName, P in AdapterMod.Params.items():
			AMap[PName]=PName
			
		#---------------------------------	
		Infos={}	
		Infos["Name"]     = AdapterName
		Infos["Type"]     = "adapter"
		Infos["Version"]  = self.Version
		Infos["Category"] = self.Category
		
		AdapterInterfaces=[x.Copy() for x in Interfaces]
		AdapterServ = LibEditor.ProvidedServiceXml(
						Mod=AdapterMod, 
						Interfaces=AdapterInterfaces, 
						Infos=Infos, 
						OutputPath=None
						)
		AdapterMod.ProvidedServMap[AdapterName]=AMap
		#---------------------------------
		for Item in AdapterInterfaces:
			Item.Service=AdapterServ
	
#		AdapterMod.DumpToFile(os.path.join(OutputPath, "Module_{0}.xml".format(AdapterMod.Name)))
#		AdapterServ.DumpToFile(os.path.join(OutputPath, "Service_{0}.xml".format(AdapterServ.Name)))
		
		AdapterMod.IdentifyServices([AdapterServ,]) 
		return AdapterMod, AdapterServ
	#----------------------------------------------------------------------
	def GetProtocolStates(self, Name, Interfaces):
		"""
		Return a list of states needed to perform protocol conversion and
		a networkx graph of states.
			self[OUT] => ITF[IN]
			ITF[OUT]  => self[IN]
		"""
		AbsoluteAssignments=[]
		RegisterDict={}
		RegisterAssignDict={}
		MasterRegValuesDict={}
		SlaveRegValuesDict={}
		#--------Generate HDL Code--------
		MasterIn, MasterOut, SlaveIn, SlaveOut = None, None, None, None 
		logging.debug("Adaptation of interfaces: {0}".format([str(x) for x in self.Interfaces]))
		logging.debug("---------- to interfaces  : {0}".format([str(x) for x in Interfaces]))
		for MasterItf in Interfaces:
			IProt=MasterItf.Protocol
			if MasterItf.Direction=="IN":      MasterIn=IProt
			elif MasterItf.Direction=="OUT":   MasterOut=IProt
			elif MasterItf.Direction=="INOUT": MasterIn=IProt;MasterOut=IProt
			RegisterDict.update(IProt.GetRegisters())
			RegisterAssignDict.update(IProt.GetRegisterAssignments())
			MasterRegValuesDict.update(IProt.RegValues)
		for SlaveItf in self.Interfaces:
			IProt=SlaveItf.Protocol
			if SlaveItf.Direction=="IN":      SlaveIn=IProt
			elif SlaveItf.Direction=="OUT":   SlaveOut=IProt
			elif SlaveItf.Direction=="INOUT": SlaveIn=IProt;SlaveOut=IProt
			RegisterDict.update(IProt.GetRegisters())
			RegisterAssignDict.update(IProt.GetRegisterAssignments())
			SlaveRegValuesDict.update(IProt.RegValues)
		FSMParams={}
		
		for Prot in [MasterOut, SlaveIn, MasterIn, SlaveOut]:
			if Prot is None: 
				logging.error("[Protocol adaptation] No interface to adapt to. Aborted.")
				return None, None, None, None  
			Prot.Reset()
		InputAdapterFSM,  InputFSMParams, InternalDict1=self.GenerateAdapterFSM("InputAdapter", MasterOut, SlaveIn)
		OutputAdapterFSM, OutputFSMParams, InternalDict2=self.GenerateAdapterFSM("OutputAdapter", SlaveOut, MasterIn)
		FSMParams.update(InputFSMParams)
		FSMParams.update(OutputFSMParams)
		
		InternalDict=InternalDict1.copy()
		InternalDict.update(InternalDict2)
		#---------------------------------
		
		#----------------Define new interfaces--------------------------
		Ports=[]
		#---------------------------------------------------------------
		# Port directions must be inverted in adapter interface. Output must be read, input written.
		for I in self.Interfaces+Interfaces:
			SigList=[x.Copy() for x in I.GetSignals(Ctrl=True, Data=True, Directions=["IN", 'OUT'])]
			for S in SigList:
				S.InverseDirection()
#				S.Name=I.Mapping[S.Name]
			Ports+=SigList
			
			for AssigneeName, Assignor in I.Tags.items():
				Assignee=Assignor.Copy()
				Idx=Assignor.GetIndex()
				if not (Idx is None): Assignee.Size=str(Idx.start)+"+1-"+str(Idx.stop)
				Assignee.SetName(AssigneeName)
				Ports.append(Assignee)
				AA=AssignmentStatement(Assignee=Assignee.HDLFormat(), Assignor=Assignor.HDLFormat(), Cond=None, Desc="Set tag of register")
				AbsoluteAssignments.append(AA)
		for P in self.Ports.values(): 
			if P.GetName() in [x.GetName() for x in Ports]: continue
			PCopy=P.Copy()
			PCopy.InverseDirection()
			Ports.append(PCopy)

		return [InputAdapterFSM, OutputAdapterFSM], Ports, FSMParams, InternalDict, AbsoluteAssignments
	#----------------------------------------------------------------------
	def GenerateAdapterFSM(self, Name, Master, Slave):
		"""
		Generate FSM for a Master/slave adaptation.
		Assumptions:
			- Master has no serialization factor
			- Slave has only one step
			- Master has only one data signal
		"""
		Master, Slave=Rearrange(Master, Slave)
		AdapterFSM=FSM("{0}_FSM".format(Name))
		FSMParams={}
		MasterOutCtrls=[]
		SlaveOutCtrls=[]
		#---------------------------------
		# Registers are AssignmentSignal
		InternalDict={}
		for Prot in [Master, Slave]:
			for R in list(Prot.GetRegisters().values()):
				R.SetIndex(None) # When indexing interfaces, registers are indexed => Wrong declaration format.
				SigName=R.GetName()#.split('(')[0]
				InternalDict[SigName]=R
#				if SigName in RegValDict:
#					R.Value=MasterRegValuesDict[SigName]
#				else:
#					R.Value=SlaveRegValuesDict[SigName]
		
		#----Assign ctrl signals----
		AssignedCtrlList=[]
		for Prot in [Master, Slave]:
			for C in Prot.GetAssignedCtrl():
				AssignedCtrlList.append(C.Copy())
				HDLSig=C.HDLFormat()
				RA=AssignmentStatement(Assignee=HDLSig, Assignor=0, Cond=None, Desc="Default value")
				AdapterFSM.AddResetAssignment(RA)
		#----------------------------
		logging.debug("* Steps Master out : {0}".format(Master._Steps))
#		logging.debug("\t> {0}".format([list(map(str, x.GetOutputs()+x.GetInputs())) for x in Master._Steps]))
		logging.debug("* Steps slave in   : {0}".format(Slave._Steps))
#		logging.debug("\t> {0}".format([list(map(str, x.GetOutputs()+x.GetInputs())) for x in Slave._Steps]))
		for Step in Master.IterSteps():
			if len(Step.GetOutputs()+Step.GetInputs())==0:
				logging.error("[{0}] Empty protocol step '{1}'".format(Master, Step))
				return AdapterFSM, FSMParams, {}
		for Step in Slave.IterSteps():
			if len(Step.GetOutputs()+Step.GetInputs())==0:	
				logging.error("[{0}] Empty protocol step '{1}'".format(Slave, Step))
				return AdapterFSM, FSMParams, {}
		#----------------------------
		IterCnt=0
		MasterDataSaved=False
		while Slave.HasDataToBeWritten() or Master.HasDataToBeRead():
		
			IterCnt+=1
			if IterCnt>50:
				logging.error("Reach the maximum number of iterations. Stop FSM generation.")
				break
			logging.debug("-- Slave step : {0}".format(Slave.CurrentStep()))
			for MasterStep in Master.IterSteps():
				MasterInCtrls=[]
				SlaveInCtrls=[]
				if not MasterDataSaved: MasterStep.Reset()
				logging.debug("-- Next MasterStep : {0}".format(MasterStep))
				#######################===-ENTERING CONDITIONS-===###################
				EnteringCond=None
				if MasterStep.HasCtrl("OUT"):
					#---Add entering condition---
					MasterInCtrls=MasterStep.GetCtrl("OUT") # MASTER OUT => SLAVE IN
#					for C in MasterInCtrls: C.Value=1
					if len(MasterInCtrls):
						if EnteringCond is None: EnteringCond=Condition()
						EnteringCond.AddANDCond(*MasterInCtrls)
				if Slave.CurrentStep().HasCtrl("OUT"):
					#---Add entering condition---
					SlaveInCtrls=Slave.CurrentStep().GetCtrl("OUT") # MASTER OUT => SLAVE IN
#					for C in SlaveInCtrls: C.Value=1
					if len(SlaveInCtrls):
						if EnteringCond is None: EnteringCond=Condition()
						EnteringCond.AddANDCond(*SlaveInCtrls)
		
				#######################===-DATA ASSIGNMENTS-===###################
				if MasterStep.HasData("OUT"):
					#----------------------------
					if Master.HasRegToBeRead():
						for Data in MasterStep.GetData("OUT"):
							Reg=Master.PopRegToBeRead()
							logging.debug("Assign register '{0} 'to '{1}'".format(Reg.Sig, Data.Sig))
							A=Master.AssignRegister(Data, RegAssignment=Reg)
							if A: 
								AdapterFSM.AddAssignment(A) 
#								for Sig in A.GetAssignedSignals():
#	#								RegSig=A.GetAssignorSignal(Sig)
#									Regs=Master.GetRegisters()
#									if Sig.Name in Regs:
#										ParamSignal=Regs[Sig.Name].Copy()
#										ParamSignal.Name="ResetVal_"+ParamSignal.Name
#										FSMParams[Sig.Name]=ParamSignal
#										RA=AssignmentStatement(Assignee=Sig, Assignor=ParamSignal, Cond=None, Desc="Reset interface register value")
#										AdapterFSM.AddResetAssignment(RA)
							else:
								logging.error("Unable to assign master interface input register (with Data '{0}')".format(Data))
					#----------------------------
					elif Slave.CurrentStep().HasData("IN") and Slave.HasRegToBeWritten():
						# We must save input data from master until registers from slave are filled.
						for Data in MasterStep.GetData("OUT"):
							DataName=Data.GetName()
							if MasterDataSaved: continue
							Reg=Data.Copy()
							Reg.SetName(DataName+"_TEMP")
							InternalDict[DataName]=Reg.Sig
							A=Slave.AssignRegister(Data, RegAssignment=Reg)
							if A: 
								AdapterFSM.AddAssignment(A) 
								Reg.Reset()
								MasterStep.AddData(Reg)
								MasterDataSaved=True
						for Data in Slave.CurrentStep().GetData("IN"):
							Reg=Slave.PopRegToBeWritten()
							logging.debug("Assign register '{0} 'to '{1}'".format(Reg.Sig, Data.Sig))
							A=Slave.AssignRegister(Data, RegAssignment=Reg)
							if A: 
								AdapterFSM.AddAssignment(A) 
#								for Sig in A.GetAssignedSignals():
#	#								RegSig=A.GetAssignorSignal(Sig)
#									Regs=Slave.GetRegisters()
#									if Sig.Name in Regs:
#										ParamSignal=Regs[Sig.Name].Copy()
#										ParamSignal.Name="ResetVal_"+ParamSignal.Name
#										FSMParams[Sig.Name]=ParamSignal
#										RA=AssignmentStatement(Assignee=Sig, Assignor=ParamSignal, Cond=None, Desc="Reset interface register value")
#										AdapterFSM.AddResetAssignment(RA)
							else:
								logging.error("Unable to assign master interface input register (with Data '{0}')".format(Data))
					#----------------------------
					else:
						logging.debug("Assign data.")
						A=Slave.AssignDataFrom(MasterStep, Cond=None)
						AdapterFSM.AddAssignment(A) 
						AdapterFSM.SetTag(Tag="LoopMarker", Anteriority=None) # For Data serialization loop
							
				#######################===-CTRL ASSIGNMENTS-===###################
				if MasterStep.HasCtrl("IN"):
					MasterOutCtrls+=[x.GetName() for x in MasterStep.GetCtrl("IN")]
				if Master.IsLastStep(MasterStep) and not Slave.HasDataToBeWritten():
					if Slave.CurrentStep().HasCtrl("IN"):
						SlaveOutCtrls+=[x.GetName() for x in Slave.CurrentStep().GetCtrl("IN")]
					
				for C in AssignedCtrlList:
					CtrlName=C.GetName()
					if CtrlName in MasterOutCtrls: 
						SyncCond=MasterStep.GetSyncCtrl(CtrlName=CtrlName)
						CtrlAssignments=AssignmentStatement()
						CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=1, Cond=SyncCond, Desc="")
						if SyncCond:
							CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc="")
						AdapterFSM.AddAssignment(CtrlAssignments, OnTransition=False)
					elif CtrlName in SlaveOutCtrls: 
#						SyncCond=Condition()
#						SyncCond.AddANDCond(*(SlaveInCtrls+MasterInCtrls))
						SyncCond=Slave.CurrentStep().GetSyncCtrl(CtrlName=CtrlName)
						CtrlAssignments=AssignmentStatement()
						CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=1, Cond=SyncCond, Desc="")
						if SyncCond:
							CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc="")
						AdapterFSM.AddAssignment(CtrlAssignments, OnTransition=False)
					else: #---Assign 0 to other ctrl signals---
						AdapterFSM.AddAssignment(AssignmentStatement(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc=""), OnTransition=False)
				MasterOutCtrls=[]
				SlaveOutCtrls=[]	
				########################===-STATE CREATION-===####################
				if Master.IsLastStep(MasterStep) and (not Slave.HasDataToBeWritten()) and (not Master.HasDataToBeRead()): break
				else:
					if EnteringCond is None: 
						#----------------------------
						CurrentState=AdapterFSM.AddState() # inconditional change
						#----------------------------
					else:
						#----------------------------
						CurrentState=AdapterFSM.AddState(Cond=EnteringCond) # Conditional change
						#----------------------------
					CurrentState.AddInputCtrl(SlaveInCtrls+MasterInCtrls)
		
			#------------------------------------
			if Master.HasDataToBeRead():
				Slave.CurrentStep().Reset()
				Slave.Next(Loop=True)
				
		#---Finish up slave steps---
		while not Slave.IsLastStep(Slave.CurrentStep()):
			Slave.CurrentStep().Reset()
			Slave.Next(Loop=True)
			#######################===-ENTERING CONDITIONS-===###################
			if Slave.CurrentStep().HasCtrl("OUT"):
				#---Add entering condition---
				SlaveInCtrls=Slave.CurrentStep().GetCtrl("OUT") # MASTER OUT => SLAVE IN
#				for C in SlaveInCtrls: C.Value=1
				if len(SlaveInCtrls):
					EnteringCond=Condition()
					EnteringCond.AddANDCond(*SlaveInCtrls)
			#######################===-CTRL ASSIGNMENTS-===###################
			if Slave.CurrentStep().HasCtrl("IN"):
				SlaveOutCtrls=[x.GetName() for x in Slave.CurrentStep().GetCtrl("IN")]
			#---Assign 0 to other ctrl signals---
			for C in AssignedCtrlList:
				if C.GetName() in SlaveOutCtrls+MasterOutCtrls: 
					AdapterFSM.AddAssignment(AssignmentStatement(Assignee=C.HDLFormat(), Assignor=1, Cond=None, Desc=""), OnTransition=False)
				else:
					AdapterFSM.AddAssignment(AssignmentStatement(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc=""), OnTransition=False)
			MasterOutCtrls=[]
			SlaveOutCtrls=[]
			
				
		# Close FSM loop and create a mini loop if a serialization factor > 1  
		AdapterFSM.CloseLoop(EnteringCond, Serialization=Master.GetSerializationFactor(), LoopStep=AdapterFSM.GetStepByTag("LoopMarker")) # Use last entering condition
		return AdapterFSM, FSMParams, InternalDict
	#----------------------------------------------------------------------
	def GenerateAdapterFSM(self, Name, Master, Slave):
		"""
		Generate FSM for a Master/slave adaptation.
		Assumptions:
			- Master has no serialization factor
			- Slave has only one step
			- Master has only one data signal
		"""
		AdapterFSM=FSM("{0}_FSM".format(Name))
		
		FSMParams, InternalDict = Master.MapAsFSM(AdapterFSM, Slave)
		
		return AdapterFSM, FSMParams, InternalDict
	#---------------------------------------------------------------
	def GenSrc(self, Synthesizable=True, OutputDir="./Output", IsTop=True, HwConstraints=None, ProcessedServ={}):
		"""
		Generate source files or copy sources to output directory.
		Return True if success.
		"""
		if self.IsOrthogonal(): return []
#		if not os.path.isdir(OutputDir): os.makedirs(OutputDir)
		Mod = self.GetModule(Constraints=HwConstraints)
		if Mod is None:
			logging.error("[Service '{0}'] No module implementation for this service.".format(self))
			return []
		else: 
			if self.Name in ProcessedServ:
				S=ProcessedServ[self.Name]
			else:
				S=None
			return Mod.GenSrc(Synthesizable=Synthesizable, OutputDir=OutputDir, IsTop=IsTop, HwConstraints=HwConstraints, ProcessedServ=ProcessedServ, ModInstance=S)
	#---------------------------------------------------------------
	def IsOrthogonal(self):
		"""
		return True if service is of type 'orthogonal' else False.
		"""
		return self.Type=="orthogonal"
	#---------------------------------------------------------------
	def CollectPkg(self):
		"""
		Update package dictionary with children package.
		"""
		for Child in [self.GetModule(),]: # self.Params.values()+self.Ports.values()+
			if not (Child is None): 
				Child.CollectPkg()
				PackageBuilder.CollectPkg(self, Child)
				self.PkgVars.update(Child.Vars.copy())
				
#		self.Params  = {} # Dictionary of service parameters
#		self.Vars    = {}
#		self.Ports   = {} # Dictionary of service ports interface
		
		PortNames=list(self.Ports.keys())
		ParamNames=list(self.Ports.keys())
		
		for S in list(self.Ports.values()):
			self.Package["TypeImport"].update(S.GetUsedTypes())
		for S in list(self.Params.values()):
			self.Package["TypeImport"].update(S.GetUsedTypes())
			
			
#		for Const in self.Package["Constants"].keys():
#			if self.Params.keys().count(Const):
#				self.Package["Constants"][Const]=self.Params[Const].HDLFormat(self.Vars.copy())
	#---------------------------------------------------------------
	def SetParam(self, Param, Value):
		"""
		Change a parameter value.
		"""
		if Param in self.Params:
			self.Params[Param].Default = Value
			self.Params[Param].SetValue(Value)
			return True
		else:
			return False
	#---------------------------------------------------------------
	def __repr__(self):
		"""
		Print service parameters to stdout.
		"""
		return """
		SERVICE: name='{0}', Type='{1}', Version='{2}'
		* Parameters = {3}
		* Ports      = {4}
		* Modules that implements it = {5}
		""".format(self.Name, self.Type, self.Version, list(self.Params.keys()), list(self.Ports.keys()), [x.Name for x in self.ModList])
	#---------------------------------------------------------------
	def Display(self):
		print(repr(self))
	#---------------------------------------------------------------
	def __str__(self):
		return '{0}({1})[v{2}]'.format(self.Name, self.Type, self.Version)
		
#======================================================================
#def GetInitiator(Protocol1, Protocol2):
#	"""
#	Return Protocol initiator
#	Priority to Protocol1
#	"""
#	Protocol1.SetDirection(Direction="IN")
#	Protocol2.SetDirection(Direction="IN")
#	CurStep1=Protocol1.CurrentStep()
#	CurStep2=Protocol2.CurrentStep()
#	if CurStep1 is None: 
#		Protocol1.SetDirection(Direction="INOUT")
#		CurStep1=Protocol1.CurrentStep()
#	if CurStep2 is None: 
#		Protocol2.SetDirection(Direction="INOUT")
#		CurStep2=Protocol2.CurrentStep()
#	if CurStep1 is None:
#		if CurStep2 is None:
#			return None, None
#		else:
#			return Protocol2, Protocol1
#	else:
#		if CurStep2 is None:
#			return Protocol1, Protocol2
#		else:
#			if len(CurStep1.GetOutputs())==0: return Protocol2, Protocol1
#			else: return Protocol1, Protocol2

#======================================================================
#def ResetOutputSignals(AdapterFSM, Interfaces):
#	"""
#	RESET OUTPUT SIGNALS
#	"""
#	for I in Interfaces:
#		for S in I.Signals:
#			if S.Direction=="OUT":
#				S_HDL=S.HDLFormat()
#				AdapterFSM.InitState().AddAssignment([(None, [(S_HDL,None),])])
#	return 
	
		
#======================================================================
#def NewFSMState(AdapterFSM, LastState, MasterCurStep, SlaveCurStep, SetSlaveEC=True):
#	"""
#	Create a new state with proper entering conditions and control assignments.
#	"""
#	#------------------Set step entering condition----------------------
#	if SetSlaveEC:
#		ECond=SlaveCurStep.EnteringConditions()+MasterCurStep.EnteringConditions()
#		# TODO:
##		ECond.AddSyncAssignments(MasterCurStep.GetData(Direction="OUT"), SlaveCurStep.GetData(Direction="OUT"))
#	else:
#		ECond=MasterCurStep.EnteringConditions()
#	#-----------------Set a state for this Step--------------------------
#	NewState=AdapterFSM.AddState(Previous=LastState, Cond=ECond, Name=MasterCurStep.GetStateName(SlaveCurStep))
##	logging.info("New step : {0} [{1}] | [{2}]".format(NewState, map(lambda x: x.Name, MasterCurStep.GetCtrl()), map(lambda x: x.Name, MasterCurStep.GetData())))
#	LastState=NewState
#	#----------Don't forget to assign output control signals----------
#	for C in MasterCurStep.GetCtrl(Direction="OUT")+SlaveCurStep.GetCtrl(Direction="OUT"):
#		C_HDL=C.HDLFormat()
#		C_HDL.Value=1
#		NewState.AddAssignment([(None, [(C_HDL, C_HDL.Value),]),])
#	return NewState
#======================================================================
def Rearrange(Master, Slave):
	"""
	Meld master and slave protocols.
	"""
	HasSync=False
	for CName, C in Slave.CtrlDict.items():
		if C.Direction=="OUT": HasSync=True
	if HasSync:
		NewMaster = Master.Copy()
		NewSlave  = Slave.Copy()
		for Step in NewSlave.IterSteps():
			NewStep=Step.Copy()
			NewStep.RemoveData()
			NewMaster._Steps.append(NewStep)
			Step.RemoveCtrl()
		
		return NewMaster, NewSlave
	else:
		return Master, Slave



