#!/usr/bin/python


import os, sys, datetime, logging, shutil

from lxml import etree

from HdlLib.SysGen.PackageBuilder import PackageBuilder
from HdlLib.SysGen import LibEditor
from HdlLib.SysGen import HDLEditor as HDL
from HdlLib.SysGen.Signal import Signal
from HdlLib.SysGen.Condition import Condition
from HdlLib.SysGen.Protocol import DirectedProtocol
from HdlLib.Utilities.Misc import SyntheSysError

#=======================================================================
class Interface():
	"""
	Interface object for XML service Interface abstraction.
	"""
	#---------------------------------------------------------------
	def __init__(self, Service, XMLElmt=None, Infos={}):
		"""
		Gather Interface parameters.
		"""
#		PackageBuilder.__init__(self)
#		print("NEW INTERFACE (serv {0})".format(Service.Name))
		self.Name      = ""
		self.Size      = 1 # Number of possible connections for this interface
		self.Direction = "INOUT"
		self.Service   = Service
		self.Signals   = []
		self.DataList  = []
		self.DataDict  = {}
		self.CtrlList  = []
		self.Mapping   = {}
		self.CurIndex  = None
		self.Protocol  = None
		self.XMLElmt   = XMLElmt
		self.ParamVars = {}
		self.Registers = {}
		self.Protocol  = None
		self.Tags      = {}
		for SName, S in Service.Params.items():
			self.ParamVars.update(S.GetUsedParam())
		if not XMLElmt is None:
#			print("\t=>SetFromXML")
			if not self.SetFromXML(XMLElmt): 
				logging.error("[Interface.__init__:serv({0})] Unable to parse interface XML content.".format(Service))
				sys.exit(1)
			
		else:
#			print("\t=>FromINFO")
			self.Name      = Infos["Name"]
			self.Size      = Infos["Size"] # Number of possible connections for this interface
			self.Direction = Infos["Direction"]
			self.DataList  = Infos["DataList"]
			self.DataDict  = {}
			self.DataWidth = Infos["DataWidth"] if "DataWidth" in Infos else None
			for D in self.DataList:
				self.DataDict[D.Name]=D 
			self.CtrlList  = Infos["CtrlList"]
			self.Mapping   = Infos["Mapping"]
			self.Protocol  = Infos["Protocol"]
			self.Registers = Infos["Registers"]
			self.Tags      = Infos["Tags"]
			self.Signals   = self.DataList+self.CtrlList
			for S in self.Signals:
				self.ParamVars.update(S.GetUsedParam())
			self.XMLElmt   = self.GetXMLElmt()
			self.SerializationFactors={D.Name:1 for D in self.DataList if D.Direction=="IN"}
		self.SignalDict  = {}
		for S in self.Signals:
			self.SignalDict[S.Name]=S
		
		try: int(eval(str(self.Size), self.ParamVars))
		except: 
			logging.error("Variables used in size ('{0}') of interface '{1}' not previously defined.".format(self.Size, self.Name))
			exit(1)
	#---------------------------------------------------------------
	def GetSize(self, Eval=True):
		"""
		Evaluate and return size of interface.
		"""
		if self.Size is None: Size=1
		else:
			if Eval is True: Size=int(eval(self.Size, self.ParamVars))
			else: Size=self.Size
		return Size
	#---------------------------------------------------------------
	def SetProtocol(self, P):
		"""
		Set P as Interface protocol. P must be a DirectedProtocol.
		"""
