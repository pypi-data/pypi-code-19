

import os, sys, logging, shutil, re
import math, random
import glob
from lxml import etree
import collections

from SysGen.PackageBuilder import PackageBuilder
from SysGen.Signal import Signal, SigName
from SysGen.Condition import Condition
from SysGen import HDLEditor as HDL
from SysGen import LibEditor
from functools import reduce
from SysGen.HW.HwResources import HwResources

from Utilities.Misc import ReplaceTextInFile, SyntheSysError

#=======================================================================
class Instance():
	#---------------------------------------------------------------
	def __init__(self, Name, Mod):
		"""
		Module instance that gather information during design generation.
		"""
		self.Name=Name
		self.Mod=Mod
		self.Instances=[]
		if self.Mod: self.Mod.LastCreatedInstance=self
	#---------------------------------------------------------------
	def AddInstance(self, Name, Mod):
		"""
		Create instance and add it to instance list.
		"""
		I=Instance(Name=Name, Mod=Mod)
		self.Instances.append(I)
		return I
	#---------------------------------------------------------------
	def AddInstanceAsInstance(self, Inst):
		"""
		Add existing instance it to instance list.
		"""
		self.Instances.append(Inst)
		return Inst
	#---------------------------------------------------------------
	def WalkInstances(self, Path=[], Max=9999999, Depth=999999):
		"""
		Yield sub instances recursively.
		"""
		if Depth>0:
			Cnt=1
			yield self, Path
			for Inst in self.Instances:
				for I,P in Inst.WalkInstances(Path=Path+[self.Name,], Max=Max, Depth=Depth-1):
					if Cnt>Max: break
					yield I,P
					Cnt+=1
	#---------------------------------------------------------------
	def Copy(self):
		"""
		Create instance and add it to instance list.
		"""
		ICopy=Instance(Name=self.Name, Mod=self.Mod)
		ICopy.Instances=self.Instances[:]
		return ICopy
	#---------------------------------------------------------------
	def GetPathName(self, InstanceName):
		"""
		Return Path name of this instance from top module.
		"""
#		print("\n***** looking for",InstanceName,"from", self,"******")
		for Inst, Path in self.WalkInstances():
#			print(">", Inst, Path)
			if Inst.Mod is None: pass
			else:
				if Inst.Name==InstanceName:
#					print("FOUND ! ",Path, Inst.Name)
					return "/".join(Path[1:]+[Inst.Name,])
		logging.error("[GetPathName] Instance name '{0}' not found from instance '{1}'".format(InstanceName, self))
	#---------------------------------------------------------------
	def GatherConstraintSources(self, FromInst=None):
		"""
		return the constraints source file list of the module.
		"""
		CList=[]
		for Inst in reversed(self.Instances):
			ConstrSources=Inst.Mod.GetConstraintSources()
			if len(ConstrSources)==0: 
				if self.Name == FromInst:
					CList+=Inst.GatherConstraintSources(FromInst=None)
				else:
					CList+=Inst.GatherConstraintSources(FromInst=FromInst)
				continue
			PN=self.Mod.LastCreatedInstance.GetPathName(InstanceName=Inst.Name)
			if PN is None: sys.exit(1)
			if FromInst is None:
				PN="/".join([self.Name, PN])
				
			PatternDict={"INSTANCE_PATH_NAME":PN,}
			for SrcPath in ConstrSources: 
				for VarName, VarValue in PatternDict.items():
					ReplaceTextInFile(FileName=SrcPath, OldText="${0}".format(VarName), NewText="{0}".format(VarValue))
				CList.append(SrcPath)
		return CList
	#---------------------------------------------------------------
	def DisplayTree(self):
		"""
		Return instance name.
		"""
		for Inst, Path in self.WalkInstances():
			print(("-->".join(Path)+"-->"+Inst.Name))
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return instance name.
		"""
		return self.Name
			 
#=======================================================================
class Module(PackageBuilder):
	Instances=[]
	#---------------------------------------------------------------
	def __init__(self, XMLElmt, FilePath=None):
		"""
		Set global Module definition parameters.
		"""
		Module.Instances.append(self)
		PackageBuilder.__init__(self)
		self.Name      = ""
		self.Version   = ""
		self.Title     = ""
		self.Purpose   = ""
		self.Desc      = ""
		self.Issues    = ""
		self.Speed     = ""
		self.Area      = ""
		self.Tool      = ""
		self.Latency   = None
		self.MaxFreq   = {}
		self.DataIntroductionInterval = 1
		self.Params    = collections.OrderedDict()
		self.Const     = collections.OrderedDict()
		self.Ports     = collections.OrderedDict() # Dictionary of port signals
		self.OrthoPorts= collections.OrderedDict()
		self.Sources   = {"RTL":[], "Behavioral":[], "Constraints":[]} # two lists of sources
		
		self.Dependencies = {
			"package": collections.OrderedDict( ( ("IEEE.std_logic_1164", None),) ), 
			"library": collections.OrderedDict( ( ("IEEE", None),) )
			}
		self.Resources = {} # Dictionary of devices dictionaries of resources
		self.Latency=None
		self.ReqServ   = collections.OrderedDict()
		self.ServAlias = collections.OrderedDict()
		self.ProvidedServMap = collections.OrderedDict()
		self.ProvidedServ = collections.OrderedDict()
		self.IO        = []
		self.Vars      = {}
		self.XmlFilePath  = FilePath
		self.UsedParams=[]
#		self.Packages=["IEEE.std_logic_1164",] #,  "IEEE.std_logic_signed", "IEEE.std_logic_arith", ]
		self.XMLElmt   = XMLElmt
		self.AbstractModule=True
		self.TBEntity=None
		self.TBSource=None
		self.TBDependencies=[]
		self.NoOrthoPorts=False
		self.LastCreatedInstance=None
		
		if XMLElmt is None: pass
		elif not self.SetFromXML(XMLElmt): 
			logging.error("Unable to parse module XML content.")
	#---------------------------------------------------------------
	def Copy(self):
		"""
		return New instance of module class.
		"""
		M=Module(XMLElmt=None)
		M.Name=self.Name    
		M.Version=self.Version 
		M.Title=self.Title    
		M.Purpose=self.Purpose  
		M.Desc=self.Desc   
		M.Issues=self.Issues 
		M.Speed=self.Speed    
		M.Area=self.Area     
		M.Tool=self.Tool     
		M.Latency=self.Latency
		M.MaxFreq=self.MaxFreq   
		M.DataIntroductionInterval=self.DataIntroductionInterval
		M.Params=self.Params    
		M.Const=self.Const     
		M.Ports=self.Ports      # Dictionary of port signals
		M.OrthoPorts=self.OrthoPorts
		M.Sources=self.Sources    # two lists of sources
		M.Dependencies=self.Dependencies 
		M.Resources=self.Resources # Dictionary of devices dictionaries of resources
		M.Latency=self.Latency
		M.ReqServ=self.ReqServ
		M.ServAlias = self.ServAlias
		M.ProvidedServMap=self.ProvidedServMap
		M.ProvidedServ=self.ProvidedServ 
		M.IO=self.IO        
		M.Vars=self.Vars      
		M.XmlFilePath=self.XmlFilePath  
		M.UsedParams=self.UsedParams
		M.XMLElmt=self.XMLElmt   
		M.AbstractModule=self.AbstractModule
		M.TBEntity=self.TBEntity
		M.TBSource=self.TBSource
		M.TBDependencies=self.TBDependencies
#		M.Packages=self.Packages
		return M
	#---------------------------------------------------------------
	def GetTestBenchInfo(self):
		"""
		return testbench entity name, top source and a list of dependency files.
		"""
		return self.TBEntity, self.TBSource, self.TBDependencies
	#---------------------------------------------------------------
	def UpdateXML(self):
		"""
		Return XML representation of attributes.
		"""
		self.XMLElmt=LibEditor.ModuleXml(self)
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
		ModuleFilePath=os.path.join(OutputPath, "Module_{0}.xml".format(self.Name))
		logging.debug("Generate '{0}'.".format(ModuleFilePath))
		with open(ModuleFilePath, "wb+") as XMLFile:
			XMLFile.write(etree.tostring(self.XMLElmt, encoding="UTF-8", pretty_print=True))
		self.XmlFilePath=ModuleFilePath
		return self.XmlFilePath
	#---------------------------------------------------------------
	def DisplayXML(self):
		"""
		Print to std out xml content.
		"""
		print( etree.tostring(self.XMLElmt, encoding="UTF-8", pretty_print=True).decode("utf-8") )
		return 
	#---------------------------------------------------------------
	def DumpToLibrary(self):
		"""
		Write XML informations to library xml file.
		"""
		logging.debug("Re-write '{0}'.".format(self.XmlFilePath))
		with open(self.XmlFilePath, "wb+") as XMLFile:
			XMLFile.write(etree.tostring(self.XMLElmt, encoding="UTF-8", pretty_print=True))
		return self.XmlFilePath
	#---------------------------------------------------------------
	def GetLastCreatedInstance(self):
		"""
		Si a une instance retoune la dernière. Sinon en crée une.
		"""
		if self.LastCreatedInstance is None:
			return Instance(Name=self.Name+"_0", Mod=self)
		else:
			return self.LastCreatedInstance
	#---------------------------------------------------------------
	def EditParam(self, PName, PVal):
		"""
		Parse XML content and extract module information.
		"""
		# Change default value of module parameters
		Param = self.Params[PName]
		Param.Default = PVal
		Param.Value   = PVal
#		self.Params[PName].Vars.update({PName:PVal})
		# Get each parameter
		for ParamElmt in self.XMLElmt.iterchildren("parameter"):
			if ParamElmt.get("name")==PName:
				ParamElmt.attrib["default"]=str(PVal)
	#---------------------------------------------------------------
	def Reload(self):
		"""
		RE-Parse XML content and extract module information.
		"""
		self.ReqServ=collections.OrderedDict()
		self.SetFromXML(self.XMLElmt)
	#---------------------------------------------------------------
	def SetFromXML(self, XMLElmt):
		"""
		Parse XML content and extract module information.
		"""
		PythonTypes={
			"float"   : float,
			"integer" : int,
			"fixed"   : int,
		}
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
		TS=XMLElmt.attrib.get("typesignature")
		if TS is None: 
			self.TypeSignature = tuple()
		else:
			self.TypeSignature = tuple([PythonTypes[T] for T in TS.split()])
#		logging.info("Found module: '{0}'".format(self.Name))
		
		# Get each parameter
		ParamDict=collections.OrderedDict()
		for ParamElmt in XMLElmt.iterchildren("parameter"):
			Attr=ParamElmt.attrib
			try: Val=int(Attr.get("default"))
			except: Val=Attr.get("default")
			ParamDict[Attr.get("name").replace('.', '_')]=Val
		for ParamElmt in XMLElmt.iterchildren("parameter"):
			self.AddParameter(ParamElmt, VarDict=ParamDict)
		# Get each input
		for InputElmt in XMLElmt.iterchildren("input"):
			Attr=InputElmt.attrib
			self.AddPort(PName=Attr.get("name"), PDir="IN", PType=Attr.get("type"), PTypeImport=Attr.get("typeimport"), PSize=Attr.get("size"), PDefault=Attr.get("default"))
		# Get each output
		for OutputElmt in XMLElmt.iterchildren("output"):
			Attr=OutputElmt.attrib
			self.AddPort(PName=Attr.get("name"), PDir="OUT", PType=Attr.get("type"), PTypeImport=Attr.get("typeimport"), PSize=Attr.get("size"), PDefault=Attr.get("default"))
		# Get each source
		for CoreElmt in XMLElmt.iterchildren("core"):
			for BehavElmt in CoreElmt.iter("behavioral"): # Iterate on all children
				self.AddSource(None, None, BehavElmt.attrib.get("path"), Synthesizable=False)
			for RTLElmt in CoreElmt.iter("rtl"): # Iterate on all children
				RTLType=RTLElmt.attrib.get("type")
				RTLName=RTLElmt.attrib.get("name")
				RTLPath=RTLElmt.attrib.get("path")
				self.AddSource(RTLType, RTLName, RTLPath, Synthesizable=True)
			for ConstraintsElmt in CoreElmt.iter("constraints"): # Iterate on all children
				ConstraintsType=ConstraintsElmt.attrib.get("type")
				ConstraintsName=ConstraintsElmt.attrib.get("name")
				ConstraintsPath=ConstraintsElmt.attrib.get("path")
				self.AddConstraintSource(ConstraintsType, ConstraintsName, ConstraintsPath)
		# Get each feature
		for FeatureElmt in XMLElmt.iterchildren("features"):
			# Get pipeline feature
			for DesignElmt in FeatureElmt.iterchildren("design"):
				try: 
					Latency=int(DesignElmt.get("Latency"))
					self.Latency=Latency
				except:
					logging.warning("Attribute 'Latency' of 'design' element (line '{0}') cannot be interpreted as an integer. Ignored.".format(DesignElmt.sourceline))
				try: 
					DII=int(DesignElmt.get("DataIntroductionInterval"))
					self.DataIntroductionInterval=DII
				except:
					logging.warning("Attribute 'DataIntroductionInterval' of 'design' element (line '{0}') cannot be interpreted as an integer. Ignored.".format(DesignElmt.sourceline))
					
			# Get resource usage
			for FPGAElmt in FeatureElmt.iterchildren("fpga"):
				FPGA=FPGAElmt.attrib.get("id").upper()
				for RscElmt in FPGAElmt.iterchildren("resources"): # Iterate on all children
					Attr=RscElmt.attrib
					for RName, Rused in Attr.items():
						self.AddResource(FPGA, RName.upper(), Rused)
							
				for ClockElmt in FPGAElmt.iterchildren("clock"):
					try: MaxFreq=int(ClockElmt.attrib.get("MaxFreq"))
					except:
						logging.warning("Attribute 'MaxFreq' of 'clock' element (line '{0}') cannot be interpreted as an integer. Ignored.".format(ClockElmt.sourceline))
						continue
					self.MaxFreq[FPGA]=MaxFreq # in MHz
		# Get each service
		for ServElmt in XMLElmt.iterchildren("services"):
			for ReqElmt in ServElmt.iter("required"): # Iterate on all children
				ReqMapping=collections.OrderedDict()
				ReqName=ReqElmt.get("name")
				ReqID=ReqName.split(':')
				if len(ReqID)>1: RVars=ReqID[1:]
				else: RVars=[]
				for MapElmt in ReqElmt.iter("map"):
					VDict=self.Vars.copy()
					if MapElmt.get("formal"):
						Formal=MapElmt.get("formal")
						ActualList=SigName(MapElmt.get("actual"), RVars, VDict)
#						WhenExpr=MapElmt.get("when")
#						Cond=eval(str(WhenExpr), VDict)
#						if MapElmt.get("when")==None: Cond=True
#						ReqMapping[Formal]=[ActualList, Condition(WhenExpr), {}]
						if MapElmt.get("when") is None: Cond=True
						else: Cond=Condition(eval(str(MapElmt.get("when")), VDict))
						ReqMapping[Formal]=[ActualList, Cond, {}]
					else:
						self.IO.append(MapElmt.get("actual"))
				for V in RVars:	V=eval(V, VDict)
				Alias = ReqElmt.get("alias")
				if not Alias: Alias=ReqName
				self.AddReqServ(ReqID[0], ReqElmt.attrib.get("type"), ReqElmt.attrib.get("version"), ReqMapping, UniqueName=ServName(Alias))
			for OffElmt in ServElmt.iterchildren("offered"): # Iterate on all children
				OffMapping=collections.OrderedDict()
				for MapElmt in OffElmt.iter("map"):
					OffMapping[MapElmt.get("formal")]=MapElmt.get("actual")
				self.AddProvServ(OffElmt.attrib.get("name"), OffElmt.attrib.get("alias"), OffMapping)
		# Get each looped parameters
		for LoopElmt in XMLElmt.iterchildren("loop"):
			self.ParseLoops(LoopElmt)
			
		if len(self.Sources["RTL"])>0:
			self.AbstractModule=False
#		logging.debug("[MODULE={0}] Parse completed.".format(self.Name))
		return True
	#---------------------------------------------------------------
	def ParseLoops(self, LoopElmt, Indexes=[], IdxDict={}):
		"""
		Parse each service requirement in XML loop element.
		"""
		Var, InitVal, LastVal = self.ParseIndex(LoopElmt.get("index"))
		if Var: 
			if not Indexes.count(Var): Indexes.append(Var)
			for Index in range(InitVal, LastVal+1):
				LocalParams={}
				IdxDict[Var]=Index
				# Get each constant (format: Name_v0val0_v1val1...)
				SigVars=self.Vars.copy()
				for ParamElmt in LoopElmt.iterchildren("parameter"):
					Attr = ParamElmt.attrib		
					BaseName=Attr.get("name")			
					CName=BaseName+'_'+"".join([x+str(IdxDict[x]) for x in Indexes])
					CType=Attr.get("type")
					CTypeImport=Attr.get("typeimport")
					CSize=Attr.get("size")
					CDefault=Attr.get("default")
					SigVars.update(IdxDict)
					Constant=Signal(CName, CType, CTypeImport, CSize, CDefault, ParamVars=SigVars.copy()).HDLFormat(SigVars.copy())
					if not list(self.Const.keys()).count(BaseName): self.Const[BaseName]={}
					self.Const[BaseName][CName]=Constant
					LocalParams[BaseName]=CName
				
				# Get each service
				for ServElmt in LoopElmt.iterchildren("services"):
					for ReqElmt in ServElmt.iter("required"): # Iterate on all children
						ReqName=ReqElmt.get("name")
						ReqID=ReqName.split(':')
						if len(ReqID)>1: RVars=ReqID[1:]
						else: RVars=[]
						ReqMapping=collections.OrderedDict()
						for MapElmt in ReqElmt.iter("map"):
							VDict=self.Vars.copy()
							VDict.update(IdxDict.copy())
							Formal=MapElmt.get("formal")
							ActualList=SigName(MapElmt.get("actual"), RVars, VDict, LocalParams=LocalParams) 
							#------Index Value replacements----------
							for Actual in ActualList:
								Original=Actual[1][:] # TODO: info on actual content
								Ref=Actual[1].replace('*','_').replace('+','_').replace('-','_').replace('/','_').replace('(','_').replace(')','_')
								OpList=[] # list element without operators
								for A0 in Actual[1].split('*'):
									for A1 in Actual[1].split('+'):
										for A2 in Actual[1].split('-'):
											for A3 in Actual[1].split('/'):
												for A4 in Actual[1].split('('):
													for A5 in Actual[1].split(')'):
														OpList.append(A5)
								# Replace each index by its value
								for i, Operand in enumerate(OpList):
									if Operand in IdxDict:
										OpList[i]=str(IdxDict[Operand])
								# re-insert the operator at proper place
								Actual[1]=""
								Cnt=0 # Counter of operand
								i=0 # Counter for character
								
								
								while(len(Actual[1])!=len(Ref)):
									if i>=len(Original) or i>=len(Ref):
										logging.warning("{0}>=len(Original) ({1}) or {0}>=len(Ref) ({2})".format(i,Original, Ref))
										break
									if Original[i]!=Ref[i]:
										Actual[1]+=Ref[i]
										Cnt+=1
										i+=1
									else:
										Actual[1]+=OpList[Cnt]
										i+=len(OpList[Cnt])
										Cnt+=1
							#----------------------------------------
							if MapElmt.get("when") is None: Cond=True
							else: Cond=Condition(eval(str(MapElmt.get("when")), VDict))
							ReqMapping[Formal]=[ActualList, Cond, IdxDict.copy()]
						for V in RVars:	V=eval(V, VDict)
						Alias = ReqElmt.get("alias")
						if not Alias: Alias=ReqName
						else: Alias+=":{0}".format(Var)
						self.AddReqServ(ReqID[0], ReqElmt.attrib.get("type"), ReqElmt.attrib.get("version"), ReqMapping, UniqueName=ServName(Alias, Vars=IdxDict.copy()))
				# Get each looped children
				for SubLoopElmt in LoopElmt.iterchildren("loop"):
					self.ParseLoops(SubLoopElmt, Indexes[:], IdxDict.copy())
		else: logging.error("[Module '{0}'] Can't find index name in loop.".format(self))
	#---------------------------------------------------------------
	def ParseIndex(self, String):
		"""
		Parse index string in loop. Ex: "r=[0,rows[" <=> for r in range(0,rows,1)
		"""
		if String:
			try: Var, Range  = String.split('=')
			except: logging.error("[Module '{0}'] It should be one (and only one) '=' symbol in index description '{1}'.".format(self, String))
			try: Left, Right = Range.split(',')
			except: logging.error("[Module '{0}'] It should be one (and only one) ',' symbol in index description '{1}'.".format(self, String))

			InitVal=eval(Left[1:], self.Vars.copy())
			if Left.startswith('['): pass
			elif Left.startswith(']'): InitVal+=1
			else: logging.error("[Module '{0}'] Wrong range description '{1}'. Expected brakets range format (ex: '[0,rows[').".format(self, Range))

			LastVal=eval(Right[:-1], self.Vars.copy())
			if Right.endswith('['): LastVal-=1
			elif Left.endswith(']'): pass
			else: logging.error("[Module '{0}'] Wrong range description '{1}'. Expected brakets range format (ex: '[0,rows[').".format(self, Range))
		
			return Var, InitVal, LastVal
		else:
			return None, 0, 0
	#---------------------------------------------------------------
	def IdentifyServices(self, ServList):
		"""
		Replace ID by a Service object
		and find the corresponding service in library
		"""
		# Replace ID by a Service object
#		if self.Name=="PCIe_Riffa22_VC707":
#			print("MOD:", self.Name)
		RequiredServ = collections.OrderedDict()
		for ID, ServReq in self.ReqServ.items():
			SName, SType, SVersion, UniqueName = ID.split('#')
			if SName in RequiredServ:
				RequiredServ[SName].append(ServReq)
			else:
				RequiredServ[SName]=[ServReq,]
			
#		print("ServList:", [S.Name for S in ServList])
#		print("RequiredServ:", [R for R in RequiredServ])
		for S in ServList:
#			if self.Name=="PCIe_Riffa22_VC707":
#				print(">", S.Name)
			# Find the corresponding service in library
			if S.Name in RequiredServ:# and S.Version==SVersion:	
#				print("\t> Require service", S)
				for Req in RequiredServ[S.Name]:
					Req[0]=S
			elif S.Name in self.ProvidedServ:
#				print("\t> offer service", S)
				self.ProvidedServ[S.Name]=S
	#---------------------------------------------------------------
	def AddReqServ(self, SName, SType, SVersion, Mapping={}, UniqueName="", Serv=None):
		"""
		Add a required service (defined by SName, SType, SVersion) to this module.
		"""
		# Find a unique name for the service in that module
#		Index=0
#		while('#'.join([SName, SType, SVersion, "{0}_{1}".format(UniqueName, Index)]) in self.ReqServ): Index+=1
		
		# Create ID and store in dictionary
		ID='#'.join([SName, SType, SVersion, UniqueName])
		
		if SType=="orthogonal":
			Constraints=None
			for Formal in Mapping:
				if Formal.lower()=="constraints": 
					ActualList=Mapping.pop(Formal)
					Constraints=ActualList[0][0][1]
					break
			self.ReqServ[ID]=[Serv, Mapping, True, Constraints]
		else:
			self.ReqServ[ID]=[Serv, Mapping, False, None]
	#---------------------------------------------------------------
	def GetReqServMap(self, ReqServName):
		"""
		Return the mapping dictionary of requested service if it exists. Return Empty dictionary otherwise.
		"""
		ReqDict=collections.OrderedDict()
		for ReqServ, Mappings, IsOrtho, Constraints in list(self.ReqServ.values()):
			if ReqServ!=None:
				if ReqServ.Name==ReqServName:
					for Formal, Map in Mappings.items():
						ActualList, Cond, IdxDict = Map
						if len(ActualList)>1:
							# TODO: for InstName, SigName, Index in ActualList:
							pass
						else:
							if len(ActualList)==1:
								InstName, SigName, Index = ActualList[0]
								if SigName in self.Ports:
									ReqDict[SigName]=self.Ports[SigName]
								elif SigName in self.OrthoPorts:
									ReqDict[SigName]=self.OrthoPorts[SigName]
								# else it's a modifier
							else:
								logging.error('No mapping for formal port {0}. Unable to get required service associated.'.format(Formal))
				
#		if len(ReqDict)==0: 
#			logging.debug("Requested service '{0}' not found in module '{1}'. No mapping to return.".format(ReqServName, self))
		return ReqDict
	#---------------------------------------------------------------
	def GetReqServ(self, ReqServName=None):
		# for ReqServ, Mappings in self.ReqServ.values():
		SList=[x[0] for x in list(self.ReqServ.values())]
		if ReqServName is None:
			return SList
		else:
			return [x for x in SList if x.Name==ReqServName and not (x is None)]
	#---------------------------------------------------------------
	def AddProvServ(self, SName, SAlias, mapping):
		"""
		Add a service (defined by name and alias) to this module.
		"""
		self.ServAlias[SAlias]      = SName
		self.ProvidedServMap[SName] = mapping
		if not SName in self.ProvidedServ:
			self.ProvidedServ[SName] = None
	#---------------------------------------------------------------
	def AddParameter(self, XMLElmt, VarDict={}):
		"""
		Add a parameter (defined by Name/type/size/default value) to this module.
		"""
		# Set dictionary of parameters values.
		Variables=self.Vars.copy()
		Variables.update(VarDict.copy())
		
		Param=Signal()
		Param.SetFrom(XMLElmt, Vars=Variables)
		self.Params[Param.Name] = Param  # TODO: Is the copy necessary ?
		self.Params[Param.Name].IsParam = True
		
		self.Vars[Param.Name] = Param.integers(Base=10, Variables=Variables)
		
		self.DependencyPkg(Param.TypeImport)
	#---------------------------------------------------------------
	def GetParametersDict(self):
		"""
		Return the dictionary of module parameters.
		"""
		return self.Params
	#---------------------------------------------------------------
	def GetUsedParam(self):
		"""
		Return the dictionary of USED module parameters.
		"""
		UsedParams=self.UsedParams[:]
		for PName, Port in self.Ports.items():
			UsedParams+=Port.GetUsedParam()
		return UsedParams
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
	#---------------------------------------------------------------
	def AddPortAsSignal(self, Sig):
		"""
		Add a port (defined by Name/type/size/default value) to this module.
		"""
		# Set dictionary of parameters values.
		self.Ports[Sig.GetName()]=Sig
		self.DependencyPkg(Sig.TypeImport)
	#---------------------------------------------------------------
	def AddPort(self, PName, PDir, PType, PTypeImport, PSize, PDefault, PModifier=None, PShare=False, IdxDict={}):
		"""
		Add a port (defined by Name/type/size/default value) to this module.
		"""
		# Set dictionary of parameters values.
		Variables=self.Vars.copy()
		Variables.update(IdxDict.copy())
		
		PName=PName.replace('.', '_')
		Default=None if PDefault=="" else PDefault
		self.Ports[PName]=Signal(PName, PType, PTypeImport, PSize, Default, PDir, PModifier, bool(PShare), ParamVars=Variables.copy())
		self.DependencyPkg(PTypeImport)
	#---------------------------------------------------------------
	def GetPortsDict(self):
		"""
		Return the dictionary of module ports.
		"""
		Ports = collections.OrderedDict()
		Rsts  = list(self.GetReqServMap("reset").keys())
		Clks  = list(self.GetReqServMap("clock").keys())
		INs   = list(self.GetReqServMap("FPGA_Input").keys())
		OUTs  = list(self.GetReqServMap("FPGA_Output").keys())
		for k, v in self.Ports.items():
			if k not in Rsts+Clks+INs+OUTs:
				Ports[k]=v
		return Ports
	#---------------------------------------------------------------
	def AddSources(self, SourceFileList, IsDependency=True):
		"""
		Add a source files to this module Sources['RTL'] attribute.
		> Avoid double adds
		"""
		NewSrcList=[]
		for S in SourceFileList:
			if S in self.Sources["RTL"]:
				self.Sources["RTL"].remove(S)
#			print("Add", os.path.basename(S))
			NewSrcList.append(S)
		if IsDependency is True:
			self.Sources["RTL"]=NewSrcList+self.Sources["RTL"]
		else:
			self.Sources["RTL"]=self.Sources["RTL"]+NewSrcList
#		print(self.Name, "=> Current sources:", [os.path.basename(src) for src in self.Sources["RTL"]])
		return NewSrcList
	#---------------------------------------------------------------
	def AddSource(self, SrcType, SrcName, SrcPathPattern, Synthesizable=False):
		"""
		Add a source file to this module.
		"""
		CurDir = os.path.abspath('./')
		if not (self.XmlFilePath is None):
			os.chdir(os.path.dirname(self.XmlFilePath))
		
		for SrcPath in glob.glob(SrcPathPattern):
			if not os.path.isfile(SrcPath):
				logging.error("[Module '{0}'] No such file '{1}'. Fix the XML lib file ('{2}')".format(self.Name, SrcPath, self.XmlFilePath))
				sys.exit(1)
			if Synthesizable: 
				if SrcType!=None:
					SupportedTypes=["package", "library"]
					if SrcType.lower() in SupportedTypes:
						if SrcName in self.Dependencies[SrcType]:
							self.Dependencies[SrcType][SrcName].append(os.path.abspath(SrcPath))
						else:
							self.Dependencies[SrcType][SrcName]=[os.path.abspath(SrcPath),]
					else:
						logging.error("Attribute 'type' of 'rtl' not recognized. Expected {0}. Found '{1}'".format(' or '.join(SupportedTypes), SrcType))
				else:
					self.Sources["RTL"].append(os.path.abspath(SrcPath))
			else:   self.Sources["Behavioral"].append(os.path.abspath(SrcPath))
			
			
		if not (self.XmlFilePath is None):
			os.chdir(CurDir)
	#---------------------------------------------------------------
	def AddConstraintSource(self, SrcType, SrcName, SrcPath):
		"""
		Add a source file to this module.
		"""
		CurDir = os.path.abspath('./')
		if not (self.XmlFilePath is None):
			os.chdir(os.path.dirname(self.XmlFilePath))
			
		self.Sources["Constraints"].append(os.path.abspath(SrcPath))
		
		if not (self.XmlFilePath is None):
			os.chdir(CurDir)
	#---------------------------------------------------------------
	def GetConstraintSources(self, ReplacePatternDict={}):
		"""
		return the constraints source file list of the module.
		"""
		if len(ReplacePatternDict)>0:
			for SrcPath in self.Sources["Constraints"]: 
				for VarName, VarValue in ReplacePatternDict.items():
					ReplaceTextInFile(FileName=SrcPath, OldText="${0}".format(VarName), NewText="{0}".format(VarValue))
		return self.Sources["Constraints"]
	#---------------------------------------------------------------
	def GetDependencies(self):
		"""
		Return dictionary of Libname:[library paths,].
		"""
		Dep = self.Dependencies.copy()
		# Get child services dependencies
		for ReqServ, Mapping, IsOrtho, Constraints in list(self.ReqServ.values()):
			if ReqServ is None:
				logging.error("[Module.GetDependencies] No requested service for mapping !")
				continue
			SubMod = ReqServ.GetModule() # TODO : Manage constraints
			if SubMod!=None: Dep.update(SubMod.GetDependencies()) # Recursive
			
		return Dep
	#---------------------------------------------------------------
	def AddResource(self, Dev, RName, Rused=0):
		"""
		Add a resource information for an FPGA to this module.
		"""
		if Dev in self.Resources:
			HwR=self.Resources[Dev]
		else:
			HwR=HwResources()
			self.Resources[Dev]=HwR
		
		return HwR.AddResources(Name=RName.upper(), Used=Rused, Available=-1, Percentage=-1)
	#---------------------------------------------------------------
	def CompatibleFPGAs(self):
		"""
		Return list of referenced FPGA.
		"""
		return [FPGA.upper() for FPGA in self.Resources.keys()]
	#---------------------------------------------------------------
	def GetUsedResources(self, DeviceName):
		"""
		Add a resource information for an FPGA to this module.
		"""
		if self.Name=="SimuCom": return HwResources()
		if DeviceName in self.Resources:
			return self.Resources[DeviceName]
#		elif "ALL" in self.Resources:
#			return HwResources()
		else:
			logging.debug("{0}'s resources: {1}".format(self, self.Resources))
			logging.warning("[Module.GetUsedResources] Device '{0}' not in module '{1}' resources.".format(DeviceName, self))
		return None
	#---------------------------------------------------------------
	def GetOutputDataSize(self):
		"""
		Return the number of bits for output data.
		"""
		Sum=0
		for SName, S in self.ProvidedServ.items():
			if SName.lower() in ["userclock", "userreset"]: continue
			Sum+=S.GetOutputDataSize()
		return Sum
	#---------------------------------------------------------------
	def GetMaxFreq(self, FPGA):
		"""
		Return highest frequency associated with an FPGA.
		"""
		if "ALL" in self.MaxFreq:
			return self.MaxFreq["ALL"]
		elif FPGA.upper() in self.MaxFreq:
			return self.MaxFreq[FPGA]
		else:
			return None
	#---------------------------------------------------------------
	def GetLatency(self):
		"""
		Return latency of the module.
		"""
		return self.Latency
	#---------------------------------------------------------------
	def GetDataIntroductionInterval(self):
		"""
		Return Data Introduction Interval value.
		"""
		return self.DataIntroductionInterval
	#---------------------------------------------------------------
	def GetThroughput(self, FPGA):
		"""
		Return highest throughput associated with an FPGA.
		"""
		if "ALL" in self.MaxFreq:
			return self.MaxFreq["ALL"]/self.DataIntroductionInterval
		elif FPGA.upper() in self.MaxFreq:
#			print("self.MaxFreq[FPGA]:", self.MaxFreq[FPGA])
#			print("self.DataIntroductionInterval:", self.DataIntroductionInterval)
			return self.MaxFreq[FPGA]/self.DataIntroductionInterval
		else:
			return None
	#---------------------------------------------------------------
	def IsAbstract(self):
		"""
		Return False if RequiredServices list is empty, True otherwise.
		"""
		return self.AbstractModule
	#---------------------------------------------------------------
	def GetAbsFileName(self):
		"""
		Return abstract name of top file if module is abstract.
		"""
		if self.IsAbstract(): return "{0}.vhd".format(self.Name)
		else: return None
	#----------------------------------------------------------------------
	def GetTop(self):
		"""
		return entity name and path of HDL Top source.
		"""
		Sources=self.Sources["RTL"]
#		logging.debug("Sources: '{0}'".format(self.Sources["RTL"]))
		if len(Sources)==0:
			return None, None
#		Design=DesignTree.Design(FileList=Sources)
#		TopList=Design.TopComponentList
#		logging.debug("TopList: '{0}'".format(TopList))
#		if len(TopList)==0: return None, None	
#		Top=TopList[0]
#		
#		EntityName=Top.EntityName
#		TopPath=Top.XmlFilePath
#				
#		return EntityName, TopPath
		return self.Name, Sources[-1]
	#---------------------------------------------------------------
	def GetSources(self, Synthesizable=True, Constraints=None, IsTop=False, IgnorePkg=True):
		"""
		Return the list of source files of this module and its dependencies.
		"""
		SrcList=[]
		if Synthesizable: TYPE = "RTL"
		else: TYPE = "Behavioral"
		for Src in self.Sources[TYPE]:
			if Src not in SrcList: SrcList.append(Src)
		if not IgnorePkg:
			for PackSrcList in list(self.Dependencies["package"].values()):
				for PackSrc in PackSrcList:
					if PackSrc not in SrcList: SrcList.append(PackSrc)
		if IsTop: SrcList.append(os.path.abspath(self.GetTopPackName()))
		for ID, (Serv, Map, IsOrtho, Constraints) in self.ReqServ.items():
			if Serv is None:
				logging.error("[Module {0}] Required service '{1}' missing: source fetch skipped.".format(self, ID))
			else:
				if not IsOrtho:
					SubMod = Serv.GetModule(Constraints=Constraints)
					if SubMod!=None:
						SubModSrcList = SubMod.GetSources(Synthesizable=Synthesizable, Constraints=Constraints)
						SrcList+=[x for x in SubModSrcList if not (x in SrcList) ]
		if self.IsAbstract(): SrcList.append(os.path.join(os.path.dirname(self.XmlFilePath), self.GetAbsFileName()))
		
		return SrcList
	#---------------------------------------------------------------
#	def AddLibSources(self, SourceList, Synthesizable=True):
#		"""
#		Add HDL src to the list of source files of this module.
#		"""
#		if Synthesizable: TYPE = "RTL"
#		else: TYPE = "Behavioral"
#		for Src in SourceList: 
#			for SrcItem in glob.iglob(Src):
#				if SrcItem not in self.Sources[TYPE]: self.Sources[TYPE].append(SrcItem)
#		return True
	#---------------------------------------------------------------
	def RemoveSources(self, SourceList, Synthesizable=True):
		"""
		Remove HDL src to the list of source files of this module.
		"""
		if Synthesizable: TYPE = "RTL"
		else: TYPE = "Behavioral"
		for Src in SourceList: 
			if Src in self.Sources[TYPE]: 
				self.Sources[TYPE].remove(Src)
		return True
	#---------------------------------------------------------------
	def ReplaceSource(self, OldPath, NewPath, Synthesizable=True):
		"""
		Remove HDL src to the list of source files of this module and replace it by New pat.
		"""
		if Synthesizable: TYPE = "RTL"
		else: TYPE = "Behavioral"
		if OldPath in self.Sources[TYPE]: 
			Idx=self.Sources[TYPE].index(OldPath)
			self.Sources[TYPE].remove(OldPath)
			self.Sources[TYPE].insert(Idx, NewPath)
		return True
	#---------------------------------------------------------------
	def ReplaceConstraintSource(self, OldPath, NewPath):
		"""
		Remove HDL src to the list of source files of this module and replace it by New path.
		Replace each pattern by its value.
		"""
		if OldPath in self.Sources["Constraints"]: 
			Idx=self.Sources["Constraints"].index(OldPath)
			self.Sources["Constraints"].remove(OldPath)
			self.Sources["Constraints"].insert(Idx, NewPath)
			
		return True
	#---------------------------------------------------------------
	def Provide(self, SName):
		"""
		Return True if this module implement the specified service (identified by its name).
		"""
		if SName in self.ProvidedServ: return True
		else: return False
	#---------------------------------------------------------------
	def GetProvidedService(self, Name=None):
		"""
		Return first item found in self.ProvidedServ.
		"""
		if len(self.ProvidedServ)==0: 
			logging.warning("Module {0} provide no services !".format(self))
			return None
		else: 
			if Name is None:  
				
				for Key, Value in self.ProvidedServ.items():
					return Value # TODO manage several provided serv
			else:
				return self.ProvidedServ[Name]
	#---------------------------------------------------------------
	def GetPadConstraints(self):
		Constraints=[]
		UniqueList=[]
		for PName, P in self.Ports.items():
			if P.Name in UniqueList: continue
			else: UniqueList.append(P.Name)
			if P.Constraints is None: 
				Constraints.append( (P, None, "Ignore") )
			else:
				Type, Identifier, FormalMap = P.Constraints
				PadType=FormalMap.upper()
				Constraints.append( (P, PadType, Identifier) )
				
		if self.IsAbstract():
			for PName, P in self.OrthoPorts.items():
				if P.Name in UniqueList: continue # Select only ortho names (gather clock/reset signals)
				else: UniqueList.append(P.Name)
				OP=P.Copy()
				OP.Name=PName
				if OP.Constraints is None: 
					Constraints.append( (OP, None, "Ignore") )
				else:
					Type, Identifier, FormalMap = OP.Constraints
					PadType=FormalMap.upper()
					Constraints.append( (OP, PadType, Identifier) )
		return Constraints
	#---------------------------------------------------------------
	def GetClockNames(self, MappedName=False):
		"""
		Return the list of clock names connected to service 'clock'.
		"""
