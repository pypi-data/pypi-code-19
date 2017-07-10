
__all__ = ()

import os, sys, logging, shutil, tempfile, re
import collections
from lxml import etree
import math 

from Utilities import Timer, Misc 
from SysGen import FpgaOperations
from SysGen import LibEditor 
from SysGen.HW import HwConstraints, HwLib
from SysGen.HW.HwResources import HwResources

#=======================================================================
class HwModel():
	#---------------------------------------------------------------
	def __init__(self, Name):
		"""
		Hardware model that gather HW information for FPGA BOARDS.
		"""
		self.Name          = Name
		self.Config        = HwLib.ArchiConfig(self.Name) # Get FPGA board configuration
		self.InterfaceDict = self.Config.GetInterface() # Get FPGA board interface pads		
		self.AvailableRsc  = HwResources(RscDict=self.Config.GetAvailableRsc(), FPGAModel=self) # TODO : get from library
		self.XMLElmt       = None
	#---------------------------------------------------------------
	def IsSupported(self):
		"""
		Return True if config file is found in library, False otherwise.
		"""
		if self.Config.Config is None:
			return False
		else:
			return True
	#---------------------------------------------------------------
	def GetFPGA(self, FullId=True):
		"""
		Return the name of the this board's FPGA.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetFPGA] Config file not loaded")
			return "Unknown"
		return self.Config.GetFPGA(FullId=FullId).upper()
	#---------------------------------------------------------------
	def GetBitStreamExt(self):
		"""
		Return the name of the this board's FPGA flow binary extension.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetBitStreamExt] Config file not loaded")
			return "Unknown"
		return self.Config.GetBitStreamExt()
	#---------------------------------------------------------------
	def GetMapReportExt(self):
		"""
		Return the name of the this board's FPGA flow map report file extension.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetMapReportExt] Config file not loaded")
			return "Unknown"
		return self.Config.GetMapReportExt()
	#---------------------------------------------------------------
	def GetParReportExt(self):
		"""
		Return the name of the this board's FPGA flow PaR report file extension.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetParReportExt] Config file not loaded")
			return "Unknown"
		return self.Config.GetParReportExt()
	#---------------------------------------------------------------
	def GetInterface(self):
		"""
		Return the lists of generic port pads and clock pads from *.co configuration file.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetInterface] Config file not loaded")
			return None
		return self.Config.GetInterface()
	#---------------------------------------------------------------
	def GetSynthesisScript(self, DestinationPath=None):
		"""
		Return the Synthesis script for this architecture.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetSynthesisScript] Config file not loaded")
			return "Unknown"
		
		Script=self.Config.GetSynthesisScript()
		if DestinationPath is None:
			return Script
		else:
			shutil.copy(Script, DestinationPath)
			Script=os.path.join(DestinationPath, os.path.basename(Script))
			return Script
	#---------------------------------------------------------------
	def GetRscEstimationScript(self, DestinationPath=None):
		"""
		Return the rsc estimation script for this architecture.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetRscEstimationScript] Config file not loaded")
			return "Unknown"
		
		Script=self.Config.GetRscEstimationScript()
		if DestinationPath is None:
			return Script
		else:
			shutil.copy(Script, DestinationPath)
			Script=os.path.join(DestinationPath, os.path.basename(Script))
			return Script
	#---------------------------------------------------------------
	def GetUploadScript(self, DestinationPath=None):
		"""
		Return the upload script for this architecture.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetUploadScript] Config file not loaded")
			return "Unknown"
		Script=self.Config.GetUploadScript()
		if DestinationPath is None:
			return Script
		else:
			shutil.copy(Script, DestinationPath)
			Script=os.path.join(DestinationPath, os.path.basename(Script))
			return Script
	#---------------------------------------------------------------
	def GetSourcesTemplate(self):
		"""
		Return the SourceList template for this architecture flow.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetSourcesTemplate] Config file not loaded")
			return None
		return self.Config.GetSourcesTemplate()
	#---------------------------------------------------------------
	def GetTemplates(self, SetupVars, DestinationPath=None):
		"""
		Return the Synthesis SetupFile for this architecture flow.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetTemplates] Config file not loaded")
			return "Unknown"
		TemplateList=self.Config.GetTemplates(SetupVars, DestinationPath)
		return TemplateList
	#---------------------------------------------------------------
	def GetSetupEnvScript(self):
		"""
		Return the SetupEnvScript for this architecture flow.
		"""
		if self.Config.Config is None:
			logging.error("[SyntheSys.SysGen.HW.GetSetupEnvScript] Config file not loaded")
			return None
		return self.Config.GetSetupEnvScript()
	#---------------------------------------------------------------
