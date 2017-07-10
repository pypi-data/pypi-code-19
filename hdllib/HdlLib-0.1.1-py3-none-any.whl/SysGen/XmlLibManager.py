#!/usr/bin/python


import os, sys, logging, shutil, math, random
from lxml import etree

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__))))
from HdlLib.SysGen import HDLEditor as HDL
HDL.Generator="YANGO netlist generator" # For Header comments

from HdlLib.SysGen.Service import Service
from HdlLib.SysGen.Module import Module

#=======================================================================
class XmlLibManager:
	#---------------------------------------------------------------
	def __init__(self, LibPath, *ExtendedPathList):
		"""
		Save library path.
		"""
		self.LibPath  = os.path.abspath(LibPath)
		logging.debug("LibPath: '{0}'".format(LibPath))
		logging.debug("ExtendedPathList: '{0}'".format(ExtendedPathList))
		self.ExtPaths = [os.path.abspath(x) for x in list(ExtendedPathList)]
		self.Services = list()
		self.Modules  = list()
		self.DTD      = {}
		self.Classification={}
		
		for Type in ["service", "module"]:
			DTDPath=os.path.join(self.LibPath, "{0}.dtd".format(Type))
			if not os.path.isfile(DTDPath): 
				logging.error("No such file '{0}'. Check for library integrity or change library path.".format(DTDPath))
				sys.exit(1)
			self.DTD[Type] = etree.DTD(DTDPath)
		
		CurDir=os.path.abspath("./")
		
		os.chdir(self.LibPath) # For source path fetching
		logging.debug("Loading the library...")
		if self.Reload() is False:
			logging.error("Library corrupted.")
			sys.exit(1)
		logging.debug("Library initialized.")
		os.chdir(CurDir)
	#---------------------------------------------------------------
	def Reload(self):
		"""
		Parse each xml file in library path and filter module/service xml elements
		"""
		del self.Services[:]
		del self.Modules[:]
		self.Classification={}
		for Path in self.ExtPaths+[self.LibPath,]:
#			logging.debug("[LIBRARY:'{0}'] Browsing...'{0}'".format(Path))
			for Root, SubFolders, Files in os.walk(Path):
				for FileName in Files:
					if FileName.endswith(".xml"):
						FilePath = os.path.join(Root, FileName)
						RootElmt = etree.parse(FilePath)
#						logging.debug("[LIBRARY:'{0}'] Looking for modules in '{1}'...".format(os.path.basename(self.LibPath), FileName))
						for Elmt in RootElmt.iter("module"):
							if self.Verify("module", Elmt):	 
								try: self.Modules.append(Module(Elmt, FilePath)) 
								except: 
									logging.error("File '{0}' parsing failure.".format(FilePath))
									return False
#						logging.debug("[LIBRARY:'{0}'] Looking for services in '{1}'...".format(os.path.basename(self.LibPath), FileName))
						for Elmt in RootElmt.iter("service"):
							if self.Verify("service", Elmt): 
								try: self.Services.append(Service(Elmt))
								except: 
									logging.error("File '{0}' parsing failure.".format(FilePath))
									return False
		self.LinkMod2Serv()
		return True
	#---------------------------------------------------------------
	def LinkMod2Serv(self):
		"""
		Parse each xml file in library path and filter module/service xml elements
		"""
#		logging.debug("[LIBRARY:'{0}'] Link all modules/services...".format(os.path.basename(self.LibPath)))
		# Link all modules to services each other
		for Mod in self.Modules:
			Mod.IdentifyServices(self.Services)
			for ID, ServReq in list(Mod.ReqServ.items()):
				if ServReq[0] is None:
					logging.warning("no service found for ID='{0}'".format(ID))
			
#		logging.debug("[LIBRARY:'{0}'] Link all services to modules...".format(os.path.basename(self.LibPath)))
		for Serv in self.Services:
			# Classify the service
			if not Serv.Category: self.ClassifyService(Serv, TreePath=None)
			else: 
				TPath=Serv.Category.split('.')
				TPath.reverse()
				self.ClassifyService(Serv, TreePath=TPath)
			# Link to modules	
			for Mod in self.Modules:
				if Mod.Provide(Serv.Name): 
					Serv.AddModule(Mod)
					Mod.ProvidedServ[Serv.Name]=Serv