#		print(Level*'    '+"=================")
#		print(Level*'    '+"Module:", self.Name)
		ClockList=[]
#		print("self:", self.Name)
#		print("self.ReqServ:", self.ReqServ)
		for ServID, (Serv, ClkMapping, IsOrtho, Constraints) in self.ReqServ.items():
			#-------------------
			if ServID.startswith("clock"):
#				print()
#				print(Level*'    '+"ServID:", ServID)
#				print("*Serv:", Serv)
#				Serv, ClkMapping, ClkIsOrtho=self.ReqServ[ServID]
#				print("ClkMapping:", ClkMapping)
				for Formal, ActualCond in ClkMapping.items():
					if Formal in Serv.Params: continue
					ActualList, Cond, OtherDict=ActualCond
					ActualName=ActualList[0][1]
#					print(Level*'    '+"---> ActualName:", ActualName)
					if ActualName in self.Ports:
						if MappedName: 
							ClockList.append(SharedName(Formal=Formal, Params=Serv.Params, ReqMap=ClkMapping))
#							ClockList.append('clock_'+ClkMapping["freq"][0][0][1])
						else: ClockList.append(ActualName)
					else:
						ClockList.append(SharedName(Formal=Formal, Params=Serv.Params, ReqMap=ClkMapping))
#						ClockList.append('clock_'+ClkMapping["freq"][0][0][1])
#				print(Level*'    '+"  *ClockList:", ClockList)
			#-------------------
#			Serv, ModMap, ServIsOrtho = self.ReqServ[ServID]
			if Serv is None: 
				logging.warning("[GetClockNames] Service '{0}' not a referenced service.".format(ServID))
				continue
			Mod=Serv.GetModule()
			if Mod: ClockList+=Mod.GetClockNames(MappedName=True)
		ClockList=list(set(ClockList))
		return ClockList
	#---------------------------------------------------------------
	def GetResetNames(self, MappedName=False):
		"""
		Return the list of reset names connected to service 'reset'.
		"""
		ResetList=[]
		for ServID, (Serv, ResetMapping, IsOrtho, Constraints) in self.ReqServ.items():
			if Serv is None: 
				logging.warning("[GetResetNames] Service '{0}' not a referenced service.".format(ServID))
				continue
			#-------------------
			elif ServID.startswith("reset"):
#				Serv, ResetMapping, ResetIsOrtho=self.ReqServ[ServID]
#				ActualName=ResetMapping["reset"][0][0][1]
				for Formal, ActualCond in ResetMapping.items():
					if Formal in Serv.Params: continue
					ActualList, Cond, OtherDict=ActualCond
					ActualName=ActualList[0][1]
				if ActualName in self.Ports:
					if MappedName:
						ResetList.append(SharedName(Formal=Formal, Params=Serv.Params, ReqMap=ResetMapping)) 
#						ResetList.append('reset_'+ResetMapping["delay"][0][0][1])
					else: ResetList.append(ActualName)
				else:
#					print "[{0}]".format(self.Name), "Created reset: '{0}'".format('reset_'+ResetMapping["delay"][0][0][1])
					ResetList.append(SharedName(Formal=Formal, Params=Serv.Params, ReqMap=ResetMapping)) 
#					ResetList.append('reset_'+ResetMapping["delay"][0][0][1])
			#-------------------