#	def GetUploadSetupFile(self, SetupVars, DestinationPath=None):
#		"""
#		Return the upload SetupFile for this architecture flow.
#		"""
#		if self.Config.Config is None:
#			logging.error("[SyntheSys.SysGen.HW.GetUploadSetupFile] Config file not loaded")
#			return "Unknown"
#		Script=self.Config.GetUploadSetupFile(SetupVars, DestinationPath)
#		return Script
	#---------------------------------------------------------------
	def Copy(self):
		"""
		Create a Hardware model copy.
		"""
		HwCopy=HwModel(Name=self.Name)
		return HwCopy
	#---------------------------------------------------------------
	def GenerateXML(self):
		"""
		Return XML representation of attributes.
		"""
		self.XMLElmt=LibEditor.HwModelXml(self)
		return self.XMLElmt
	#---------------------------------------------------------------
	def GetXMLElmt(self):
		"""
		return XML representation of Service.
		"""
		return self.XMLElmt
	#---------------------------------------------------------------
	def DumpToFile(self, OutputPath):
		"""
		Write XML informations to specified file.
		"""
		HwModelFilePath=os.path.join(OutputPath, "HwModel_{0}.xml".format(self.Name))
		logging.debug("Generate '{0}'.".format(HwModelFilePath))
		with open(HwModelFilePath, "wb+") as XMLFile:
			XMLFile.write(etree.tostring(self.XMLElmt, encoding="UTF-8", pretty_print=True))
		return HwModelFilePath
	#---------------------------------------------------------------
	def Reload(self):
		"""
		RE-Parse XML content and extract hw model information.
		"""
		self.SetFromXML(self.XMLElmt)
	#---------------------------------------------------------------
	def SetFromXML(self, XMLElmt):
		"""
		Parse XML content and extract hw model information.
		"""
		if not isinstance(XMLElmt, etree.Element):
			logging.error("[SetFromXML] Unable to parse HW model XML content.")
			logging.error("[SetFromXML] XMLElmt ('{0}') is not a instance of etree.Element.".format(type(XMLElmt)))
		self.XMLElmt=XMLElmt
		# Build a module object from module name, Type, Version
		self.Name      = XMLElmt.attrib.get("name")
		self.Version   = XMLElmt.attrib.get("version")
		self.Title     = XMLElmt.attrib.get("title")
		self.Purpose   = XMLElmt.attrib.get("purpose")
		self.Desc      = XMLElmt.attrib.get("description")
		self.Issues    = XMLElmt.attrib.get("issues")
		self.Speed     = XMLElmt.attrib.get("speed")
		self.Area      = XMLElmt.attrib.get("area")
		self.Tool      = XMLElmt.attrib.get("tool")
		
		for CoreElmt in XMLElmt.iterchildren("core"):
			for BehavElmt in CoreElmt.iter("behavioral"): # Iterate on all children
				self.AddSource(None, None, BehavElmt.attrib.get("path"), Synthesizable=False)
			for RTLElmt in CoreElmt.iter("rtl"): # Iterate on all children
				RTLType=RTLElmt.attrib.get("type")
				RTLName=RTLElmt.attrib.get("name")
				RTLPath=RTLElmt.attrib.get("path")
				self.AddSource(RTLType, RTLName, RTLPath, Synthesizable=True)
		# Get each feature
		for FeatureElmt in XMLElmt.iterchildren("features"):
			# Get pipeline feature
			for PipeElmt in FeatureElmt.iterchildren("pipeline"):
				self.PipeLength=PipeElmt.get("length")
			# Get resource usage
			for RscElmt in FeatureElmt.iterchildren("resources"):
				for DevElmt in RscElmt.iter(): # Iterate on all children
					Attr=DevElmt.attrib
					for RName, Rused in Attr.items():
						self.AddResource(DevElmt.tag, RName, Rused)
		return True
	#----------------------------------------------------------------------
	def ModuleResources(self, Mod, Library, ParamVal={}, RemoteHost=None):
		"""
		Update resources usage for module 'Mod' on this device.
		Parse *_par.par file and return a HwResources object.
		"""
		# SETUP PARAMETERS-----------------
		for PName, Value in ParamVal.items():
			if PName in Mod.Params:
				logging.info("\t> Set '{0}' to {1}.".format(PName, Value))
				Mod.EditParam(PName, Value)
			else:
				logging.error("No such parameter '{0}' in module '{1}'.".format(PName, Mod.Name))
		Mod.Reload()
		if Library: 
			Mod.IdentifyServices(Library.Services)
		Parameters={PName:P.GetValue() for PName, P in Mod.Params.items()}
		logging.info("Start evaluation of FPGA resources usage for module '{0}' on architecture '{1}' with parameters '{2}'".format(Mod, self, Parameters))
		#----------------------------------
		
		# Create a temporary directory
		OutputPath=tempfile.mkdtemp(prefix='ModuleRscEstimation_{0}_{1}'.format(Mod.Name, Timer.TimeStamp()))
			
		SrcPath=os.path.join(OutputPath, "src")
		if not os.path.isdir(SrcPath): os.makedirs(SrcPath)
		Serv=LibEditor.ProvidedServiceXml(Mod, Interfaces=[], Infos={"Name": Mod.Name, "Type": "", "Version": "", "Category": ""}, OutputPath=SrcPath)
		#--------------------------------------
		if Mod.LastCreatedInstance is None:
			Mod.GenSrc(Synthesizable=True, OutputDir=SrcPath, TestBench=False, ProcessedServ=dict(), IsTop=True, NewPkg=True, Recursive=True)
		
		#--------------------------------------
		# Create an Constraint file
		ConstraintFilePath, ModuleWrapper, NewClockSigs=self.GetPadConstraints(Module=Mod, Library=Library, OutputPath=SrcPath, ControlHW=None)
		if ConstraintFilePath is None:
			logging.error("[ModuleResources] No FPGA pad constraints generated: Synthesis aborted.")
			return None
		
		# Remove Ports that are not meant to be FPGA external pads----
		PNames=list(ModuleWrapper.Ports.keys())
		ExternalPads=list(ModuleWrapper.GetExternalPorts().keys())
		ClockResets=ModuleWrapper.GetResetNames()+list(NewClockSigs.keys())
		
		for PName in PNames:
			if PName in ExternalPads: continue
			elif PName in ClockResets: continue
			del ModuleWrapper.Ports[PName]
			
		#--------------------------------------
		ModuleWrapper.GenSrc(Synthesizable=True, OutputDir=SrcPath, TestBench=False, ProcessedServ={Serv.Name:Mod.LastCreatedInstance}, IsTop=True, NewPkg=False, Recursive=True)
		SynthMod=ModuleWrapper
		#--------------------------------------
			
		ResultFilesDict=FpgaOperations.Synthesize(HwModel=self, ConstraintFile=ConstraintFilePath, SrcDirectory=SrcPath, OutputPath=OutputPath, Module=SynthMod, RscEstimation=True, RemoteHost=RemoteHost)