#		logging.debug("[LIBRARY:'{0}'] Library loaded.".format(os.path.basename(self.LibPath)))
	#---------------------------------------------------------------
	def ClassifyService(self, Serv, TreePath=None, Cat=None):
		"""
		Insert the service into the category classification.
		"""
		if not TreePath:
			if not list(self.Classification.keys()).count("Unclassified"): self.Classification["Unclassified"]={}
			self.Classification["Unclassified"]['{0}({1})[v{2}]'.format(Serv.Name, Serv.Type, Serv.Version)]=Serv
		else:
			if Cat==None: Cat=self.Classification
			
			Leaf = TreePath.pop()
			if len(TreePath)>0:
				if not list(Cat.keys()).count(Leaf): Cat[Leaf]={}
#				logging.info("Classify Service class {0}.".format(Leaf))
				self.ClassifyService(Serv, TreePath, Cat=Cat[Leaf])
			else: # in the end: add service
				if not list(Cat.keys()).count(Leaf): Cat[Leaf]={}
				if list(Cat[Leaf].keys()).count('{0}({1})[v{2}]'.format(Serv.Name, Serv.Type, Serv.Version)): 
#					logging.error("Service {0} already classified: ignored.".format('{0}({1})[v{2}]'.format(Serv.Name, Serv.Type, Serv.Version)))
					return
#				logging.info("Classify Service {0}.".format(Leaf))
				Cat[Leaf]['{0}({1})[v{2}]'.format(Serv.Name, Serv.Type, Serv.Version)]=Serv
	#---------------------------------------------------------------
	def Verify(self, Type, Elmt):
		"""
		Parse each xml file in library path and filter module/service xml elements
		"""
		if list(self.DTD.keys()).count(Type):  
			Valid = self.DTD[Type].validate(Elmt)
			if Valid: return True
			else:
				logging.error(self.DTD[Type].error_log.filter_from_errors()[0])
				sys.exit(1)
				return False
		else: 
			logging.error("No such type ({0}) for this library.".format(Type))
			sys.exit(1)
			return False
	#---------------------------------------------------------------
	def Display(self, ServiceTree=False):
		"""
		Print to stdout the list of modules and services or Service tree classification.
		"""			
		#---------------------------------------------------------------
		def DisplayTreeServ(Tree, Indent=""):
			"""
			Print to stdout recursively subtree item with indentation.
			"""
			for Item in sorted(Tree.keys()):
				if isinstance(Tree[Item], dict):
					print((Indent+"-->"+Item))
					DisplayTreeServ(Tree[Item], Indent=Indent+"  ")
				else:
					print((Indent+"* "+Item))
		#---------------------------------------------------------------
		if ServiceTree:
			print("SERVICE LIBRARY:")
			DisplayTreeServ(self.Classification)
		
		else:
			for Serv in self.Services:
				Serv.Display()
			for Mod in self.Modules:
				Mod.Display()
			
			print("")
			print(("#"*55))
			print(("# SUMMARY: {0} Services and {1} Modules saved in library.".format(len(self.Services), len(self.Modules))))
			print(("#"*55))
	#---------------------------------------------------------------
	def Service(self, SName, SType=None, SVersion=None, ServiceAlias=None):
		"""
		Return the service object with specified name/type/version if it exists, None otherwise.
		"""
		# TODO : SType management
		Serv=SName.split('.')[-1]
		for Serv in self.Services:
			if Serv.Name==SName:
				if ServiceAlias is None: Serv.Alias=Serv.Name
				else: Serv.Alias=ServiceAlias
				
				if SVersion:
					if Serv.Version==SVersion: return Serv
				else: return Serv
		logging.error("Service '{0}' not found ! Unable to fetch it in library.".format(SName))
		return None
	#---------------------------------------------------------------
	def Module(self, MName, MType=None, MVersion=None):
		"""
		Return the module object with specified name/type/version if it exists, None otherwise.
		"""