#			Serv, ModMap, IsOrtho = self.ReqServ[ServID]
			Mod=Serv.GetModule()
			if Mod: ResetList+=Mod.GetResetNames(MappedName=True)
		ResetList=list(set(ResetList))
		return ResetList
	#---------------------------------------------------------------
	def GetStimuliNames(self):
		"""
		Return the list of stimuli names.
		"""
		return [P.Rename(N).AVAName() for N,P in self.GetExternalPorts().items() if P.Direction=="IN"]
#		ResetsClocks=self.GetClockNames()+self.GetResetNames()
#		AllPorts={}
#		AllPorts.update(self.Ports)
#		for Actual, FormalSig in self.OrthoPorts.items():
#			OName=FormalSig.OrthoName()
#			AllPorts[OName]=FormalSig
#		StimuliNames=[str(x.AVAName()) for x in [x for x in list(AllPorts.values()) if x.Direction=="IN"]]
#		StimuliNames=[x for x in StimuliNames if x not in ResetsClocks]
#		return StimuliNames
	#---------------------------------------------------------------
	def GetTraceNames(self):
		"""
		Return the list of Trace names.
		"""
		return [P.Rename(N).AVAName() for N,P in self.GetExternalPorts().items() if P.Direction=="OUT"]
#		AllPorts={}
#		AllPorts.update(self.Ports)
#		for Actual, FormalSig in self.OrthoPorts.items():
#			OName=FormalSig.OrthoName()
#			AllPorts[OName]=FormalSig
#		TraceNames=[str(x.AVAName()) for x in [x for x in list(AllPorts.values()) if x.Direction=="OUT"]]
#		return TraceNames
	#---------------------------------------------------------------
	def GetBidirNames(self):
		"""
		Return the list of bidirectionals names.
		"""
		return [P.Rename(N).AVAName() for N,P in self.GetExternalPorts().items() if P.Direction=="INOUT"]
#		AllPorts={}
#		AllPorts.update(self.Ports)
#		for Actual, FormalSig in self.OrthoPorts.items():
#			OName=FormalSig.OrthoName()
#			AllPorts[OName]=FormalSig
#		BidirNames=[str(x.AVAName()) for x in [x for x in list(AllPorts.values()) if x.Direction=="INOUT"]]
#		return BidirNames
	#---------------------------------------------------------------
	def GetDataPorts(self):
		"""
		return list of port without reset and clocks.
		"""
		DataPortDict={}
		# TODO : consider self.OrthoPorts
		for PName, P in self.Ports.items():
			if PName in self.GetClockNames() or PName in self.GetResetNames():
				continue
			else:
				DataPortDict[PName]=P
		return DataPortDict
	#---------------------------------------------------------------
	def GetExternalPorts(self, CalledServ=None):
		"""
		Return the list of clock names connected to service 'clock'.
		CalledServ is the service that this module provide.
		"""
		PortDict=collections.OrderedDict()
		
		ItfPorts=self.Ports.copy()
		ItfPorts.update(dict( (OP.OrthoName(), OP) for OP in list(self.OrthoPorts.values())))
		for ServID, (Serv, PortMapping, IsOrtho, Constraints) in self.ReqServ.items():
			#-------------------
#			Serv, ModMap, IsOrtho = self.ReqServ[ServID]
			if Serv is None: 
				logging.warning("[GetClockNames] Service '{0}' not a referenced service.".format(ServID))
				continue
			Mod=Serv.GetModule()
			if Mod: 
				PortDict.update(Mod.GetExternalPorts(CalledServ=Serv)) 
			#-------------------
			if ServID.startswith("FPGAPads"):
#				print("ServID:", ServID)
#				print("Module:", self.Name)
#				print("PortMapping:", PortMapping)
#				print("Ports:", [x for x in self.Ports])
#				print("ItfPorts:", [x for x in ItfPorts])
#				Serv, PortMapping, IsOrtho=self.ReqServ[ServID]
#				CalledServName=str(CalledServ.Alias)+"_" if CalledServ else ""
				PortDict.update({PortMapping[x][0][0][1]:ItfPorts[PortMapping[x][0][0][1]] for x in list(PortMapping.keys())})
		return PortDict
	#---------------------------------------------------------------
	def Characteristics(self):
		"""
		Return the number of clocks, stimuli, traces, bidirectionals of the module.
		"""
		NbClk   = len(self.GetClockNames())
		NbStim  = len(self.GetStimuliNames()+self.GetResetNames())
		NbTrace = len(self.GetTraceNames())
		NbBiDir = len(self.GetBidirNames())
		return NbClk, NbStim, NbTrace, NbBiDir
	#---------------------------------------------------------------
	def PropagateServDefaultParam(self, Serv):
		"""
		Set default value for each parameters/port from provided service.
		"""
		for PName, P in Serv.Params.items():
			Mapping=self.ProvidedServMap[Serv.Name]
			if PName in Mapping:
				MappedName=Mapping[PName]
				if MappedName in self.Params:
#					print(P.Name)
#					print(P.Value)
#					print(P._UsedParams.copy())
					V=P.GetValue()
					self.Params[MappedName].SetValue(V)
					self.Params[MappedName].SetDefault(V)
#		for PName, P in Serv.Ports.items():
#			Mapping=self.ProvidedServMap[Serv.Name]
#			if PName in Mapping:
#				MappedName=Mapping[PName]
#				if MappedName in self.Ports:
#					V=P.GetValue()
#					self.Ports[MappedName].SetValue(V)
#					self.Ports[MappedName].SetValue(V)
		
		return
	#---------------------------------------------------------------
	def GenSrc(self, Synthesizable=True, OutputDir="./Output", TestBench=False, IsTop=True, ProcessedServ={}, ModInstance=None, TBValues={}, TBClkCycles=1600, TBCycleLength=10, CommunicationService=None, Recursive=True, NewPkg=True, HwConstraints=None):
		"""
		Generate source files or copy sources to output directory.
		Return list of generated sources if success.
		"""
		#----Write xml file for module----
		if IsTop is False: OutputDir=os.path.join(OutputDir, self.Name)
		if not os.path.isdir(OutputDir): os.makedirs(OutputDir)
		
		self.XmlFilePath=self.DumpToFile(OutputPath=OutputDir)
		for SName, S in self.ProvidedServ.items():
			if S is None:
				logging.error("[{0}:GenSrc] No service associated with '{1}'.".format(self.Name, SName))
				continue
			S.XmlFilePath=S.DumpToFile(OutputPath=OutputDir)
			
		#---------------------------
		if Synthesizable: TYPE = "RTL"
		else: TYPE = "Behavioral"
		ArchName=TYPE
		self.IntSignals=collections.OrderedDict()
		self.Connections=collections.OrderedDict()
		
		if ModInstance is None:
			ModInstance=Instance(self.Name, self)
			
		if self.IsAbstract():
#			logging.warning("{0} :=> Abstract module".format(self))
#			logging.debug("[Module '{0}'] Abstract module : generate source.".format(self))
			ArchName = "RTL"
			# Build a top and Instantiate children
			# Define architecture
			Content=""
			Declarations=""
	
			# Declare all constants -----------------------------------------
			for BaseName, CDict in self.Const.items():
				for C in sorted(CDict.keys()):
					Declarations+=CDict[C].Declare(Constant=True)
			SubMod=None
			for ServID in sorted(self.ReqServ.keys()): # Service connection
				SubServ, SubModMap, IsOrtho, Constraints = self.ReqServ[ServID]
				if SubServ:	
					if SubServ.Name=="FPGAPads": continue
#					logging.debug("> Request service {0}.".format(SubServ.Name))
					# Propagate orthogonal signals upward through the hierarchy
					SubMod = SubServ.GetModule(Constraints=HwConstraints)
					if SubMod is None:
						Msg="[SysGen.Module.GenSrc] no module associated with service '{0}' in instances of {1} for constraints '{2}'.".format(SubServ.Name, self.Name, HwConstraints)
						logging.error(Msg)
						raise SyntheSysError(Msg)
					if not IsOrtho:  self.AddOrtho(SubServ, SubMod, SubModMap, Constraints, HwConstraints=HwConstraints)
					# Map Parameters
#					SubServ.PropagateModDefaultParam(self, SubModMap)
					for ParameterName in list(SubModMap.keys()): # For each mapped parameter
						if ParameterName in SubServ.Params: # if it's a service parameter
							# Change its value
							for Actual in SubModMap[ParameterName][0]: # Actual=[Instance, SignalName, Index]
								Val=str(Actual[1])#eval(str(Actual[1]), self.Vars.copy())
								if Val in self.Params:
									SubServ.Params[ParameterName].SetValue(self.Params[Val].GetDefaultValue())
					if SubMod is None: 
						logging.warning("Service {0} ignored due to absence of implementation module.".format(SubServ))
					else: 
						InstanceName=ServID.split('#')[-1]
						#-----------------------------
						INSTANCE=None
						if not (SubServ.Name in ProcessedServ):
							#-----------------------------
							if not SubServ.IsOrthogonal(): 
								INSTANCE=ModInstance.AddInstance(Name=InstanceName, Mod=SubMod)
							
							ProcessedServ[SubServ.Name]=INSTANCE
							#-----------------------------
							if Recursive is True:
								SubServSrc = SubServ.GenSrc(Synthesizable=Synthesizable, OutputDir=OutputDir, IsTop=False, HwConstraints=HwConstraints, ProcessedServ=ProcessedServ)
								self.AddSources(SubServSrc, IsDependency=True)
							
						else:
							#-----------------------------
							if not SubServ.IsOrthogonal(): 
								INSTANCE=ProcessedServ[SubServ.Name].Copy()
								INSTANCE.Name=InstanceName
								ModInstance.AddInstanceAsInstance(INSTANCE)
								self.AddSources(INSTANCE.Mod.Sources["RTL"], IsDependency=True)
						#-----------------------------
						# Add ports of orthogonal service to module port
						if SubServ.IsOrthogonal(): 
							OrthoPorts=[]
							for S in list(SubMod.Ports.values()):
								SCopy=S.Copy()
								SCopy.Name='_'.join([InstanceName, S.Name])
#								if SCopy.Direction=="IN" : SCopy.Direction="OUT"
#								elif SCopy.Direction=="OUT": SCopy.Direction="IN"
#								else: SCopy.Direction="INOUT"
								OrthoPorts.append(SCopy)
								
							ODict=collections.OrderedDict()
							for O in OrthoPorts:
								ODict[O.Name]=O
							self.OrthoPorts.update(ODict)
							
							continue
						self.OrthoPorts.update(SubMod.OrthoPorts)
						# Switch from Service mapping to Module Mapping
						SubServMap = SubMod.ProvidedServMap[SubServ.Name]
						# First map services
						PortDict, GenericDict, Cont, IntSignals = self.BuildMap(SubServ, SubModMap, SubMod, SubServMap, InstanceName)
						# Instantiate sub-modules
						Content+=HDL.Instantiate(
									InstanceName  = InstanceName, 
									Module        = SubMod.Name, 
									Architecture  = TYPE, 
									SignalDict    = PortDict, 
									GenericDict   = GenericDict, 
									Comment       = str(SubMod.Title)
									)
						Content+=Cont+'\n'+"-"*65
						
						self.IntSignals.update(IntSignals)
#						AvailableParam=dict( (str(k),str(v)) for k,v in GenericDict.items())
						
						# Replace submodule generic parameters by mapped top module parameter
						ConstMap={k.replace(k.split(':')[0], SubServMap[k.split(':')[0]]):v for k,v in SubModMap.items() if k.split(':')[0] in SubServMap}
						
						for IntSigName in sorted(IntSignals.keys()):
							if not (IntSigName in self.OrthoPorts):
								IntSignals[IntSigName].MapConstants(Mapping=ConstMap)
						#self.Vars.update(SubMod.Vars)
						
				else: 
					logging.warning("[Module.GenSrc] In module {0}, no service associated with requested {1}.".format(self, ServID))
				
			# Declare all internal signals-----------------------------------
			for IntSigName in sorted(self.IntSignals.keys()):
				if not (IntSigName in self.OrthoPorts):
					self.IntSignals[IntSigName].InitVal=""
					Declarations+=self.IntSignals[IntSigName].Declare(UnConstrained=False)
				
			TopPath=LibEditor.HDLModule(	
						OutputPath   = OutputDir, 
						Mod          = self, 
						Packages     = self.Dependencies["package"].keys(), 
						Libraries    = ["IEEE",], 
						Declarations = Declarations, 
						Content      = Content
						)
			self.AddSources([os.path.abspath(TopPath),], IsDependency=False)

			if IsTop is True and NewPkg is True:
				self.CollectPkg()
#				logging.info("{0} is Top => Generate package".format(self))
				Pkg, PkgPath=self.GenPackage(self.Name, OutputDir)
				if Pkg: #self.Sources["RTL"].insert(0, os.path.abspath(PkgPath))
					self.AddSources([os.path.abspath(PkgPath),], IsDependency=True)
			else: Pkg=None
				
		# Concrete, Sourced module------
		else: 
#			logging.warning("{0} :=> Concrete module".format(self))
			#-------------------------------------------------------------
			if IsTop is True: DepSources=[P for P in self.Dependencies["package"].values() if not (P is None)]
			else: DepSources=[]
			for Src in self.Sources["RTL"]+DepSources:#self.GetSources(Synthesizable):
				for SrcItem in glob.iglob(Src):
					NewSource=os.path.join(os.path.abspath(OutputDir), os.path.basename(SrcItem))
					if os.path.abspath(SrcItem)!=NewSource:
						shutil.copy(SrcItem, OutputDir)
						self.ReplaceSource(Src, NewSource, Synthesizable=True)
			#-------------------------------------------------------------
			for Src in self.GetConstraintSources():
				for SrcItem in glob.iglob(Src):
					NewSource=os.path.join(os.path.abspath(OutputDir), os.path.basename(SrcItem))
					if os.path.abspath(SrcItem)!=NewSource:
						shutil.copy(SrcItem, OutputDir)
						self.ReplaceConstraintSource(Src, NewSource)
			
			#-------------------------------------------------------------
			for SubServ, SubModMap, IsOrtho, Constraints in list(self.ReqServ.values()): # Service connection
				if SubServ:
					if SubServ.Name=="FPGAPads": continue
					SubMod = SubServ.GetModule(Constraints=HwConstraints)
					if SubMod: 
						self.AddOrtho(SubServ, SubMod, SubModMap, Constraints, HwConstraints=HwConstraints)
