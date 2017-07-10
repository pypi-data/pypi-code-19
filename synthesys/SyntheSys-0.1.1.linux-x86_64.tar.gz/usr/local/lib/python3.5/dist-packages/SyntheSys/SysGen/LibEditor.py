#!/usr/bin/python

"""
Open a Gtk window enabling to browse the service library.
Icons for library an service must be set when called from another location.
"""
import logging, os, sys
from lxml import etree

from SysGen import Condition
from SysGen import HDLEditor as HDL
from SysGen import Module
		
#=========================================================================
def HDLModule(OutputPath, Mod, Packages, Libraries, Declarations, Content):
	"""
	Create a VHDL file with specified code content.
	"""
	OutputFilePath = os.path.join(OutputPath, Mod.Name+HDL.ExtensionDict["VHDL"])
	with open(OutputFilePath, "w+") as HDLFile:	
		# Write VHDL Header----------------------------------------------
		HDLFile.write(
			HDL.Header(
				Mod.Name, 
				Mod.Title, 
				Mod.Purpose, 
				Mod.Desc, 
				Mod.Issues, 
				Mod.Speed, 
				Mod.Area, 
				Mod.Tool, 
				Mod.Version
				)
			)
		
		# Write Library call---------------------------------------------
		HDLFile.write(HDL.Libraries(Libraries))
		HDLFile.write(HDL.Packages(Packages))
		
		
		UsedParams=set(Mod.GetUsedParam())
		Generics=[x.HDLFormat(Mod.Vars.copy()) for x in [x for x in list(Mod.Params.values()) if x.Name in UsedParams]]
		for G in Generics:
			Mod.Vars.update({G.Name:G.InitVal})
		if Mod.NoOrthoPorts is True:
			Ports=[x.HDLFormat(Mod.Vars.copy()) for x in list(Mod.Ports.values())]
		else:
			Ports=[x.HDLFormat(Mod.Vars.copy()) for x in list(Mod.Ports.values())+list(Mod.OrthoPorts.values())]
		Ports=RemoveDuplicated(Ports)
		
		# Write entity---------------------------------------------------
		HDLFile.write(HDL.Entity(Mod.Name, Generics, Ports, Comments=Mod.Purpose))
		# Write Architecture---------------------------------------------
		HDLFile.write(HDL.Architecture("RTL", Mod.Name, Declarations, Content, Mod.Desc))
			
	return OutputFilePath	
			
#=========================================================================
def NewModule(Infos={}, Params=[], Ports=[], Clocks=[], Resets=[], Sources=[]):
	"""
	Create a module to add to library (and its associated XML).
	return Module object created.
	"""
#	logging.debug("Create module '{0}' XML representation".format(Infos["Name"]))
	M=etree.Element( "module", 
                     name   =Infos["Name"], 
                     version=Infos["Version"], 
                     title  =Infos["Title"], 
                     purpose=Infos["Purpose"], 
                     description=Infos["Desc"], 
                     tool   =Infos["Tool"], 
                     area   =Infos["Area"], 
                     speed  =Infos["Speed"], 
                     issues =Infos["Issues"])
	
#	logging.debug("Parameters: '{0}'".format([P.Name for P in Params]))
	# Add parameters
	for Param in Params:
		etree.SubElement(M, 
				 "parameter", 
				 name=Param.Name, 
				 size=str(Param.GetSize()), 
				 type=Param.Type, 
				 default=str(Param.GetValue())) 
	
	# Add IO
	for Port in Ports:
#		if Port.Name not in Clocks and Port.Name not in Resets:
#			if Port.Type.lower().find("std_logic")!=-1: TYPE="logic"
#			elif Port.Type.lower().find("integer")!=-1: TYPE="numeric"
#			elif Port.Type.lower().find("natural")!=-1: TYPE="numeric"
#			else: TYPE=Port.Type
		if Port.Direction=="IN":
			etree.SubElement(M, 
					  "input", 
					  name=Port.Name, 
					  size=str(Port.Size), 
					  type=Port.Type, 
					  default=str(Port.GetValue())) 
		else:
			etree.SubElement(M, 
					  "output", 
					  name=Port.Name, 
					  size=str(Port.Size), 
					  type=Port.Type, 
					  default=str(Port.GetValue()))
					  
	Services = etree.SubElement(M, "services")
	# Add clock service
	for C in Clocks: 
		Required  = etree.SubElement(Services, "required", name="clock", type="orthogonal", version="1.0", alias="Clk")
		MAP = etree.SubElement(Required, "map", formal="clock", actual=C)
		MAP = etree.SubElement(Required, "map", formal="freq", actual="50")
	# Add reset service
	for R in Resets: 
		Required  = etree.SubElement(Services, "required", name="reset", type="orthogonal", version="1.0", alias="Rst")
		MAP = etree.SubElement(Required, "map", formal="reset", actual=R)
		MAP = etree.SubElement(Required, "map", formal="delay", actual="0")
			
	if len(Sources)>0:
		# Add resources
		etree.SubElement(M, "resources") 
		for Src in Sources:
			# Add source referencing
			Core = etree.SubElement(M, "core") 
			etree.SubElement(Core, "rtl", path=Src) 
	
#	if XMLLIB!=None: return Module.Module(M, FilePath=None)
#	else: return None
#	if Infos["Name"]=="DUT":
#		sys.stdout.write(etree.tostring(M, encoding="UTF-8", pretty_print=True).decode("utf-8"))
#		input()
	return Module.Module(M)
 