#		print("P:{0}".format(P))
		if not isinstance(P, DirectedProtocol):
			logging.warning("[SetProtocol] Specified protocol is not a 'DirectedProtocol' object (Type:{0}).".format(type(P)))
		self.Protocol=P
		return True
	#---------------------------------------------------------------
	def GetProtocol(self):
		"""
		return Protocol associated with this interface.
		"""
		return self.Protocol
	#---------------------------------------------------------------
	def UpdateXML(self):
		"""
		Return XML representation of attributes.
		"""
		self.XMLElmt=LibEditor.InterfaceXml(self)
	#---------------------------------------------------------------
	def SetFromXML(self, XMLElmt):
		"""
		Parse XML content and extract interface information.
		"""
		if XMLElmt.tag!="interface":
			logging.error("[Service {0}] XML content do not describe an interface.".format(self.Service.Name)) 
			sys.exit(1)
			return False
			
		self.Name      = str(XMLElmt.attrib.get("name"))
		self.Size      = XMLElmt.attrib.get("number") # Number of possible connections for this interface
		self.Direction = str(XMLElmt.attrib.get("direction").strip().upper())
		self.DataWidth = None
		self.DataList  = []
		self.DataDict  = {}
		self.CtrlList  = []
		self.Mapping   = {}
		self.CurIndex  = None
		self.Protocol  = None
		self.Sequences = {}
		self.SerializationFactors={}
		self.Tags={}
		
		for CtrlElmt in XMLElmt.iterchildren("datawidth"):
			Attr = CtrlElmt.attrib
			# Get Signal with specified name
			N=Attr.get("name")
			if not N in self.Service.Params:
				logging.error("[{0}] Attribute '{1}' in interface doesn't correspond to a service parameter.".format(self, "datawidth"))
				return False
			else:	
				self.DataWidth=N
				break

		for CtrlElmt in XMLElmt.iterchildren("control"):
			Attr = CtrlElmt.attrib
			# Get Signal with specified name
			N=Attr.get("name")
			if not N in self.Service.Ports:
				logging.error("[{0}] Ctrl '{1}' in interface doesn't correspond to a service port.".format(self, N))
				print("Available ports:", self.Service.Ports)
				return False
			else:	
				self.AddSignal(Signal=self.Service.Ports[N], Target=Attr.get("target"), Ctrl=True)
				
		for DataElmt in XMLElmt.iterchildren("data"):
			Attr = DataElmt.attrib
			# Get Signal with specified name
			N=Attr.get("name")
			self.Registers[N]=[]
			self.SerializationFactors[N]=Attr.get("serialization")
			if not N in self.Service.Ports:
				logging.error("[{0}] Data '{1}' in interface doesn't correspond to a service port.".format(self, N))
				print("Available ports:", self.Service.Ports)
#				raise TypeError
				return False
				continue
			else:	
				Sig=self.Service.Ports[N]
				self.AddSignal(Signal=Sig, Target=Attr.get("target"), Ctrl=False)
			for SetsElmt in DataElmt.iterchildren("sets"):
				Attr = SetsElmt.attrib
				RegName=Attr.get("register")
				Position=Attr.get("position")
				try: P=int(Position)
				except:
					logging.error("[{0}] attribute 'position' of sets child of data element '{1}' not an integer representation: skipped.".format(repr(self), N))	
					continue
				Value=Attr.get("value")
				RegSig=Sig.Copy()
				RegSig.Name=RegName
				RegDict={
					"Data"      : N, 
					"Position"  : P, 
					"Name"      : RegName,
					"Value"     : Value,
					"Signal"    : RegSig.Divide(self.Size) if self.GetSize()>1 else RegSig,
					"Direction" : self.Direction,
					"TagsOrder" : []
					}
				Tags={}
				for TagElmt in SetsElmt.iterchildren("tag"):
					Attr = TagElmt.attrib
					Slice=Attr.get("slice")
					TagName=Attr.get("name")
					if Slice is None:
						Tags[TagName]=RegSig
					else:
						Left, Right=Slice.split(':')
						Tags[TagName]=RegSig[Left:Right]
					RegDict["TagsOrder"].append(TagName)
				RegDict["Tags"]=Tags
				self.Tags.update(Tags)
				self.Registers[N].append(RegDict)
							
		self.Protocol=DirectedProtocol(Interface=self, Name=self.Name+"_"+self.Direction+"_Protocol")
		try: self.Protocol.SetFromXML(XMLElements=list(XMLElmt.iterchildren("protocol")))
		except: 
			Msg="Interface '{0}' parsing failure.".format(self.Name)
			logging.error(Msg)
			raise SyntheSysError(Msg)
		