#						self.OrthoPorts.update(SubMod.OrthoPorts)
						if not SubServ.Name in ProcessedServ:
							if Recursive is True:
								SubServSrc=SubServ.GenSrc(Synthesizable=Synthesizable, OutputDir=OutputDir, IsTop=False, HwConstraints=HwConstraints, ProcessedServ=ProcessedServ)
								self.AddSources(SubServSrc, IsDependency=True)
						else:
							self.AddSources(SubMod.Sources["RTL"], IsDependency=True)
					else:
						Msg="[SysGen.Module.GenSrc] no module associated with service '{0}' in instances of {1} for following constraints:{2}.".format(SubServ.Name, self.Name, HwConstraints)
						logging.error(Msg)
						raise SyntheSysError(Msg)
			#-------------------------------------------------------------
			if IsTop is True: 
				# Generate package--------------
				self.CollectPkg()
				Pkg, PkgPath = self.GenPackage(self.Name, OutputDir)
				if Pkg: #self.Sources["RTL"].insert(0, os.path.abspath(PkgPath))
					self.AddSources([os.path.abspath(PkgPath),], IsDependency=True)
			else: Pkg=None
			
		# TESTBENCH GENERATION-------------	
		if TestBench: self.GenTB(Pkg, TYPE, OutputDir, TBValues=TBValues, NbCycles=TBClkCycles, CycleLength=TBCycleLength, CommunicationService=CommunicationService, ParamVars=self.Vars.copy())
		
		# SPECIFY GLOBAL TOP PACKAGE-------------	
		if IsTop is True and NewPkg is True:
			AlreadyModified=[]
			# Add use common package line to all sources (except TOP and verilog sources)
			AlreadyModified.append(self.Sources["RTL"][1])
			for SrcPath in self.Sources["RTL"][1:]:
				if not AlreadyModified.count(SrcPath) and SrcPath.endswith('.vhd'):
					AlreadyModified.append(SrcPath)
					with open(SrcPath,"r") as SrcFile:
						Code = SrcFile.read()
					with open(SrcPath,"w+") as SrcFile:
						SrcFile.write(HDL.Packages(["work."+Pkg,]))
						SrcFile.write('\n'+Code)
			if not Pkg in (self.Dependencies["package"]): self.Dependencies["package"]["work."+Pkg]=PkgPath
#			print("Src:\n", "\n".join(list(collections.OrderedDict.fromkeys(self.Sources["RTL"]))))
			return self.Sources["RTL"]#list(collections.OrderedDict.fromkeys())
			
			
#		print(self.Name, "=>", [os.path.basename(s) for s in self.Sources["RTL"]])
#		print("\n\nSET\n", list(set(self.Sources["RTL"])))
#		return self.Sources["RTL"]
		return self.Sources["RTL"]#list(collections.OrderedDict.fromkeys(self.Sources["RTL"])) # Remove duplicates and keep order
	#---------------------------------------------------------------
	def BuildMap(self, SubServ, SubModMap, SubMod, SubServMap, InstanceName):
		"""
		Instanciate a Service in this module for HDL deployement.
		Fill PortDict, GenericDict, declaration and content for interconnections.
		"""
		Connections=collections.OrderedDict() # Dictionary of connections to perform in content area
		# Sort Generics and ports
		GenericDict=collections.OrderedDict()
		PortDict=collections.OrderedDict()
		# Add orthogonal ports to normal ports mapping
		OrthoMap=collections.OrderedDict()
		OrthoPorts=collections.OrderedDict()
		IntSignals=collections.OrderedDict()
		
		if SubMod.IsAbstract():
			for Actual, FormalSig in SubMod.OrthoPorts.items():
				OrthoPorts[FormalSig.OrthoName()]=FormalSig
				if SubMod.IsAbstract():
					OName=FormalSig.OrthoName()
					OrthoMap[OName]=OName
				else:
					OrthoMap[Actual]=FormalSig.OrthoName()
			PortDict.update(OrthoMap)
		else:
			for PName, P in SubMod.Ports.items():
				if (PName not in SubModMap) and (PName in SubMod.OrthoPorts):
					PortDict[PName]=SubMod.OrthoPorts[PName].Name
#					Actuals=[(None,SName,None),]
#					ModuleMap.insert(0, [PName, (Actuals, True, {})])
						
		# Sort so as to begin by parameters before ports (to save generic values)
		ModuleMap=[]
#		InvertedSubServMap=dict( (k,v) for in SubServMap)
		for Formal, ActualCond in SubModMap.items():
			F=Formal.split(':')[0]
			if not (F in SubServMap):
				if F in SubMod.OrthoPorts:
					ModuleMap.append([Formal, ActualCond])
				else:
					logging.error("[Module '{0}'] No such formal signal '{1}' in {2} mapping.".format(self, F, SubServ.Name))
					logging.error(("SubServ:    {0}".format(SubServ)))
					logging.error(("SubServMap: {0}".format(SubServMap)))
					logging.error(("SubMod.OrthoPorts: {0}".format(list(SubMod.OrthoPorts.keys()))))
	#				logging.error(("SubModMap:    {0}".format(SubModMap)))
					sys.exit(1)
	#				input()
				continue
#			print "SubServMap:", SubServMap
#			print "SubMod.Params:", SubMod.Params
			if SubServMap[F] in SubMod.Params:
				ModuleMap.insert(0, [Formal, ActualCond])
			else:
				ModuleMap.append([Formal, ActualCond])
				
		#---------------START MAPPING--------------------------------------
		#-------------------------------------
		for Formal, ActualCond in ModuleMap:
			Actuals, Condition, Vars = ActualCond	
			FormalSigName=None
			IntermediateSignal=False 
			if Formal:
				# If formal is a slice: remember for signal link.
				SplitFormal = Formal.split(':')	
				if SplitFormal[0]=='': SplitFormal[0]=Formal
				if SplitFormal[0] in SubServMap:
					FormalSigName = SubServMap[SplitFormal[0]]
				elif SplitFormal[0] in OrthoPorts:
					FormalSigName = SplitFormal[0]
				else:
					# Service port not mapped in this module
#					FormalSigName=None
					FormalSigName = SplitFormal[0]
					logging.warning("[BuildMap:Module {0}] Service port '{1}' not mapped in this module".format(self, SplitFormal[0]))
				if len(SplitFormal)>1:
					IntermediateSignal=True 
					FormalIndex=SplitFormal[1]
				else: FormalIndex=None
				
					
			# For older version of python :
			ReverseServMap=collections.OrderedDict()
			for k,v in list(SubServMap.items()):
				ReverseServMap[v]=k
			
			if FormalSigName:
				# Create signal object for actual with formal format----------------
				if FormalSigName in SubMod.Ports: # Case: it's a port signal
					FormalSig=SubMod.Ports[FormalSigName]
				elif FormalSigName in SubMod.Params: # Case: it's a parameter signal
					FormalSig=SubMod.Params[FormalSigName]
					# Save formal name as used parameter in module (self)
					self.UsedParams.append(FormalSigName)
				elif FormalSigName in SubMod.OrthoPorts: # Case: it's a special case => force orthoport mapping using communication element user clock service.
					FormalSig=SubMod.OrthoPorts[FormalSigName]
				else:
					logging.error("Formal signal '{0}' not found in ports or parameters of '{1}'".format(FormalSigName, SubMod))
					logging.debug("SubMod.OrthoPorts:".format(list(SubMod.OrthoPorts.keys())))
					
					raise NameError("Formal signal '{0}' not found in ports or parameters of '{1}'".format(FormalSigName, SubMod))
				#---------------PROCESS THE ACTUAL EXPRESSION-----------------------
				CopyVars=SubMod.Vars.copy()
				CopyVars.update(self.Vars)
				CopyVars.update(Vars)
				
				def CheckCondition(Condition):
					if Condition is True: return True
					if Condition is None or Condition is False: return False
					elif Condition.Evaluate(CopyVars.copy()): return True
					else: return False
				if CheckCondition(Condition):
					ConcatList=[] # List of signals to concatenate
					for InstName, SigName, AIndex in Actuals:
						# Test for constant value
						try:    SVal=int(SigName)
						except: SVal=None
						# Get actual name-----------------------------
						if SVal is None: # actual is a signal name
							HDLActual=None
#							DecomposedActual = re.split('(\W)', SigName)
#							print("DecomposedActual=",DecomposedActual)
#							print("FormalSigName:", FormalSigName, "(Param="+str(FormalSigName in SubMod.Params)+")")
							if FormalSigName in SubMod.Params:# and len(DecomposedActual)>1:
								HDLActual=SubMod.Params[FormalSigName].HDLFormat(ParamVars=self.Vars)
								HDLActual.Name=SigName
								self.UsedParams.append(SigName)
								if not (AIndex is None): 
									HDLActual.SetIndex(AIndex)
								
							elif InstName==InstanceName or InstName=="" or InstName is None:
								# Instance specified belongs to this module
								if (SigName in self.Ports):
									ActualName='_'.join([InstanceName, SigName])
									HDLActual=self.Ports[SigName].HDLFormat(ParamVars=self.Vars)
									if not (AIndex is None): 
										HDLActual.SetIndex(AIndex)
								elif (SigName in self.Params):
									logging.error("[BuildMap] Formal signal '{0}' is connected to parameter '{1}'".format(FormalSigName, SigName))
									exit(1)
#									ActualName=SigName
#									HDLActual=self.Params[SigName].HDLFormat(ParamVars=self.Vars)
#									self.UsedParams.append(SigName)
#									if not (AIndex is None): HDLActual.SetIndex(AIndex)
								elif (SigName in OrthoPorts):
									ActualName=SigName
									HDLActual=OrthoPorts[SigName].HDLFormat(ParamVars=self.Vars)
									if not (AIndex is None): HDLActual.SetIndex(AIndex)
								else:
#									if SigName in SubMod.Params: 
#										logging.error("[BuildMap] Connection of parameters '{0}' between instances (one of them is '{1}'). This will fail to compile.".format(SigName, SubMod))
#										exit(1)
#										ActualName=SigName
#									else: 
									ActualName='_'.join([InstanceName, SigName])
									HDLActual=GetInternalSigFrom(
												Sig      = FormalSig, 
												FIndex   = FormalIndex, 
												AIndex   = AIndex, 
												WithName = ActualName,
												Mod      = SubMod,
												IntSigs  = IntSignals
												)
							else:
								# If actual is a Port/Parameter of another instanciated module
								ActualName='_'.join([InstName, SigName])
								if SigName in SubMod.Params: 
									logging.error("[BuildMap] Connection of parameters '{0}' between instances (one of them is '{1}'). This will fail to compile.".format(SigName, SubMod))
									exit(1)
								
								# Case: it's a parameter signal
								if SigName in self.Params:
									FormalSig=self.Params[SigName]
								HDLActual=GetInternalSigFrom(
											Sig      = FormalSig, 
											FIndex   = FormalIndex, 
											AIndex   = AIndex, 
											WithName = ActualName,
											Mod      = SubMod,
											IntSigs  = {}
											)
							ConcatList.append(HDLActual)
							# Build a signal resulting from concatenation of indexed signals
#							HDLActual=reduce(lambda x,y: x+y, ConcatList)

						else:  # Actual is a constant number
							if FormalSigName in SubMod.Ports:
								# Case: it's a port signal
								Port=SubMod.Ports[FormalSigName]
								ConcatList.append(Port.HDLFormat(CopyVars).GetValue(SVal, WriteBits=True))
							else:
								# Case: it's a parameter signal
								Param=SubMod.Params[FormalSigName]
								ConcatList.append(Param.HDLFormat(CopyVars).GetValue(SVal, WriteBits=True))	
								# Build a signal resulting from concatenation of indexed signals
					if len(ConcatList)>1: IntermediateSignal=True 
					HDLActual=reduce(lambda x,y: x+y, ConcatList)
				else: # if condition is not realized actual is default value, else
					# Fetch default value of formal for actual
					continue
#					if FormalSigName in SubMod.Ports:
#						HDLActual=SubMod.Ports[FormalSigName].HDLFormat(SubMod.Vars.copy())#.GetValue()
#					elif FormalSigName in SubMod.Params:
#						HDLActual=SubMod.Params[FormalSigName].HDLFormat(SubMod.Vars.copy())#.GetValue()
				#---------------PROCESS THE FORMAL EXPRESSION-----------------------
				if IntermediateSignal is False: # Formal signal is not indexed: do not create intermediate signal
					# Add as portmap if 'formal' is a sub module port
					if FormalSigName in SubMod.Ports:
						PortDict[FormalSigName]=HDLActual
					# Add as generic if 'formal' is a sub module parameter
					elif FormalSigName in SubMod.Params:
						GenericDict[FormalSigName]=HDLActual
					elif FormalSigName in SubMod.OrthoPorts: # Case: it's a special case direct module to module mapping (in clocking top wrappers)
						PortDict[FormalSigName]=HDLActual
					else:
						logging.error("No such formal signal {0} mapped to submodule {1}".format(repr(FormalSigName), SubMod))
						logging.error("Available ports:")
						for P in SubMod.Ports: logging.error("\t> {0}".format(repr(P)))
						logging.error("Available parameters:")
						for P in SubMod.Params: logging.error("\t> {0}".format(repr(P)))
						sys.exit(1)	
				else:
					InterSigName=InstanceName+'_'+ReverseServMap[FormalSigName]
					# Fill Connections list
					InterSig=IndirectConnection(InterSigName, FormalIndex, FormalSig, HDLActual, Connections, IntSigs=IntSignals, Vars=CopyVars)
					# Add as port map (if 'formal' is a sub module port)
					if FormalSigName in SubMod.Ports:
						PortDict[FormalSigName]=InterSig
					# or as generic map (if 'formal' is a sub module parameter)
					elif FormalSigName in SubMod.Params:
						GenericDict[FormalSigName]=InterSig
					elif FormalSigName in OrthoPorts: #  Case: it's a special case => force orthoport mapping using communication element user clock service.
						PortDict[FormalSigName]=InterSig
					else:
						logging.error("No such formal {1} signal mapped to submodule {0}".format(SubMod, FormalSigName))
			else:
				pass # IO connections
		
		Content="" # Content of Architecture
		
		# Now connect signals---------------------------------------------------------------
		for FormalSig in sorted(Connections.keys()):
			# For each signal to assign value get indexed dictionnary
			ActualSignals=Connections[FormalSig] # ActualSignals={0:S0, 1:S1, 3:S3...} or a HDLSignal
			Zeros=self.GetMissing(ActualSignals, FormalSig, SubMod.Vars.copy()) # Complete missing indexes

			# either concatenate signals-------		
			if isinstance(ActualSignals, dict):
				FullConnections=ActualSignals.copy()
				FullConnections.update(Zeros) # FullConnections = Signal Connections + Zeros connections
				for Index in sorted(FullConnections.keys()):
					ActualSig=FullConnections[Index]
					if ActualSig.Name!=FormalSig.Name: # Do not connect signal with itself
						FormalSig.SetIndex(Index)
						if Index not in Zeros:
							if FormalSig.Direction.upper()=="IN":
								Content+=ActualSig.Connect(FormalSig, False)
							else:
								Content+=FormalSig.Connect(ActualSig, False)
						FormalSig.SetIndex(None)
						
			# or only one signal-------
			else:
				if FormalSig.Direction.upper()=="OUT":
					Content+=ActualSignals.Connect(FormalSig, False)
				else:
					Content+=FormalSig.Connect(ActualSignals, False)
		self.Connections.update(Connections)

		return PortDict, GenericDict, Content, IntSignals
	#---------------------------------------------------------------
	def GenTB(self, Pkg, TYPE, OutputDir, TBValues={}, NbCycles=1600, CycleLength=10, CommunicationService=None, ParamVars={}):
		"""
		Generate TestBench files 'module_tb.vhd' and 'module_tb_io.txt'.
		"""
		logging.debug("Create testbench for design '{0}'".format(self.Name))
		
		V={k:v.GetValue() for k,v in self.Params.items()}
		for P in list(self.Ports.values())+list(self.OrthoPorts.values()):
			P.UpdateVars(V)
		
		# FILE:'module_tb.vhd'-------------------------------------
		TB_FilePath = os.path.join(OutputDir, "{0}_tb.vhd".format(self.Name))
		self.TBEntity="{0}_tb".format(self.Name)
		self.TBSource=TB_FilePath
		self.Sources["Behavioral"].append(TB_FilePath)
		with open(TB_FilePath, 'w+') as TB_File:
			# Write TB VHDL Header
			TB_File.write(HDL.Header("{0}_tb".format(self.Name), 
						"Generate {0}'s stimuli".format(self.Name), 
						"Perform testbench", 
						"Use TextIO module to get stimuli.", 
						"no known issues", 
						"No speed information", 
						"No area information", 
						"Xilinx isim", 
						self.Version))
			# Write TB Library call
			TB_File.write(HDL.Libraries(["IEEE",]))
			TB_File.write(HDL.Packages(["IEEE.std_logic_1164",]))