#		ResultFilesDict={"MapReport":None}
		if 'RouteReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['RouteReport']
		elif 'PlaceReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['PlaceReport']
		else:
			logging.error("[ModuleResources] No resources report generated. Unable to extract resources consumption.")
			return None

		Rsc=self.GetUsedResourcesDict(RscFilePath)
		UsedResources=HwResources(Rsc)
	
#		UsedResources=HwResources({})
		Misc.CleanTempFiles(OutputPath)
		return UsedResources
	#---------------------------------------------------------------
	def AvailableResources(self):
		"""
		Return AvailableRsc dictionary attribute.
		"""
#		logging.debug("Available resources for FPGA '{0}': {1}".format(self.Name, self.AvailableRsc))
		return self.AvailableRsc
	#---------------------------------------------------------------
#	def EvaluateResources(self, APCG, OtherModules=[]):
#		"""
#		Return a HwResources object initialized with the sum of all Hw resources of a design.
#		"""
#		UsedRsc={}
#		for Node in APCG.nodes():
#			Mod=Node.GetService().GetModule(self)
#			ModUsedRsc=Mod.GetUsedResources(DeviceName=self.Name)
#			if len(ModUsedRsc)==0:
#				self.ModuleResources(Mod, RemoteHost=None)
#				ModUsedRsc=Mod.GetUsedResources(DeviceName=self.Name)
#			for Rsc, Value in ModUsedRsc.items():
#				if Rsc in UsedRsc:
#					UsedRsc[Rsc]+=Value
#				else:
#					UsedRsc[Rsc]=Value
#		for Mod in OtherModules:
#			ModUsedRsc=Mod.GetUsedResources(DeviceName=self.Name)
#			for Rsc, Value in ModUsedRsc.items():
#				if Rsc in UsedRsc:
#					UsedRsc[Rsc]+=Value
#				else:
#					UsedRsc[Rsc]=Value
#					
#		return HwResources(RscDict=UsedRsc)
	#---------------------------------------------------------------
	def GetSourcesFileName(self):
		"""
		return path of the BaseCtrlConstraints key in .ini file.
		"""
		return self.Config.GetSourcesFileName()
	#---------------------------------------------------------------
	def GetPadConstraints(self, Module, Library, OutputPath="./Constraints", ControlHW=None):
		"""
		Create a constraint file for specified Module.
		"""
		#----------------------------------------------------
		# Generate constraints from Signals type and board constraints dictionary.
		ConstraintPath, ModuleWrapper, NewClockSigs=HwConstraints.GenConstraintsFile(
						Module=Module, 
						HwModel=self, 
						ControlHW=ControlHW,
						Library=Library,
						OutputPath=OutputPath
						)
		#----------------------------------------------------
		return ConstraintPath, ModuleWrapper, NewClockSigs
	#---------------------------------------------------------------
	def GetBaseCtrlConstraints(self):
		"""
		return path of the BaseCtrlConstraints key in .ini file.
		"""
		return self.Config.GetBaseCtrlConstraints()
	#---------------------------------------------------------------
	def GetCtrlConfig(self, TargetHW, Module):
		"""
		Check if a configuration of this control HW is compatible with 
		TargetHW for a given Module and return it.
		"""
		ConfigDict=self.Config.GetConfigDict()
		NbClk, NbStim, NbTrace, NbBiDir = Module.Characteristics()
		logging.debug("Module characteristics: \n\t- clock number {0} \n\t- stimuli: {1} \n\t- traces: {2} \n\t- bidirectionals: {3}".format(NbClk, NbStim, NbTrace, NbBiDir))
		logging.debug("'{0}' Configurations found for target '{1}':".format(self.Name, TargetHW.Name))
		
		CompatibleConfigList=[]
		for Target, ConfigList in ConfigDict.items():
			if TargetHW.Name.lower()!=Target.lower(): 	
				logging.debug("\t\tskip target '{0}'".format(Target))
				continue
			for C in ConfigList:
				MaxStimuli, MaxTraces, MaxBidir, ClockMode=self.Config.GetConfigIO(C)
				if ClockMode=="mono" and NbClk>1:
					logging.debug("\t\tskip {Conf}: {S}s, {T}t, {B}b, {CM}".format(Conf=C, S=MaxStimuli, T=MaxTraces, B=MaxBidir, CM=ClockMode))
				elif NbStim>MaxStimuli or NbTrace>MaxTraces or NbBiDir>MaxBidir:
					logging.debug("\t\tskip {Conf}: {S}s, {T}t, {B}b, {CM}".format(Conf=C, S=MaxStimuli, T=MaxTraces, B=MaxBidir, CM=ClockMode))
				else:
					logging.debug("\t\t> {Conf}: {S}s, {T}t, {B}b, {CM} => COMPATIBLE".format(Conf=C, S=MaxStimuli, T=MaxTraces, B=MaxBidir, CM=ClockMode))
					CompatibleConfigList.append(C)
			break
		return CompatibleConfigList
	#---------------------------------------------------------------
	def GetCtrlConfigInterface(self, CtrlConfig, TargetInterfaceDict):
		"""
		"""
		CtrlIOPath=self.Config.GetCtrlIO(CtrlConfig)
		if CtrlIOPath is None: 
			logging.error("[GetConfigInterface] Configuration {0} of {1} do not have CtrlIO contraints file. Aborted.")
			return {}
		PortDict=HwConstraints.GetConstraintsFromFile(ConstraintsFile=CtrlIOPath)
		
		Elmts={
			"CLOCK" : "clk_matrix",
			"IN"    : "stim_o",
			"OUT"   : "trce_i",
			"INOUT" : "stim_io",
			}
		CtrlInterfaceDict={}
		Keys=list(PortDict.keys())
		
		# Pair Pad:Tag dictionary
		InvertedCtrlDict={}
		for T in self.InterfaceDict:
			InvertedCtrlDict.update({v:k for k,v in self.InterfaceDict[T].items()})
		for Type, Net in Elmts.items():
			OrderedKeys=reversed(Misc.NaturalSort([x for x in Keys if x.startswith(Net)]))
			CtrlInterfaceDict[Type]=collections.OrderedDict()
			for x in list(OrderedKeys):
				PadName=PortDict[x]
				if PadName in InvertedCtrlDict:
					Tag=InvertedCtrlDict[PadName]