#		if not (self.SerializationFactor is None) : self.Protocol.SetSerializationFactor(self.SerializationFactor)
		
		self.Signals = self.DataList+self.CtrlList
		self.DataDict  = {}
		for D in self.DataList:
			self.DataDict[D.Name]=D 
		
		return True
	#---------------------------------------------------------------
	def AddSignal(self, Signal, Target=None, Ctrl=True):
		"""
		Add data or control signal to interface.
		"""
		if Ctrl is True: self.CtrlList.append(Signal)
		else: self.DataList.append(Signal)
		if Target: self.Mapping[Signal.GetName()]=Target
		self.ParamVars.update(Signal.GetUsedParam())
	#---------------------------------------------------------------
	def GetUsedParam(self, GetSignals=False):
		"""
		Return the dictionary of USED parameters.
		"""
		UsedParams={}
		for D in self.GetSignals(Ctrl=True, Data=True, Directions=["IN", 'OUT']):
			UsedParams.update(D.GetUsedParam())
		if GetSignals:
			UsedSigParams={}
			for N,V in UsedParams.items():
				UsedSigParams[N]=self.Service.Params[N]
			return UsedSigParams
		else:
			return UsedParams
	#---------------------------------------------------------------
	def UpdateAllValues(self, ValueDict):
		"""
		Change values of each port/params and their respective "usedparam" dictionary.
		"""
		for D in self.GetSignals(Ctrl=True, Data=True, Directions=["IN", 'OUT']):
			D.UpdateAllValues(ValueDict)
	#---------------------------------------------------------------
	def GetDataDict(self):
		"""
		return Data dictionary.
		"""
		return self.DataDict
	#---------------------------------------------------------------
	def GetRegisterDict(self):
		"""
		return Data dictionary.
		"""
		return self.Registers
	#---------------------------------------------------------------
	def GetXMLElmt(self):
		"""
		return XML representation of interface.
		"""
		ItfElmt = etree.Element( "interface", 
				     name       = self.Name, 
				     direction  = self.Direction, 
				     number     = str(self.Size))
		for C in self.CtrlList:
			CtrlElmt=etree.SubElement( ItfElmt, "control",  
					         name   = C.Name,
					         target = self.Mapping[C.Name] if C.Name in self.Mapping else C.Name, 
					         )
		for C in self.DataList:
			DataElmt=etree.SubElement( ItfElmt, "data",  
					         name   = C.Name,
					         target = self.Mapping[C.Name] if C.Name in self.Mapping else C.Name, 
					         )
			if C.Name in self.Registers:
				for RDict in self.Registers[C.Name]:
					Position=str(RDict["Position"])
					Register=RDict["Name"] 
					Value=str(RDict["Value"])
					if Value is None:
						RegElmt=etree.SubElement( DataElmt, "sets",  
									 register   = Register,
									 position   = Position,
									 )
					else:
						RegElmt=etree.SubElement( DataElmt, "sets",  
									 register   = Register,
									 position   = Position,
									 value      = Value
									 )
		if not (self.Protocol is None):
			self.Protocol.AddXMLElmtTo(ItfElmt)	
		
		return ItfElmt
	#---------------------------------------------------------------
	def Copy(self):
		"""
		Create new Interface and copy parameters.
		"""
		Infos={}
		Infos["Name"]=self.Name
		Infos["Size"]=self.Size # Number of possible connections for this interface
		Infos["Direction"]=self.Direction
		Infos["DataList"]=self.DataList
		Infos["CtrlList"]=self.CtrlList
		Infos["Mapping"]=self.Mapping
		Infos["Protocol"]=self.Protocol
		Infos["Registers"]=self.Registers
		Infos["Tags"]=self.Tags
		I=Interface(Service=self.Service, XMLElmt=None, Infos=Infos)
		I.CurIndex=self.CurIndex
		return I
	#---------------------------------------------------------------
	def GetRegister(self, RegName):
		"""
		Return Register signal corresponding to RegName.
		"""
		for Data, RegList in self.Registers.items():
			for RegInfo in RegList:
				if RegInfo["Name"]==RegName:
					Reg=RegInfo["Signal"]
					Reg.SetValue(RegInfo["Value"])
					return Reg
		return None
	#---------------------------------------------------------------
	def IsCompatibleWith(self, ITF):
		"""
		Return true if each signal of ITF has a counterpart in current interface.
		Else return False.
		"""
		if self.Direction==ITF.Direction:
			logging.debug("Interface '{0}' has same direction as '{1}'.".format(ITF, self)) 
			return False
		elif ITF.Name!=self.Name:
			logging.debug("Interface '{0}' has and '{1}' has different names.".format(ITF, self)) 
			return False
		# Check mapping signals presence
		ITFPorts = [x.Name for x in ITF.Signals]
		for Sig in list(self.Mapping.values()):
			if not ITFPorts.count(Sig): 
				logging.debug("'{0}' target '{1}' missing from '{2}'.".format(self, Sig, ITF))
				return False
			
		return True
	#---------------------------------------------------------------
	def SetupRegisters(self, Signal, Register, Value):
		"""
		Set internal dictionary for specified sequence of values.
		"""
		SignalName=str(Signal)
		if not SignalName in self.Registers:
			logging.error("[SetupRegisters:{0}] No such signal '{1}' found (Available:{1}): ignored.".formats(self, SignalName, list(self.Registers.keys())))
			return False
		for RegDict in self.Registers[SignalName]:
			if RegDict["Name"]==Register:
				logging.debug("Set Register '{0}' to value '{1}'".format(Register, Value))
				if not "Position" in RegDict: RegDict["Position"]=len(self.Registers[SignalName])
				RegDict["Value"]=Value
				RegDict["Signal"].SetValue(Value)
				return True
		RegSig=Signal.Copy()
		RegSig.Name=Register
		RegSig.SetValue(Value)
		self.Registers[SignalName].append({
					"Data"      : Signal, 
					"Position"  : len(self.Registers[SignalName]), 
					"Name"      : Register,
					"Value"     : Value,
					"Signal"    : RegSig,
					"Direction" : self.Direction})
		return True
	#---------------------------------------------------------------
	def Connect(self, ITF, XMLReqServ=None, Ref=False, KeepNames=False):
		"""
		Add map child for interfaces signals connections.
		ITF must be compatible (see IsCompatibleWith(self, ITF)).
		If Ref==True, do not connect to ITF but local signals.
		"""
		# First set index for signals name ---------------------------------
		if self.CurIndex!=None: FormalIDX=":{0}".format(self.CurIndex)
		else: FormalIDX=""
		
		IntSignalCreated = []
		Mapping = {}
		if Ref: # If its the reference interface (internal signal will be named with its own service-name prefix)
			# Map signals for a service ------------------------------------
			for Sig in self.Signals:
				if self.CurIndex!=None: LocalIndex=":"+str(self.CurIndex) # For type custom array
				else: LocalIndex=""
				IntSignal = '.'.join([self.Service.Alias, str(Sig.Name)+LocalIndex])
				if XMLReqServ: MAP = etree.SubElement(XMLReqServ, "map", formal=Sig.Name+FormalIDX, actual=IntSignal)
				Mapping[str(Sig)+LocalIndex]=([[self.Service.Alias, str(Sig.Name), self.CurIndex],], True, {})
				S=Sig.Copy()
				S.Name=IntSignal
				IntSignalCreated.append(S)
			return Mapping, IntSignalCreated
		else:
			# Setup Actual index
			if self.CurIndex!=None: FormalIDX=":{0}".format(self.CurIndex)
			else: FormalIDX=""
			# Map signals for a service ------------------------------------
			for Sig in self.Signals:
				ActualName=self.Mapping[Sig.Name] if KeepNames is False else Sig.Name
				IntSignal = '.'.join([ITF.Service.Alias, ActualName])
				if XMLReqServ: MAP = etree.SubElement(XMLReqServ, "map", formal=Sig.Name+FormalIDX, actual='.'.join([ITF.Service.Alias, ActualName]))
				Mapping[str(Sig)+FormalIDX]=([[ITF.Service.Alias, ActualName, ITF.CurIndex],], True, {})#[(ITF.Service.Alias, ActualName)]
				
				S=Sig.Copy()
				S.Name=IntSignal
				IntSignalCreated.append(S)
			return Mapping, IntSignalCreated
	#---------------------------------------------------------------
	def Complement(self, Service=None):
		"""
		Return an interface object with complementary signals.
		"""
		# Inverse Mapping dictionnary
		Mapping={}
		for k,v in self.Mapping.items():
			Mapping[v]=k
		# Generate Interface object
		Infos={}
		Infos["Name"]=self.Name
		Infos["Size"]=self.Size # Number of possible connections for this interface
		
		Infos["Direction"]=[]
		if "IN"==self.Direction:
			Infos["Direction"]="OUT"
		elif "OUT"==self.Direction:
			Infos["Direction"]="IN"
		else:
			Infos["Direction"]=self.Direction
				
		Infos["DataList"] = []
		for S in self.DataList:
			NewS = S.Copy()
			NewS.Name=self.Mapping[S.Name] if S.Name in self.Mapping else S.Name
			NewS.Direction="OUT" if S.Direction=="IN" else "IN"
			Infos["DataList"].append(NewS)
			
		Infos["CtrlList"] = []
		for S in self.CtrlList:
			NewS = S.Copy()
			NewS.Name=self.Mapping[S.Name] if S.Name in self.Mapping else S.Name
			NewS.Direction="OUT" if S.Direction=="IN" else "IN"
			Infos["CtrlList"].append(NewS)
		Infos["Mapping"]=Mapping
		Infos["Protocol"]=None
		
		SigDict={}
		for S in self.Signals:
			SigDict[S.Name]=S 
			
		Infos["Registers"]=self.Registers.copy()
		Infos["Tags"]=self.Tags.copy()
		
		if Service is None:Service=self.Service
		I=Interface(Service=Service, XMLElmt=None, Infos=Infos)
		
		CompProto=self.Protocol.Complement(Interface=I)
		Infos["Protocol"]=CompProto
		I.SetProtocol(CompProto)
		
		I.CurIndex=self.CurIndex