#			TB_File.write(HDL.Packages(["IEEE.std_logic_signed",]))
#			TB_File.write(HDL.Packages(["IEEE.std_logic_arith",]))
			TB_File.write(HDL.Packages(["std.textio",]))
			if Pkg: TB_File.write(HDL.Packages(["work."+Pkg,]))
			# Write TB entity---------------------------------------------------
			Generics=[]
			Ports=[]
			TB_File.write(HDL.Entity("{0}_tb".format(self.Name), Generics, Ports, "{0}'s testbench module".format(self.Name)))
			# Define TB architecture--------------------------------------------
			Content="\n"
			
			Params  = [P for N,P in self.Params.items() if N in self.UsedParams]
			Signals = list(self.Ports.values())		
			for OPName, OP in self.OrthoPorts.items():
				if not OPName in self.Ports:
					Signals.append(OP)
			Signals = RemoveDuplicated(Signals)
			Aliases = []
			PortDict=collections.OrderedDict()
			GenericDict=collections.OrderedDict()
			for Par in Params : 
				GenericDict[Par.Name]=Par.HDLFormat(ParamVars.copy())
				
			for Sig in Signals: 
#				if Sig.Name in self.OrthoPorts:
				PortDict[Sig.OrthoName()]=Sig.HDLFormat(ParamVars.copy())
#				else:
#					PortDict[Sig.Name]=Sig.HDLFormat(ParamVars.copy())
			self.TB_DUT='DUT_'+self.Name
			Content+=HDL.Instantiate(self.TB_DUT, self.Name, TYPE, PortDict, GenericDict, Comment=str("Instantiate DUT module"))# Instantiate DUT module

			Declarations="\n"
			Stim = Signal("Stimuli", Type="logic", Size=99999)
			
			for P in Params : 
				Declarations+=P.HDLFormat(ParamVars.copy()).Declare(Constant=True)
			Declarations+='\n'
			CurIdx=0
			for S in Signals : 
				ParamVars.update(S.GetUsedParam())
				if S.Direction.upper()=="OUT":
					Declarations+=S.HDLFormat(ParamVars.copy()).Declare()
				elif S.Type.lower()=="logic":
					# Declare alias
					Size = S.FullSize if S.FullSize!=None else S.Size
					EndIdx=eval(str(Size)+"-1", ParamVars)+CurIdx
					Declarations+=S.HDLFormat(ParamVars.copy()).AliasOf(Stim.HDLFormat(ParamVars.copy())[EndIdx:CurIdx])
					Aliases.append(S)
					CurIdx+=eval(Size, ParamVars)
				elif S.Type.lower()=="numeric":
					Declarations+=S.HDLFormat(ParamVars.copy()).Declare()
					# Declare alias
					S_bits=S.Copy()
					S_bits.Name="TO_INTEGER({0})".format(S.Name+"_bits")
					Content+=S.HDLFormat(ParamVars.copy()).Connect(S_bits.HDLFormat(ParamVars.copy()))
					S_bits.Name=S.Name+"_bits"
					S_bits.Type="logic"
					
					if S.Size=="": 
						logging.warning("Size of signal '{0}' undefined.".format(S))
						S.Size=1
					Size = S.FullSize if S.FullSize!=None and S.FullSize!="" else S.Size
					if Size is None: 
						logging.error("Signal '{0}' don't have a predefined size: aborted.'".format(S))
						raise "Size error"
					EndIdx=eval(str(Size), ParamVars)+CurIdx
					Declarations+=S_bits.HDLFormat(ParamVars.copy()).AliasOf(Stim.HDLFormat(ParamVars.copy())[CurIdx:EndIdx])
					Aliases.append(S_bits)
					CurIdx+=eval(S_bits.FullSize, ParamVars)
				else:
					# Declare alias
					S.ComputeType()
					Declarations+=S.HDLFormat(ParamVars.copy()).Declare()
					S_bits=S.Copy()
					S_bits.TypeImport=None
					#logging.debug("ParamVars={0}".format(ParamVars))
					S_bits.Size=eval(str(S.Size)+'*'+S.Type.split('*')[0], ParamVars)
					S_bits.FullSize=S_bits.Size
					S_bits.Type="logic"
					S_bits.Name+="_bits"
					S_bits2=S_bits.Copy()
					S_bits2.Name+="_link"
					S_bits2_bis=S_bits2.Copy()
					S_bits2_bis.Name+="((i+1)*{0}-1 downto i*{0})".format(S.Type.split('*')[0])
					Content+='\n'+HDL.For(
							Name="ArrayToSig_{0}".format(S.Name), 
							Var='i', 
							Start=0, 
							Stop=str(S.FullSize)+"-1", 
							Content=S.HDLFormat(ParamVars.copy())['i'].Connect(S_bits2_bis.HDLFormat(ParamVars.copy())), 
							Comments="TB array to signal conversion")
					Declarations+=S_bits.HDLFormat(ParamVars.copy()).AliasOf(Stim.HDLFormat(ParamVars.copy())[CurIdx:S_bits.Size+CurIdx])
					HDL_S_bits2=S_bits2.HDLFormat(ParamVars.copy())
					Declarations+=HDL_S_bits2.Declare()
					Content+='\n'+S_bits2.HDLFormat(ParamVars.copy()).Connect(S_bits.HDLFormat(ParamVars.copy()))
					Aliases.append(S_bits)
					CurIdx+=S_bits.Size

			Stim.Size=CurIdx
			Stim.FullSize=CurIdx	
			StimSize = Signal("NbStimuli", Type="numeric", Default=CurIdx)
			Declarations=StimSize.HDLFormat(ParamVars.copy()).Declare(Constant=True)+Declarations
			Declarations=Stim.HDLFormat(ParamVars.copy()).Declare()+Declarations
			Content+=HDL.GetTBProcess(self.Name)
			TB_File.write(HDL.Architecture("TestIO_TB", "{0}_tb".format(self.Name), Declarations, Content, "Use TextIO module to get stimuli."))
		
#		logging.debug("Create stimValues.txt file.")
		# 'module_stimValues.txt'-------------------------------------
		IO_FilePath = os.path.join(OutputDir, 'stimValues.txt')
		self.TBDependencies.append(IO_FilePath)
		Aliases.reverse()
		Aliases_names = [str(x) for x in Aliases]
		with open(IO_FilePath, 'w+') as IO_File:
			# Write header of textIO file
			IO_File.write("# Test vectors for {0} ports\n".format(self.Name))
			IO_File.write("# 0 means force 0\n")
			IO_File.write("# 1 means force 1\n")
			IO_File.write("# L means expect 0\n")
			IO_File.write("# H means expect 1\n")
			IO_File.write("# X means don't care\n")
			IO_File.write("#"*50+'\n')
			NTemplates=[]
			Names=[]
			for i, Alias in enumerate(Aliases):
				NTemplates.append("{0:"+str(eval(str(Alias.FullSize), ParamVars))+"}")
				Names.append(NTemplates[-1].format(Aliases_names[i]))
			IO_File.write("#Time   "+(' '*4).join(Names))
			# Create template for line formating
			Template=""
			for n, S in enumerate(Aliases):	
				SSize = eval(str(S.FullSize), ParamVars)
				Template+="{"+"{0}:0".format(n+1)+str(SSize)+"b}"+' '*4
				if len(S.Name)>SSize: Template+=" "*(len(str(S))-SSize)
			Template='\n'+"{0:3}"+" "*5+Template
			# Write every stimuli line of textIO file
			
			# Clock stimuli------------
			ClockStim=collections.OrderedDict()
			ClockNames=self.GetClockNames()
			for C in ClockNames:
				ClockStim[C]=0
			#--------------------------
			
			# Reset stimuli------------
			ResetStim=collections.OrderedDict()
			ResetNames=self.GetResetNames()
			for R in ResetNames:
				ResetStim[R]=1
			#--------------------------
			# Time parameters
			TimeStep=int(CycleLength/2)
			MaxTime=NbCycles*TimeStep*2
			ResetClockCycles=32
			#--------------------------
			# RESET TIME
			TBValues_Renamed={}
			for Name, Values in TBValues.items():
#				print("Name:",Name)
				Values=[0 for i in range(ResetClockCycles+4)]+Values # insert zeros 
#				print("Zero+Values:",Values)
				TBValues_Renamed[str(CommunicationService.Alias)+"_"+Name]=Values
			RisingEdge=True
			OldValues=[]
			for t in range(0, MaxTime, TimeStep):
				if 0 in list(ClockStim.values()): RisingEdge=True # Current clock is low next is rising edge
				else: RisingEdge=False
				Aliases_val=[t,]
				for n, S in enumerate(Aliases):	
					SName=str(S)
					FullSize=eval(str(S.FullSize), ParamVars)
					if SName in ClockNames:
						Aliases_val.append(ClockStim[SName])
						ClockStim[SName]=0 if ClockStim[SName]==1 else 1
					elif SName in ResetNames:
						Aliases_val.append(ResetStim[SName])
						if t>ResetClockCycles:
							ResetStim[SName]=0
					else:
#						try: 
						if 1 in list(ResetStim.values()):
							Aliases_val.append(0)
						else:
							if RisingEdge is True:
								Value=OldValues[n+1]
							else: 
								AliasName=str(S)
								if AliasName in TBValues_Renamed:
									if len(TBValues_Renamed[AliasName])>0:
										Value=int(TBValues_Renamed[AliasName].pop(0))
									else:
										Value=0
								else:
									if OldValues[n+1]==0:
										Value=1
									else:
										Value=0
#								print(">>>>",Value)
							Aliases_val.append(Value)
#						except: 
#							MaxVal = math.pow(2, FullSize)-1
#							Aliases_val.append(random.randrange(0, MaxVal+1))
#							Aliases_val.append(0)	
				OldValues=Aliases_val[:]			
				IO_File.write(Template.format(*Aliases_val))
		return 
	#---------------------------------------------------------------
	def AddOrtho(self, SubServ, SubMod, ReqMap, Constraints, HwConstraints):
		"""
		Propagate orthogonal signals upward through the hierarchy
		"""
#		if self.Name.startswith("PCIe"): 
		if SubServ.IsOrthogonal():
#			if input().upper()=="R":
#				raise TypeError
			for Formal, ActuaData in ReqMap.items():
				ActualList, Cond, IdxDict = ActuaData
				InstName, SigName, Index  = ActualList[0] # TODO Maybe use condition
				
				if Formal in SubServ.Params: continue
				# create signal for ortho port 
				if not (SigName in self.Ports): logging.error("No such port '{0}' in module {1} ports ({2})".format(SigName, self.Name, [x for x in self.Ports])); sys.exit(1)
				
				P=self.Ports[SigName]
				Type, Identifier = SubServ.Name, Constraints
				
				if Identifier is None: 
					P.Constraints = (Type, None, Formal)
				else:
					Identifier=Identifier.lower()
					P.Constraints = (Type, Identifier, Formal)
					if Identifier!="ignore": 
						continue
				Port = P.Copy()
				if SubServ.Shared: Port.Name=SharedName(Formal, SubServ.Params, ReqMap)
				self.OrthoPorts[SigName]=Port
#					print("Add ortho:", Formal, "=>", InstName, SigName, Index)
#				else:
#					print("skip", Formal, "=>", InstName, SigName, Index)
		else:
#			if len(SubMod.OrthoPorts)==0:
#			if self.Name.startswith("Shared"):
#				print("********")
#				print("Sub module {0} do not has any orthoports".format(SubMod.Name))	
			for ServID in sorted(SubMod.ReqServ.keys()): # Service connection
				SubS, RMap, IsOrtho, Constraints = SubMod.ReqServ[ServID]
				SubM = SubS.GetModule(Constraints=HwConstraints)
#				if SubS.Name=="FPGAPads": continue
				if SubM is None:
					Msg="[SysGen.Module.AddOrtho] no module associated with service '{0}' in instances of {1} for following constraints:{2}.".format(SubS.Name, SubMod.Name, HwConstraints)
					logging.error(Msg)
					raise SyntheSysError(Msg)
#				if len(SubMod.OrthoPorts)==0:
#				if self.Name.startswith("Shared"):
#					print("------\nSubMod:", SubMod.Name)
#					print("SubM:", SubM)
				SubMod.AddOrtho(SubS, SubM, RMap, Constraints, HwConstraints)
#				if self.Name.startswith("Shared"):
#					print("New ortho:", [P for P in SubMod.OrthoPorts.keys()])
#			else:
#				if self.Name.startswith("Shared"):
#					print("********\n", SubMod.Name, "Already has orthoports", [P for P in SubMod.OrthoPorts.keys()])
#			if self.Name.startswith("Shared"):
#				input()
					