#					print(x, "=>", PadName, "=>", Tag)
					CtrlInterfaceDict[Type][Tag]=PadName
				else:
					logging.error("{0} pad {1} not in {2}".format(Type, PadName, Misc.NaturalSort(InvertedCtrlDict.keys())))
#		for T in CtrlInterfaceDict:
#			print(CtrlInterfaceDict[T])
		return CtrlInterfaceDict
	#---------------------------------------------------------------
	def Synthesize(self, Mod, ConstraintFilePath, SrcDirectory, OutputPath="./FpgaSynthesis", RemoteHost=None):
		"""
		Execute Synthesis flow of Module for this Hardware.
		"""
		ResultFilesDict=FpgaOperations.Synthesize(HwModel=self, ConstraintFile=ConstraintFilePath, SrcDirectory=SrcDirectory, OutputPath=OutputPath, Module=Mod, RemoteHost=RemoteHost)
		if len(ResultFilesDict)==0:
			logging.error("[HW.Synthesize] No output files generated.")
		elif 'RouteReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['RouteReport']
			Rsc=self.GetUsedResourcesDict(RscFilePath)
			UsedResources=HwResources(Rsc)
			logging.debug("[HW.Synthesize] Used FPGA resources: {0}".format(UsedResources))
			Mod.UpdateResources(FpgaId=self.GetFPGA(FullId=False), HWRsc=UsedResources)
			Mod.DumpToLibrary() 
		elif 'PlaceReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['PlaceReport']
			Rsc=self.GetUsedResourcesDict(RscFilePath)
			UsedResources=HwResources(Rsc)
			logging.debug("[HW.Synthesize] Used FPGA resources: {0}".format(UsedResources))
			Mod.UpdateResources(FpgaId=self.GetFPGA(FullId=False), HWRsc=UsedResources)
			Mod.DumpToLibrary() 
		else:
			logging.warning("[HW.Synthesize] No resources report retrieved. ")
		
		return ResultFilesDict
	#---------------------------------------------------------------
	def GetUsedResourcesDict(self, MapFilePath):
		return GetUsedResourcesDict(MapFilePath)
	#---------------------------------------------------------------
	def Upload(self, BinaryPath, ScanChainPos=1, Remote=False):
		"""
		Upload bitstream to this Hardware's FPGA.
		"""
		return FpgaOperations.Upload(
				HwModel      = self, 
				BinaryPath   = BinaryPath, 
				ScanChainPos = ScanChainPos, 
				Remote       = Remote
				)
	#---------------------------------------------------------------
	def Display(self):
		"""
		Display Hardware model parameters in log.
		"""
		logging.info("HwModel:")
		logging.info("\tName='{0}'".format(self.Name))
	#---------------------------------------------------------------
	def __repr__(self):
		"""
		Return Hardware model string representation.
		"""
		return "HwModel(Name={0})".format(self.Name)
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return Hardware model name.
		"""
		return self.Name

#======================================================================
def GetUsedResourcesDict(MapFilePath):
	""" 
	Parse the '.map' file and fetch resources utilization and availability.
	"""
	Resources = {}
	logging.debug("Parse resource file '{0}'.".format(MapFilePath))
	with open(MapFilePath, 'r') as RsrcFile:
		for Line in RsrcFile.readlines():
#			Matched = re.match("^\s*Number\s+of\s+(?P<Resource>[\w/\s]+)s\s*:\s*(?P<Used>[,0-9]+)\s+out\s+of\s+(?P<Available>[,\d]+)\s+(?P<Percentage>[,\d]+)%\s*$", Line) # ISE format
			Matched = re.match("^\s*\|\s*(Slice|Block)\s*(?P<Resource>[\w\d]+).*\s*\|\s*(?P<Used>[<.,\d]+)\s*\|\s*([<,.\d]+)\s*\|\s*(?P<Available>[<,.\d]+)\s*\|\s*(?P<Percentage>[<,.\d]+)\s*\|\s*.*$", Line) # Vivado format
			if Matched:
				Correspondances={"LUT":"LUTs", "RAM":"RAM", "REGISTER":"Registers"}
					
				for Elmt, Identifier in Correspondances.items():
					if Matched.group("Resource")==Identifier:
						Used=Matched.group("Used").replace(',','.').replace('<','')
						Available=Matched.group("Available").replace(",", ".").replace('<','')
						Percentage=Matched.group("Percentage").replace(',','.').replace('<','')
						logging.debug("{0}:{1}/{2}({3}%)".format(Elmt, Used, Available, Percentage))
						Resources[Elmt]=[
							int(math.ceil(float(Used))), 
							int(math.ceil(float(Available))), 
							float(Percentage)/100
							]
	return Resources
	
	
	
	