#		I.XMLElmt = XMLElmt # TODO
		I.UpdateXML()
		return I
	#----------------------------------------------------------------------
	def GetElmt(self):
		"""
		Copy interface with a size of 1 => all signals are sliced.
		"""
		Size=self.GetSize(Eval=True)
		if Size>1:
			DataList=[x.Divide(self.Size) for x in self.DataList]
			CtrlList=[x.Divide(self.Size) for x in self.CtrlList]
			Infos={}
			Infos["Name"]      = self.Name
			Infos["Size"]      = 1 # Number of possible connections for this interface
			Infos["Direction"] = self.Direction
			Infos["DataList"]  = DataList
			Infos["CtrlList"]  = CtrlList
			Infos["Mapping"]   = self.Mapping
			Infos["Protocol"]  = self.Protocol.GetElmt()
			Registers={}
			for DataName, RegDictList in self.Registers.items():
				NewRegDictList=[]
				for RegDict in RegDictList:
					NewDict=RegDict.copy()
					S=RegDict["Signal"]
#					print("S:", repr(S))
					NewDict["Signal"] = S.Copy().Divide(self.Size)
					NewRegDictList.append(NewDict)
				Registers[DataName]=NewRegDictList
			Infos["Registers"] = Registers
			Infos["Tags"]      = self.Tags.copy()
			for TagName in tuple(self.Tags.keys()):
				Infos["Tags"][TagName]=self.Tags[TagName].Divide(self.Size)
				Infos["Tags"][TagName].SetIndex(self.Tags[TagName].GetIndex())
			I=Interface(self.Service, XMLElmt=None, Infos=Infos)
			return I
		else:
			return self
	#----------------------------------------------------------------------
	def GetSignals(self, Ctrl=True, Data=True, Directions=["IN", 'OUT']):
		"""
		return list of signal according to arguments.
		"""
		Sigs=[]
		if Data==True: Sigs+=[x for x in self.DataList if x.Direction in Directions]
		if Ctrl==True: Sigs+=[x for x in self.CtrlList if x.Direction in Directions]
		
		if self.CurIndex is None:
			return Sigs
		else:
			return [x.Divide(self.Size) for x in Sigs]
	#---------------------------------------------------------------
	def GenStim(self, TBValues, **ParamDict):
		"""
		Return sequence of stimuli values corresponding to interface stimuli names.
		"""
					#-------------------------------------------------
					# Add header and payload to data to be sent
					#-------------------------------------------------