#=========================================================================
def ModuleXml(Mod):
	"""
	Generate XML for module provided as Mod.
	"""
	XmlMod=etree.Element( "module", 
                     name   =Mod.Name, 
                     version=Mod.Version, 
                     title  =Mod.Title, 
                     purpose=Mod.Purpose, 
                     description=Mod.Desc, 
                     tool   =Mod.Tool, 
                     area   =Mod.Area, 
                     speed  =Mod.Speed, 
                     issues =Mod.Issues)
	# Add parameters and ports of Module to Service
	for ParamName, Param in Mod.Params.items():
		RefAttr={"default":str(Param.GetValue()), "name":Param.Name, "size":str(Param.GetSize()), "type":Param.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement(XmlMod, "parameter", **AttrDict)
		
	for PortName, Port in Mod.Ports.items():
		RefAttr={"default":str(Port.GetValue()), "name":Port.Name, "size":str(Port.Size), "type":Port.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement(XmlMod, "output" if Port.Direction=="OUT" else "input", **AttrDict) 
	#------------------	
	# Provided services
	ProvServices = etree.SubElement(XmlMod, "services")
	
	for SAlias, SName in Mod.ServAlias.items():
		Mapping=Mod.ProvidedServMap[SName]
		Offered=etree.SubElement(ProvServices, "offered", alias=SName.split('.')[-1], name=SName)
		for Formal, Actual in Mapping.items():
			if isinstance(Actual, list):
				FormatedList=[":".join([x[0], x[1].GetName()]) for x in Actual]
				XMLElmt=etree.SubElement(Offered, "map", formal=Formal, actual='{'+",".join(FormatedList)+'}')
			else:
				XMLElmt=etree.SubElement(Offered, "map", formal=Formal, actual=Actual)

#	print( etree.tostring(XmlMod, encoding="UTF-8", pretty_print=True).decode("utf-8") )
#	input()
	#------------------	
	# Required services	# TODO:  TO UNCOMMENT AND VALIDATE !
#	Services = etree.SubElement(XmlMod, "services")
#	for ID, (Serv, ServMap, IsOrtho, Constraints) in Mod.ReqServ.items():
#		SName, SType, SVersion, UniqueName = ID.split('#')
#		Required  = etree.SubElement(Services, "required", name=SName, type=SType, version=SVersion, alias=UniqueName)
#		for Formal, ActualCond in ServMap.items():
#			Actuals, Condition, Vars = ActualCond
#			if len(Actuals)>1:
#				ActualList=[]
#				for InstName, SigName, AIndex in Actuals:
#					if InstName is None or InstName=="": PairInstSig = [SigName,]
#					else : PairInstSig = [InstName, SigName]
#				
#					ActualName=".".join(PairInstSig)
#					if not (AIndex is None): ActualName+=":{0}".format(AIndex)
#					ActualList.append(ActualName)
#				Actual=",".join(ActualList)
#			else:
#				InstName, SigName, AIndex = Actuals[0]
#				
#				if InstName is None or InstName=="": PairInstSig = [SigName,]
#				else : PairInstSig = [InstName, SigName]
#				
#				ActualName=".".join(PairInstSig)
#				if not (AIndex is None): ActualName+=":{0}".format(AIndex)
#				
#			MAP = etree.SubElement(Required, "map", formal=Formal, actual=Actual)
				
	return XmlMod
	#-------------------------------------------
	def ActualXMLRepr(InstName, SigName, Index):
		"Return XML representation of an actual signal"
		Actual=SigName
		if not ((InstName is None) or (InstName=="")):
			Actual=InstName+'.'+Actual
		if not (Index is None or Index==""):
			Actual=Actual+':'+str(Index)
		return Actual
	#-------------------------------------------
	def AddXMLMapping(PName, Mapping, RequiredXmlElmt):
		"Add XML mapping corresponding to dictionary mapping to an XML element"
		if (PName in Mapping):
			ActualList, ACond, IdxDict = Mapping[PName]
			if len(ActualList)>1:
				ActualNames=[]
				for InstName, SigName, Index in ActualList:
					ActualNames.append(ActualXMLRepr(InstName, SigName, Index)) # InstName, SigName, Index = ActualList[0]
				Actual="{"+",".join(ActualNames)+"}"
			else:
				InstName, SigName, Index = ActualList[0]
				Actual=ActualXMLRepr(InstName, SigName, Index)
			if isinstance(ACond, Condition.Condition): ExtraArg={"when": str(ACond)}
			else: ExtraArg={}
		else:	
			Actual=PName
			ExtraArg={}
		return etree.SubElement(RequiredXmlElmt, "map", formal=PName, actual=Actual, **ExtraArg)
	#-------------------------------------------
	for ID, (Serv, Mapping, IsOrtho, Constraints) in Mod.ReqServ.items():
		if Serv is None:	
			continue
			logging.error("Service not referenced library {0}.".format(ID))
#		M=Serv.GetModule()
#		ResetClockSignals=M.GetResetNames(MappedName=False)+Mod.GetClockNames(MappedName=False)
#		print M, "ResetClockSignals:\n", ResetClockSignals
#		raw_input()
		
		Alias=ID.split('#')[-1]
		XmlRequired=etree.SubElement(Services, "required", name=Serv.Name, type=str(Serv.Type), version=str(Serv.Version), alias=Alias)
		for PName in sorted(Serv.Params.keys()):
			# <map formal="Rx:0"      actual="Router:x:(y+1).Tx:1"      when="y!=DimY-1"/>
			XMLElmt=AddXMLMapping(PName, Mapping=Mapping, RequiredXmlElmt=XmlRequired)
		for PName in sorted(Serv.Ports.keys()):
#			if PName in ResetClockSignals: continue
			# <map formal="Rx:0"      actual="Router:x:(y+1).Tx:1"      when="y!=DimY-1"/>
			XMLElmt=AddXMLMapping(PName, Mapping=Mapping, RequiredXmlElmt=XmlRequired)
	
	# Add resources
	for SrcType in Mod.Sources:
		if len(Mod.Sources[SrcType])>0:
			etree.SubElement(XmlMod, "resources") 
			for Src in Mod.Sources[SrcType]:
				# Add source referencing
				Core = etree.SubElement(XmlMod, "core") 
				XMLElmt=etree.SubElement(Core, SrcType, path=Src) 
				
	return XmlMod
        
#=========================================================================
def ProvidedServiceXml(Mod, Interfaces, Infos, OutputPath=None):
	"""
	Generate XML for service provided by module Mod.
	Dump into OutputPath file if specified.
	"""
	S = etree.Element( "service", 
		             name     = Infos["Name"], 
		             type     = Infos["Type"], 
		             version  = Infos["Version"], 
		             category = Infos["Category"])
	Mapping={}
	# Add parameters and ports of Module to Service
	for ParamName, Param in Mod.Params.items():
		RefAttr={"default":str(Param.GetValue()), "name":Param.Name, "size":str(Param.Size), "type":Param.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement( S, "parameter", **AttrDict)
		Mapping[Param.Name]=Param.Name
		
#	ResetNames=Mod.GetResetNames()
#	ClockNames=Mod.GetClockNames()
#	ImplicitSignals=ResetNames+ClockNames
	for PortName, Port in Mod.Ports.items():
#		if PortName in ImplicitSignals: continue
		RefAttr={"default":str(Port.GetValue()), "name":Port.Name, "size":str(Port.Size), "type":Port.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement( S, "output" if Port.Direction=="OUT" else "input", **AttrDict)  
		Mapping[Port.Name]=Port.Name
		
	ProvidedService=Infos["Name"] # TODO: another way ?
	# Add provided service to module
#	raw_input("######## Mapping:\n{0}".format(Mapping))
	Mod.AddProvServ(SName=Infos["Name"], SAlias=Infos["Name"], mapping=Mapping)
	
	# Add interfaces to service
	for I in Interfaces:
#		XMLElmt=etree.SubElement( S, "interface",  
#			                 name      = I.Name,
#			                 direction = ",".join(I.Dirs), 
#			                 number    = I.Size,
#			                 )
		S.append(I.GetXMLElmt())
		
	import Service
	try: Serv=Service.Service(S)
	except: 
		logging.error("[LibEditor.ProvidedServiceXml] Cannot instanciate service '{0}' from XML element.".format(Infos["Name"]))
		sys.exit(1)
	Mod.IdentifyServices([Serv,])
#	Mod.ProvidedServ[Serv.Name]=Serv
	Serv.ModList.append(Mod)
	Serv.Interfaces = Interfaces
	return Serv
 
#=========================================================================
def ServiceXml(Serv):
	"""
	Generate XML for service provided as Serv.
	"""
	S = etree.Element( "service", 
		             name     = Serv.Name, 
		             type     = Serv.Type,
		             version  = Serv.Version,
		             category = Serv.Category)
		             
	# Add parameters and ports of Module to Service
	for ParamName, Param in Serv.Params.items():
		RefAttr={"default":Param.Default, "name":Param.Name, "size":Param.Size, "type":Param.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement( S, "parameter", **AttrDict)
		
	for PortName, Port in Serv.Ports.items():
		RefAttr={"default":Port.Default, "name":Port.Name, "size":Port.Size, "type":Port.Type}
		AttrDict={}
		for Name, Value in RefAttr.items():
			if Value is None: continue
			else: AttrDict[Name]=str(Value)
		XMLElmt=etree.SubElement( S, "output" if Port.Direction=="OUT" else "input", **AttrDict)  
	
	# Add interfaces to service
	for I in Serv.Interfaces:
		S.append(I.GetXMLElmt())
	return S
        
#=========================================================================
def InterfaceXml(Itf, Mapping={}):
	"""
	Generate XML for service provided in Itf.
	"""
	IElmt = etree.Element( "interface", 
		             name      = Itf.Name, 
		             direction = Itf.Direction,
		             number    = "1")
		             
	# Add Data and Ctrl of Interface
	for D in Itf.DataList:
		if D.Name in Mapping:
			XMLElmt=etree.SubElement(IElmt, "data", name=D.Name, target=Mapping[D.Name])
		elif D.Name in Itf.Mapping:
			XMLElmt=etree.SubElement(IElmt, "data", name=D.Name, target=Itf.Mapping[D.Name])
		else:
			XMLElmt=etree.SubElement(IElmt, "data", name=D.Name, target=D.Name)
		
	for C in Itf.CtrlList:
		if C.Name in Mapping:
			XMLElmt=etree.SubElement(IElmt, "ctrl", name=C.Name, target=Mapping[C.Name])
		elif C.Name in Itf.Mapping:
			XMLElmt=etree.SubElement(IElmt, "ctrl", name=C.Name, target=Itf.Mapping[C.Name])
		else:
			XMLElmt=etree.SubElement(IElmt, "ctrl", name=C.Name, target=C.Name)
	
	# Add protocol
	if Itf.Protocol:
		for S in Itf.Protocol.IterSteps():
			S.AddXMLElmtTo(IElmt)
	else:
		logging.warning("No protocol specified for interface '{0}'".format(Itf))
	return IElmt
	      
#============================================================================
def RemoveDuplicated(SignalList):
	"""
	Build a new list and fill it with a set of unique signals from argument list.
	"""
	SignalSet=[]
	SignalNameSet=[]
	for Sig in SignalList:
		if not SignalNameSet.count(Sig.Name):
			SignalSet.append(Sig)
			SignalNameSet.append(Sig.Name)
	
	return SignalSet