#		logging.debug("Get module object for '{0}'".format(MName))
		for Mod in self.Modules:
			if Mod.Name.lower()==MName.lower():
				#if MType:
					#if Mod.Type==MType:
				if MVersion:
					if Mod.Version==MVersion: return Mod
				else: return Mod
				#else: return Mod	
		return None
	#---------------------------------------------------------------
	def AddService(self, Serv):
		"""
		Add service to library dynamically.
		"""
		Serv.SetFromXML(Serv.XMLElmt) # To be sure everything is considered
		
		self.Services.append(Serv)
#		logging.warning("Add service '{0}'".format(Serv))
		# Link to modules
		for Mod in self.Modules: 
			if Mod.Provide(Serv.Name): 
				Serv.AddModule(Mod)
				Mod.ProvidedServ[Serv.Name]=Serv
				logging.warning("Add service '{0}' to module '{1}'".format(Serv, Mod))
				input()
	#---------------------------------------------------------------
	def AddModule(self, Mod):
		"""
		Add module to library dynamically.
		"""
		Mod.SetFromXML(Mod.XMLElmt) # To be sure everything is considered
		self.Modules.append(Mod)
		# Replace ID by a Service object
		for ID, ServReq in list(Mod.ReqServ.items()):
			SName, SType, SVersion, UniqueName = ID.split('#')
			for S in self.Services:
				# Find the corresponding service in library
				if S.Name==SName and S.Version==SVersion:	
					ServReq[0]=S
		for Serv in self.Services:
			# Link to modules
			if Mod.Provide(Serv.Name): 
				Serv.AddModule(Mod)
				Mod.ProvidedServ[Serv.Name]=Serv
#		logging.debug("['{0}'] Module loaded into library.".format(self))
	#---------------------------------------------------------------
	def ListServices(self):
		"""
		Fetch list of services in XML library and return a dict object.
		"""
		ServDict={}
		for S in self.Services:
			ServDict[S.Name]=S
		return ServDict
	#---------------------------------------------------------------
	def ListModules(self):
		"""
		Get a list of modules in XML library and return it.
		"""
		return self.Modules
		
##============================================================================
#def UniqueName(SigName, SigList):
#	"""
#	Return a unique name for a signal by appending '_' + a number.
#	The returned name is garantied not to be in SigList. 
#	"""
#	Index = 0
#	while SigList.count(SigName+'_'+str(Index)):
#		Index+=1
#	return SigName+'_'+str(Index)
#	
	
# ====================  START OF THE HDLGenerator APPLICATION  =====================
if (__name__ == "__main__"):

	Lib = XmlLibManager("./lib", [os.path.abspath("./NoC"),])
#------------------------------------------------------------------------
#	logging.info("*** Generate example design from XML description ***")
#	Lib.Service("serviceC").GenSrc(True, "./Test_ServiceC")	
#	logging.info("*** 'serviceC' generated successfully ***")
#	logging.info("*** Generate Hermes NoC design from XML description ***")
#	Lib.Module("NoC").GenSrc(True, "./Test_NoC")	
	#Lib.Module("NoC").Display()
#------------------------------------------------------------------------
#	logging.info("*** Generate Router from XML description ***")
#	Router = Lib.Module("Router")
#	if Router: 
#		Router.GenSrc(Synthesizable=True, OutputDir="./Test_Router", TestBench=True)
#	else: 
#		logging.error("Module 'Router' not found")
#		sys.exit(1)
#	logging.info("*** 'Router' generated successfully ***")
#------------------------------------------------------------------------
#	AdOCNet = Lib.Module("AdOCNet")
#	AdOCNet.Display()
#	if AdOCNet: 
#		AdOCNet.GenSrc(Synthesizable=True, OutputDir="./Test_AdOCNet", TestBench=True)
#	else: 
#		logging.error("Module 'AdOCNet' not found")
#		sys.exit(1)
#	logging.info("*** 'NoC' generated successfully ***")
#	Lib.Display()
#------------------------------------------------------------------------
	Lib.Display(ServiceTree=True)
	sys.exit(0)
	
	
	