#					FlitWidth=self.ChildLists["NoC"][0].Parameters["Common"]["FlitWidth"]
#					TargetHeader=GenHeader(TargetPosition=Coordinates, FlitWidth=FlitWidth)
#					TargetPayload=len(TaskValues)
#					
#					TaskValues.insert(0, TargetPayload)
#					TaskValues.insert(0, TargetHeader)
#		for P in self.Signals:
#			print(P.GetName(), "'s value:", P.GetValue())
#			for Param, ParamVal in P.GetUsedParam().items():
#				print(Param, "'s value:", ParamVal)
		if self.Protocol.NbSteps()==0:
			logging.error("[GenStim:{0}] No steps in output protocol '{1}'. Stim generation aborted.".format(self, self.Protocol))
		else:
			ItfOutputCtrl=[C.Name for C in self.CtrlList if C.Direction=="IN"]
			ReverseMapping=dict( (v,k) for k,v in self.Mapping.items() )
			# Build a dictionary for the list of registers by data.------
			RegByData={}
			for DataName, RegDictList in self.Registers.items():
				RegByData[DataName]=[]
				for RegDict in RegDictList:
					RegByData[DataName].append(RegDict.copy())
			# -----------------------------------------------------------
			Stimuli={}
			Values={}
			i=0
			while len(TBValues)>0:
				i+=1
				Serialization=1
				for ProtoStep in self.Protocol.IterSteps():
					Comment=ProtoStep.Label
					StepOutCtrls=[]
					#----------------------------
					if ProtoStep.HasData("IN"):
						#----------------------------
						for Data in ProtoStep.GetData("IN"):
							DataName=Data.Sig.Name
							if DataName in RegByData: # Assign first the registers
								if len(RegByData[DataName])>0:
									RegDict=RegByData[DataName].pop(0)
									Reg=RegDict["Signal"].HDLFormat()
									# Test for register tags
									TagAssignment=False
									TagList=[]
									for TagName in RegDict["TagsOrder"]:
										if not (TagName in ParamDict):
											TagAssignment=False 
											break
										else: 
											TagAssignment=True
											Tag=RegDict["Tags"][TagName].HDLFormat()
											Tag.SetValue(ParamDict[TagName])
											TagList.append(Tag)
									if TagAssignment is True:
										ConcatSig=HDL.Signal(TagList, Vars=self.GetUsedParam())
										Stimuli[DataName]=int(Reg.GetValue(Val=ConcatSig, WriteBits=True, Vars=self.GetUsedParam()).replace('"', ''), 2)
										continue
									# Test for register as parameter
									RegName=RegDict["Name"]
									if RegName in ParamDict:
										Stimuli[DataName]=int(Reg.GetValue(Val=ParamDict[RegName], WriteBits=True).replace('"', ''), 2)
										continue
									# Default is register default value
									Reg=RegDict["Signal"].HDLFormat()
									Stimuli[DataName]=int(Reg.GetValue(Val=RegDict["Value"], WriteBits=True).replace('"', ''), 2)
									continue
									
							# Then Data follows registers
							Val=TBValues.pop(0)
							Stimuli[DataName]=Val
							if isinstance(Val, list) or isinstance(Val, tuple):
								Serialization=max(Serialization, len(Val))
					#----------------------------
					if ProtoStep.HasCtrl("IN"):
						for C in ProtoStep.GetCtrl("IN"):
							CName=C.Name#ReverseMapping[C.Name]
							if Serialization>1:
								Stimuli[CName]=['1' for i in range(Serialization)]
							else:
								Stimuli[CName]="1"
							StepOutCtrls.append(CName)
						#----------------------------
						
						
					#---Assign ctrl other signals---
					for C in ItfOutputCtrl:
						if C in StepOutCtrls: continue
						if Serialization>1:
							Stimuli[C]=['0' for i in range(Serialization)]
						else:
							Stimuli[C]="0"
						