#			self.OrthoPorts.update(SubMod.OrthoPorts)
#			print("self.Name:", self.Name)
#			print("SubMod.Name:", SubMod.Name)
			for ActualPName, FormalP in SubMod.OrthoPorts.items():
#				if self.Name.startswith("TestNode"):
#					print("Add ortho:", FormalP, '('+str(ActualPName)+')')
#					input()
				self.OrthoPorts[FormalP.Name]=FormalP
#			if SubMod.Name.startswith("PCIe"): input()
		return 
	#---------------------------------------------------------------
	def GetMissing(self, Connections, Sig, ParamVars={}):
		"""
		Return a dictionary for connection to default of signals missing in Connections.
		Connections={Index0: ActualSig0, Index1: ActualSig1 (...) }
			or 
		Connections=<Signal>
		"""
		if isinstance(Connections, dict): 
			Zeros={}
			for i in range(eval(str(Sig.Size), ParamVars)):
				if not list(Connections.keys()).count(i):
					Zero=Sig.Copy()
					Zero.SetIndex(i)
					Zeros[i]=Zero
			return Zeros
		else:
			return {}
	#---------------------------------------------------------------
	def CollectPkg(self):
		"""
		Update PkgObject package dictionary with this package.
		"""
		for Child in [x[0] for x in list(self.ReqServ.values())]:#+self.Params.values()+self.Ports.values()+self.IntSignals.values():
			if Child!=None:
				Child.CollectPkg()
				PackageBuilder.CollectPkg(self, Child)
				self.PkgVars.update(Child.Vars.copy())
				
		for SName, S in self.Ports.items():
			self.Package["TypeImport"].update(S.GetUsedTypes())
		for SName, S in self.Params.items():
			self.Package["TypeImport"].update(S.GetUsedTypes())
			
		for SubSize, SubType, Pkg, UsedConst in list(self.Package["TypeImport"].values()):
			for U in UsedConst:
				if U in self.Params:
					self.Package["Constants"][U]=self.Params[U].HDLFormat()
	#---------------------------------------------------------------
	def DependencyPkg(self, TypeImport):
		"""
		Add dependency package to empty package list. 
		They will be declared empty in top package. 
		The top package declare all type/constants.
		This will prevent error when calling old packages.
		"""
		if TypeImport!=None:
			PkgType=TypeImport.split('.')
			if len(PkgType)>1:
				Pkg, NewType = PkgType
				self.Package["EmptyPkg"].append(Pkg)
#			else:
#				logging.debug("[{0}] TypeImport format '{1}' don't specify a package source.".format(self,TypeImport))
	#---------------------------------------------------------------
	def AddXMLReqServ(self, Serv, InstanceName, Mapping=None):
		"""
		Fetch service in XML library and return a XML etree
		object of required service child.
		"""
		# Test inputs ---------------------------------------------------
		if Serv is None: 
			logging.error("[{0}] AddXMLReqServ : No service specified.".format(self)) 
			return None
		
		# Add required service to XML spec ------------------------------
		XMLServices = etree.SubElement(self.XMLElmt, "services")
		ReqElmt = etree.SubElement( XMLServices, "required",  
						 name    = Serv.Name, 
						 type    = Serv.Type,
						 version = Serv.Version,
						 alias   = InstanceName)
		if not (Mapping is None):
			for Formal, ActualCond in Mapping.items():
				ActualList, ACond, AVars = ActualCond
				InstName, SigName, Index = ActualList[0]
				ActualName=SigName if (InstName is None) or (InstName=="") else ".".join( (InstName,SigName) ) 
				if not Index is None: ActualName+=":{0}".format(Index)
				MapElmt = etree.SubElement(ReqElmt, "map", formal=Formal, actual=ActualName)
			self.AddReqServ(Serv.Name, Serv.Type, Serv.Version, Mapping=Mapping, UniqueName=InstanceName, Serv=Serv)
		else:
			self.AddReqServ(Serv.Name, Serv.Type, Serv.Version, Mapping={}, UniqueName=InstanceName, Serv=Serv)
		return XMLServices
#		return XMLServices
#	#---------------------------------------------------------------
#	def MapServParam(self, Serv, ParamName, Param):
#		"""
#		Map a parameter for service Serv to value of 'Param'.
#		"""	
#		logging.info("Set parameter '{0}' of service '{1}' to value '{2}'".format(ParamName, Serv, Param))		
#		# Find XML element for the service -------------------------------
#		for XMLServ in self.XMLElmt.iterchildren("services"):
#			for XMLReq in XMLServ.iterchildren("required"):
#				if Serv.Alias == XMLReq.attrib['alias']:
#					if isinstance(Param, Signal):
#						MAP = etree.SubElement(XMLReq, "map", formal=ParamName, actual=Param.Name)
#					else:
#						MAP = etree.SubElement(XMLReq, "map", formal=ParamName, actual=str(Param))
#					break
#		return True
	#---------------------------------------------------------------
	def Connect(self, Interface1, Interface2):
		"""
		Map each signal of the first interface to a signal of the other interface.
		Respect the XML format of YANGO (Service.signal).
		"""
#		logging.debug("[{0}] Connect '{1}' to '{2}'.".format(self, Interface1, Interface2))
		# Test inputs -----------------------------------------------------
		if Interface1==None or Interface2==None:
			logging.error("[[0]] Nothing to connect.".format(self)) 
			return False
		elif isinstance(Interface1, list):
			if isinstance(Interface1, list): logging.error("Multiple interface connection: not supported.")
			else:logging.error("Multiple interface connection: not supported.")
			return True
		elif isinstance(Interface1, list):
			if isinstance(Interface1, list):logging.error("Multiple interface connection: not supported.")
			else:logging.error("Multiple interface connection: not supported.")
			return True
		
		
		# Test compatibility ----------------------------------------------
		if not Interface1.IsCompatibleWith(Interface2):
			logging.error("[{0}] Interface '{1}' incompatible with interface '{2}'.".format(self, Interface1, Interface2))
			return False
			
		# Find XML element for each service -------------------------------
		for XMLServ in self.XMLElmt.iterchildren("services"):
			for XMLReq in XMLServ.iterchildren("required"):
				if   XMLReq.attrib["alias"]==Interface1.Service.Alias: 
					Interface1.Connect(Interface2, XMLReq, Ref=False)
				elif XMLReq.attrib["alias"]==Interface2.Service.Alias: 
					Interface2.Connect(Interface1, XMLReq, Ref=True)
						
		return True
	#---------------------------------------------------------------
	def MapSubServices(self, Services, Mappings):
		"""
		Instanciate and connect the services RefServ with Services.
		Respect the XML format of YANGO.
		"""
		if len(Services)>len(Mappings):
			logging.error("[MapSubServices] Unable to map services ({0}) because not enough mapping ({1}) specified.".format(len(Services), len(Mappings)))
			logging.error("Mappings:"+str(Mappings[0]))
#			raise TypeError
			sys.exit(1)

		
		for i, Serv in enumerate(Services):
			Mod=Serv.GetModule()
			ServMapping=collections.OrderedDict()
		
			#---------------------
			MappedSigs=collections.OrderedDict()
			for IndexedName, Map in Mappings[i].items():
				MappedSigs[IndexedName]=IndexedName.split(':')[0]
			#---------------------
			ResetNames=Mod.GetResetNames(MappedName=False)
			ClockNames=Mod.GetClockNames(MappedName=False)
			ImplicitSignals=ResetNames+ClockNames
			
			MappedSigNames=list(MappedSigs.values())

			InvertedOffMap=dict( (v,k) for k,v in Mod.ProvidedServMap[Serv.Name].items())
#			ServUsedParam=map(lambda x: InvertedOffMap[x], Mod.GetUsedParam())
#			for PName in Mod.GetUsedParam():
#				if PName in MappedSigNames: continue
#				if not PName in InvertedOffMap: continue
#				FormalName=InvertedOffMap[PName]
#				ServMapping[FormalName]=([["", PName, None],], True, Mod.Vars)
##				print("[{0}] {1}> Param '{2}'=>'{3}'".format(self.Name, Serv.Name, FormalName, PName))
##				input()
##				self.UsedParams.append(PName)
#				if not PName in self.Params:
#					self.Params[PName]=Mod.Params[PName] # Add parameter to top module parameters
#			print("InvertedOffMap:", '\n'.join(["{0}=>{1}".format(x,y) for x,y in InvertedOffMap.items()]))
			for PName, P in Mod.Ports.items():
#				if Mod.IsAbstract():
				if PName in ImplicitSignals: continue
				if PName in MappedSigNames: continue
				if not PName in InvertedOffMap:  
#					if PName in Mod.GetClockNames(): continue
					logging.warning("[{4}] Port signal '{0}' of instance module '{1}' (service '{2}') not mapped to service, and not clock or reset ({3})".format(PName, Mod.Name, Serv.Name, ImplicitSignals, self))
#					print("Mod.ReqServ:", Mod.ReqServ)
#					print("ImplicitSignals:", ImplicitSignals)
#					raise TypeError
					continue
				FormalName=InvertedOffMap[PName]
				
				if FormalName in Mod.GetExternalPorts():
					pass
				else:
					ServMapping[FormalName]=([[Serv.Alias, PName, None],], True, Mod.Vars)
					
			#---------------------
			for IndexedName, Map in Mappings[i].items():
				ServMapping[IndexedName]=Mappings[i][IndexedName]#([[InstanceName, SigName, Sig.Index] for InstanceName, SigName in Mapping[PName]], True, P.GetUsedParam())
			
			#---------------------
			XMLServ=self.AddXMLReqServ(Serv, InstanceName=Serv.Alias, Mapping=ServMapping)
		return True
	#---------------------------------------------------------------
	def SpreadUpward(self, ModInterface, Prefix=""):
		"""
		Link interface to port to spread signal upward.
		Respect the XML format of YANGO.
		"""
#		logging.debug("[{0}] Spread '{1}' upward.".format(self, ModInterface))
		# Test inputs -----------------------------------------------------
		if ModInterface==None:
			logging.error("[[0]] Nothing to spread upward.".format(self)) 
			return False
			
		IntSignals = None
		# Find XML element for each required service ----------------------
		for XMLServ in self.XMLElmt.iterchildren("services"):
			for XMLReq in XMLServ.iterchildren("required"):
				if XMLReq.attrib["alias"]==ModInterface.Service.Alias: 
					IntSignals = ModInterface.Connect(None, XMLReq, Ref=True)
		if IntSignals==None:
			logging.error("Cannot find XML element for required service '{0}'.".format(ModInterface.Service.Alias))
			return False
			
		for Port in IntSignals:
			if Port.Type.lower().find("std_logic")!=-1: TYPE="logic"
			elif Port.Type.lower().find("integer")!=-1: TYPE="numeric"
			elif Port.Type.lower().find("natural")!=-1: TYPE="numeric"
			else: TYPE=Port.Type
			if Port.Direction=="IN":
				etree.SubElement(self.XMLElmt, 
						"input", 
						name=Prefix+Port.Name, 
						size=str(eval(str(Port.Size), ModInterface.Service.Vars)), # Don't forget to spread also generic values !!!
						type=TYPE, 
						default="") 
			else:
				etree.SubElement(self.XMLElmt, 
						"output", 
						name=Prefix+Port.Name, 
						size=str(eval(str(Port.Size), ModInterface.Service.Vars)), # Don't forget to spread also generic values !!!
						type=TYPE, 
						default="") 
			
		return True
	#---------------------------------------------------------------
	def WrapForClocking(self, HwModel, ClockManagerDict, Library):
		"""
		Generate a wrapper with clock management.
		"""
		WrapperName=self.Name+"_{0}".format(HwModel.Name)
		Mapping, StimuliList, TracesList, ClocksList, ResetList = DefaultMapping(self)
		
		Vars={}
		Mapping=collections.OrderedDict()
		for PName in self.Params:
			Mapping[PName]=([[None, PName, None],], True, Vars)
		for PName in self.Ports:
			Mapping[PName]=([[None, PName, None],], True, Vars)
		if self.IsAbstract():
			for PName, P in self.OrthoPorts.items():
				Mapping[P.Name]=([[None, P.Name, None],], True, Vars)
		Infos={
			"Name"     : self.Name,
			"Type"     : "",
			"Version"  : "",
			"Category" : "",
		}
		ModServ = LibEditor.ProvidedServiceXml(self, Interfaces=[], Infos=Infos, OutputPath=None)
		#---------------------------------
		#---------------------------------
		# Create a new module 
		Infos={
			"Name"   : WrapperName,
			"Version": "", # TODO get current time
			"Title"  : "{0} wrapper for {1}.".format(HwModel.Name, self.Name),
			"Purpose": "Add clock management for {1} instanciation on {0}.".format(HwModel.Name, self.Name),
			"Desc"   : "",
			"Tool"   : "",
			"Area"   : "",
			"Speed"  : "",
			"Issues" : "",
		}
		# Spread ports upward and replace old by new ports----------------------
		Mappings=[Mapping,]
		NewServices=[ModServ,]
#		for PName, P in self.Ports.items():
#			print("Port:", P.Name)
#		input()
		NewPorts={P.Name: P for PName, P in self.Ports.items()}
#		for PName, P in self.OrthoPorts.items():
#			print("OPort:", P.Name, '({0})'.format(PName))
#		input()
		if self.IsAbstract():
			NewPorts.update({P.Name: P for PName, P in self.OrthoPorts.items()})
		
#		for PName ,P in NewPorts.items():
#			print("# {0} ({1})".format(PName, P.Name))
#		input()
#		print("BEFORE")
#		print([P.Name for P in NewPorts.values()])
#		print("ClockManagerDict:", ClockManagerDict)
#		input()
		NewClockSigs={}
		for Sig, (TargetFrequency, Diff, Nets) in ClockManagerDict.items():
#			print("Sig:", Sig)
			for PName, P in self.OrthoPorts.items(): # remove old clock signal from new port list
				if PName==Sig.Name:
					if PName in NewPorts:
						del NewPorts[PName]