#					print("Serialization:", Serialization)
#					for DataName in Stimuli:
#						print("Stimuli[DataName]:", Stimuli[DataName])
#					input()
#					print("--------")
					#----------------------------
#					if ProtoStep.HasCtrl("IN"):
#						logging.debug("{0} has Ctrl inputs".format(ProtoStep))
#						#---Assign ctrl other signals---
#						for C in self.Protocol.GetAssignedCtrl():
#							Stimuli[C.Name]="0"
						#----------------------------
					ProtoStep.Reset()
					yield Stimuli, Comment
	#----------------------------------------------------------------------
	def __getitem__(self, index):
		"""
		Set Current index value (interface index for multiple interfaces).
		"""
		if isinstance(index, int):
			if int(eval(self.Size, self.ParamVars)) > 1: self.CurIndex = index
			else: self.CurIndex = None
			self.Protocol=self.Protocol[index]
			return self
		elif isinstance(index, slice):
			logging.error("[__getitem__:{0}] Slicing interfaces not supported yet.".format(self))
			return self
		else:
			raise TypeError("index must be int or slice")
	#---------------------------------------------------------------
	def __repr__(self):
		"""
		Return interface full name with its associated service/Ports.
		"""
		if self.CurIndex==None: Idx=""
		else: Idx='['+str(self.CurIndex)+']'
		
		return self.Name+'['+str(self.Service)+']'+Idx+"-"+self.Direction+'DATA{'+','.join([str(x) for x in self.DataList])+'}'+"(Ctrl={0})".format(','.join([str(x) for x in self.CtrlList]))
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return interface name with its associated service.
		"""
		return self.Name+"_"+self.Direction
		
		
		
		