#						print("delete", PName,"/", P.Name)
						break
					else:
						logging.warning("[WrapForClocking] Cannot remove the '{0}' signal from ports of module '{1}': no such port.".format(PName, self.Name))
					
			for Net, (Pad, IOStandard, Voltage, Freq, DiffPair) in Nets:
				S=Signal(Net, Dir="IN", Size=1, Type="logic")
				NewPorts[Net]=S
				NewClockSigs[Net]=S
			if len(Nets)==2:
				ClockMapping={"clock_in1_p": ([[None, Nets[0][0], None],], True, Vars), "clock_in1_n": ([[None, Nets[1][0], None],], True, Vars), "clock_out1": ([["ClockManager21", Sig.Name, None],], True, Vars)}
				ClockManagerServName="ClockManager21"
			else:
				ClockMapping={"clock_in1": ([[None, Nets[0][0], None],], True, Vars), "clock_out1": ([["ClockManager21", Sig.Name, None],], True, Vars)}
				ClockManagerServName="ClockManager11"
			Mapping[Sig.Name]=([["ClockManager21", Sig.Name, None],], True, Vars)
			
			ClockManagerServ=Library.Service(ClockManagerServName)
			if ClockManagerServ is None:
				logging.error("[SyntheSys.SysGen.Module.WrapForClocking] No such service '{0}'".format(ClockManagerServName))
				return None
			Mappings.append(ClockMapping)
			NewServices.append(ClockManagerServ)
		
		#---------------Create final Port list-------------
#		SkipList=[]
#		for PName, P in NewPorts.items(): 
#			if P.Constraints:
#				if P.Constraints[1]=='ignore':
#					SkipList.append(PName)
#		SkipList+=[C.Name for C in ClockManagerDict]
		
		Ports=[P.HDLFormat() for P in NewPorts.values()]
		Params=[P.HDLFormat() for P in self.Params.values()]
		#--------------------------------------------------
#		print("AFTER")
		ModuleWrapper=LibEditor.NewModule(Infos=Infos, Params=Params, Ports=Ports, Clocks=list(NewClockSigs.keys()), Resets=[], Sources=[])
		#---------------------------------
#		ModuleWrapper.UpdateXML()
#		ModuleWrapper.IdentifyServices(NewServices)

		# Map services-----------------------------------
		XMLElmt=ModuleWrapper.UpdateXML()
		ModuleWrapper.Reload()
		ModuleWrapper.MapSubServices(Services=NewServices, Mappings=Mappings)
		ModuleWrapper.IdentifyServices(NewServices)
		# Add module packages to wrapper
		for P, PPath in self.Dependencies["package"].items():
			if P not in ModuleWrapper.Dependencies["package"]:
				ModuleWrapper.Dependencies["package"][P]=PPath
		#-----------------------------------------------------------------
		ModuleWrapper.NoOrthoPorts=True
		return ModuleWrapper, NewClockSigs
	#---------------------------------------------------------------
	def UpdateResources(self, FpgaId, HWRsc):
		"""
		Edit XML file with specified resources.
		"""
		self.Resources[FpgaId]=HWRsc
		RscDict=HWRsc.GetResourcesDict()
		FeaturesElmt_Found=None
		FpgaElmt_Found=None
		for FeaturesElmt in self.XMLElmt.iterchildren("features"):
			FpgaElmt_Found=FeaturesElmt_Found
			for FpgaElmt in FeaturesElmt.iterchildren("fpga"):
				if FpgaElmt.get("id")==FpgaId:
					FpgaElmt_Found=FpgaElmt
					for RscElmt in FpgaElmt.iterchildren("resources"):
						for Item in ('lut', 'ram', 'register'):
							RscType=Item.upper()
							if RscType in RscDict: RscElmt.attrib[Item]=str(RscDict[RscType][0])
							else: 
								RscElmt.attrib[Item]='0'
								logging.debug("Given resources: {0}".format(RscDict))
								logging.warning("[UpdateResources] No information about '{0}' resource : set to '0'.".format(RscType))
					return True
		# If FPGA not found : add it !
		if FpgaElmt_Found is None:
			if FeaturesElmt_Found is None:
				FeaturesElmt_Found=etree.SubElement(self.XMLElmt, 'features')
			FpgaElmt_Found=etree.SubElement(FeaturesElmt_Found, 'fpga')
		FpgaElmt_Found.attrib["id"]=FpgaId
		RscElmt=etree.SubElement(FpgaElmt_Found, 'resources')
		for Item in ('lut', 'ram', 'register'):
			RscType=Item.upper()
			if RscType in RscDict: RscElmt.attrib[Item]=str(RscDict[RscType][0])
			else: 
				RscElmt.attrib[Item]='0'
				logging.debug("Given resources: {0}".format(RscDict))
				logging.warning("[UpdateResources] No information about '{0}' resource : set to '0'.".format(Item))
		return True
	#---------------------------------------------------------------
	def Display(self):
		"""
		Display service parameters in log.
		"""
		print("MODULE:")
		print("\tname='{0}', Version='{1}'".format(self.Name, self.Version))
		print("\tTitle   ="+self.Title+"(Speed={0}, Area={1}, Tool={2}, Issues={3})".format(self.Speed, self.Area, self.Tool, self.Issues))
		print("\tPurpose ="+self.Purpose)
		print("\tDesc    ="+self.Desc)
		print("\tParameters ="+str([str(i) for i in self.Params.values()]))
		print("\tPorts      ="+str([str(i) for i in self.Ports.values()]))
		print("\tServices implemented ="+str(list(self.ProvidedServ.keys())))
		ReqVal = [x.split('#')[-1] for x in [x for x in list(self.ReqServ.keys()) if self.ReqServ[x][0]!=None]]
		print("\tServices required    ="+str(ReqVal))
		print("\tSources:")
		for Type in list(self.Sources.keys()):
			print("\t\t*{0}".format(Type))
			for S in self.Sources[Type]:
				print("\t\t\t{0}".format(S))
		print("\tResources ="+str(self.Resources))
	#---------------------------------------------------------------
	def __repr__(self):
		"""
		Return module minimal info.
		"""
		return "SyntheSys.SysGen.Module(XMLElmt={0}, FilePath={1})".format(repr(self.XMLElmt), repr(self.XmlFilePath))
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return module name.
		"""
		return self.Name
	#---------------------------------------------------------------
	def ID(self):
		"""
		Return module unique ID.
		"""
		return self.Name+"'"+str(Module.Instances.index(self))
	

#=======================================================================
def ServName(Code, Vars={}):
	"""
	Parse required service name and return normalized name format.
	"""
	ServID = Code.split(':')
	if ServID[0]=='': ServID[0] = Code
	if len(ServID)>1:
		for i in range(1, len(ServID)):
			ServID[i]=ServID[i]+str(eval(ServID[i], Vars))
		InstanceName = "_".join([ServID[0], "".join(ServID[1:])])
	else: InstanceName = ServID[0]
	return InstanceName
	

		
#============================================================================
def RemoveDuplicated(SignalList):
	"""
	Build a new list and fill it with a set of unique signals from argument list.
	"""
	SignalSet=[]
	SignalNameSet=[]
	for Sig in SignalList:
		if not str(Sig) in SignalNameSet:
			SignalSet.append(Sig)
			SignalNameSet.append(str(Sig))
	
	return SignalSet	
	
#============================================================================
def GetInternalSigFrom(Sig, FIndex=None, AIndex=None, WithName=None, Mod=None, IntSigs={}):
	"""
	return a signal copied from Sig with "WithName" and indexed with "AIndex".
	"""
	ActualSignal=Sig.Copy()
	if AIndex is None and not (FIndex is None):
		ActualSignal=ActualSignal[eval(FIndex, Sig.GetUsedParam())]
	
	if WithName is None: WithName=Sig.GetName()
	ActualSignal.SetName(WithName)
	
	ActualSignal.SetIndex(AIndex)
	HDLActual=ActualSignal.HDLFormat()

	# If it's an internal connection : declare new
	if (WithName not in IntSigs):
		try: eval(WithName) # actual is a constant number: don't declare
		except: # Actual is a signal name
			# Update signal with proper type/size
			# TODO: Do not declare non used signals
			IntSigs[WithName]=HDLActual# Declare signal as internal 
			
	return HDLActual

#============================================================================
def IndirectConnection(InterSigName, InterSigIndex, FormalSig, HDLActual, Connections=[], IntSigs={}, Vars={}):
	"""
	Connect formal and actual through an intermediate signal.
	"""
	# Create New internal signal
	# If it's an internal connection : declare signal
	if InterSigName in IntSigs:
		InterSig=IntSigs[InterSigName]
	else:
#		if HDLActual.Index is None and not (InterSigIndex is None):
		InterSig=FormalSig.HDLFormat()
#		else:
#			InterSig=HDLActual.Copy()
		InterSig.InverseDirection()
		InterSig.Name=InterSigName
#		IntSigs[InterSig].Vars.update(SubMod.Vars)
		IntSigs[InterSigName]=InterSig
	# TODO: Do not declare non used signals

	# Add connection index dictionary---------------
	if InterSigIndex is None:
		Connections[InterSig]=HDLActual
	else:
		if not InterSig in Connections:
			IndexDict={}
			Connections[InterSig]=IndexDict
		else:
			IndexDict=Connections[InterSig]

		IndexVal = eval(InterSigIndex, Vars.copy())
		IndexDict[IndexVal]=HDLActual
	return InterSig


#===============================================================
def DefaultMapping(Mod):
	"""
	return default mapping.
	"""
	Mapping=collections.OrderedDict()
	# Map internal signals
	StimuliList=[]
	TracesList=[]
	
	ClockNames=Mod.GetClockNames(MappedName=False)
	ResetNames=Mod.GetResetNames()
	# Get module input/output signals
	for N,P in Mod.GetExternalPorts().items():
		if not N in ClockNames:
			if P.Direction=="IN":
				S=P.Copy(WithName=N)
				StimuliList.append(S)
			if P.Direction=="OUT":
				S=P.Copy(WithName=N)
				TracesList.append(S)
	ClocksList  = [Signal(x, Size=1, Dir="IN") for x in ClockNames]
	ResetList   = [Signal(x, Size=1, Dir="IN") for x in ResetNames]
	
	InIndex=OutIndex=95
	for S in StimuliList:
		Size=S.GetSize()
		if Size!=1:
			Idx=slice(InIndex+1, InIndex+1-Size, -1)
		else:
			Idx=InIndex
		Mapping[S.GetName()] = ([[None, "Inputs", Idx] ], True, {})
		InIndex-=Size
	for T in TracesList:
		Size=T.GetSize()
		if Size!=1:
			Idx=slice(OutIndex+1, OutIndex+1-Size, -1)
		else:
			Idx=OutIndex
		Mapping[T.GetName()] = ([[None, "Outputs", Idx] ], True, {})
		OutIndex-=Size
		
	if len(ClocksList):
		Mapping[ClocksList[0].GetName()]    = ([[None, "Clk", None],], True, {})
		
	Params=[P for N,P in Mod.Params.items()]
	for P in Params:
		Mapping[P.GetName()] = ([[None, str(P.GetDefaultValue()), None] ], True, {})
		
	return Mapping, StimuliList, TracesList, ClocksList, ResetList
	
#===============================================================
def CopyModule(Mod):
	"""
	return copies of module and its provided service.
	This is needed to avoid issues with orthoports that are propagated throught the DUT wrapper.
	"""
	#---------------------------------
	# Create a copy of module
	Infos={}
	Infos={
		"Name"   : Mod.Name,
		"Version": "", # TODO get current time
		"Title"  : "Copy of {0} to be verified.".format(Mod.Name),
		"Purpose": "DEVICE UNDER TEST module.",
		"Desc"   : "",
		"Tool"   : "",
		"Area"   : "",
		"Speed"  : "",
		"Issues" : "",
	}
	Mapping, StimuliList, TracesList, ClocksList, ResetList=DefaultMapping(Mod)
	Ports=StimuliList+TracesList+ClocksList+ResetList
	Params=[P for N,P in Mod.Params.items()]
	CopyMod=LibEditor.NewModule(Infos=Infos, Params=Params, Ports=Ports, Clocks=[], Resets=[], Sources=[])
	
	#----------
	Infos={
		"Name"     : Mod.Name,
		"Type"     : "",
		"Version"  : "",
		"Category" : "",
	}
	CopyServ=LibEditor.ProvidedServiceXml(Mod=CopyMod, Interfaces=[], Infos=Infos)
	CopyServ.Alias=Mod.Name+"_DUT"
	
	return CopyMod, CopyServ, Mapping, StimuliList, TracesList, ClocksList
	
#==============================================================================
def GenerateEmptyWrapper(Mod=None, CopyMod=False):
	"""
	Generate new abstract module instantiating specified module.
	Mapping is default.
	"""
	logging.debug("Wrap module for verifying")
	if Mod is None:
		logging.error("[SyntheSys.SysGen.Module.GenerateEmptyWrapper] No Module specified. Aborted.")
		return None

	#----------
	if CopyMod is True:
		CopyMod, CopyServ, Mapping, StimuliList, TracesList, ClocksList = CopyModule(Mod)
	else:	
		Mapping, StimuliList, TracesList, ClocksList, ResetList = DefaultMapping(Mod)
		CopyMod  = Mod
		Infos={
			"Name"     : Mod.Name,
			"Type"     : "",
			"Version"  : "",
			"Category" : "",
		}
		CopyServ = LibEditor.ProvidedServiceXml(Mod, Interfaces=[], Infos=Infos, OutputPath=None)
	#---------------------------------
	
	#---------------------------------
	# Create a new module DUT
	Infos={
		"Name"   : "NoC",
		"Version": "", # TODO get current time
		"Title"  : "Empty wrapper for {0} to be verified.".format(Mod.Name),
		"Purpose": "DEVICE UNDER TEST module for resource estimation.",
		"Desc"   : "",
		"Tool"   : "",
		"Area"   : "",
		"Speed"  : "",
		"Issues" : "",
	}
	# Empty new module-----------------------------------

	Ports=[
#		Signal("Clk",   Dir="IN",  Size=1,  Type="logic").HDLFormat()
		]
	DUTMod=LibEditor.NewModule(Infos=Infos, Params=[], Ports=Ports, Clocks=[], Resets=[], Sources=[])
			
	#---------------------------------	
	DUTMod.UpdateXML()
	DUTMod.IdentifyServices([CopyServ, ])
	
	SubServices=[CopyServ,]
	Mappings=[Mapping,]
	DUTMod.MapSubServices(Services=SubServices, Mappings=Mappings)
	#----------
	XMLElmt=DUTMod.UpdateXML()
	DUTMod.Reload()
	DUTMod.IdentifyServices([CopyServ,])
	#-----------------------------------------------------------------
	return DUTMod
#===================================================================
def SharedName(Formal, Params, ReqMap):
	"""
	Build a signal name for share orthogonal signals.
	"""
	BaseName=Formal
	for PName in sorted(Params):
		if PName in ReqMap:
			ActualList, Cond, IdxDict = ReqMap[PName]
			InstName, SigName, Index  = ActualList[0] # TODO Maybe use condition
			BaseName+='_'+SigName
	return BaseName
	
	
	
	

