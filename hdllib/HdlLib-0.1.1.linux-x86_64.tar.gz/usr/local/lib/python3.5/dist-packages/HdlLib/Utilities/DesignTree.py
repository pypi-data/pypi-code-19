
import os, sys, re
import logging

#if sys.maxsize > 2**32: ARCHI="64" # ARCHI = "32" if sys.maxsize==2**32/2-1 else "64"
#else: ARCHI="32" 
#ParserDir = os.path.join(os.path.dirname(__file__), "Parser/results/{0}/{2}/{1}bit/".format("windows" if sys.platform.startswith("win") else "linux", ARCHI, "Python3" if "python3" in sys.executable else "Python2"))
#sys.path.append(ParserDir)
#try: import Parser
#except:
#	logging.error("ParserDir: {0}".format(ParserDir))
#	logging.error("Unable to import 'Parser' module. Check for extension compatibility. Aborted.")
#	sys.exit(1)

import io
PYTHON_PATH=os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
from HdlLib.Utilities.ExtensionSilence import ExtensionSilence

#======================================================================	
class Design:
	#--------------------------------------------------------------
	def __init__(self, FileList=[]):
		logging.debug("New design with these files: {0}".format(FileList))
		self.VerilogList = list(filter(IsVerilog, FileList)) # List
		self.VHDLList = list(filter(IsVHDL, FileList)) # List
		self.TopComponentList = [] # List
		self.ComponentList = [] # List
		
		self.ParserMsg=""
		self.GetComponentList(self.VHDLList)
		
		try:
			with open("./ADACSYS_PARSER_STDOUT.txt", 'r') as StdOutFile:
				self.ParserMsg=StdOutFile.read()
			os.remove("./ADACSYS_PARSER_STDOUT.txt")
			os.remove("./ADACSYS_PARSER_STDERR.txt")
		except: pass
		
		self.BuildDesign()
		self.BuildPathNames()
		if len(self.TopComponentList):
			self.TopComponentList[0].IsSelected=True
	#--------------------------------------------------------------
	def GetComponentList(self, FileList):
		"""
		Build a list component object with help of Parser C++ module.
		"""
		self.ComponentList = []
		print(Parser.__file__)
		DataBase = Parser.GuiInterface()
		for FilePath in FileList:
			DataBase.resetParse()
			if re.match(r".*\.(vhd)", FilePath): # Parse only vhdl files
				logging.info("Parse file '{0}'.".format(FilePath))
				if sys.platform.startswith('win'):
					if DataBase.singleFileParse(FilePath, "work"):
						break
				else:
					with ExtensionSilence(stdout="./ADACSYS_PARSER_STDOUT.txt", stderr="./ADACSYS_PARSER_STDERR.txt", mode='wb'):
						if DataBase.singleFileParse(FilePath, "work"):
							break
				logging.debug("Parse succeeded.")
					
		EntityList = Parser.StringVector()
		DataBase.getEntityList(EntityList)
		for i in range(len(EntityList)):
			EntityName = EntityList[i]
			self.ComponentList.append(Component(EntityName, DataBase=DataBase, FilePath=FilePath))
		return True
	#--------------------------------------------------------------
	def BuildDesign(self):
		"""
		Connect the components to each others according to their entity name.
		"""
		logging.debug("Connect the components to each others according to their entity name")
		#First Build a list of component that will be analysed
		CompLeft=self.ComponentList[:]
		while(CompLeft != []):
			MyComponent = CompLeft.pop() # Component to analyse
			# Replace every Missing instance of MyComponent by a Full Component if possible
			for MissingInstance in MyComponent.MissingInstanceList:
				# Find Component with the same entity name in the main list
				for Comp in self.ComponentList:
					if Comp.EntityName == MissingInstance.EntityName:
						Comp.AddParent(MyComponent, MissingInstance.InstanceName)
						break
		# Now identify the very missing instances for final list and build the Top list
		for Component in self.ComponentList:
			if Component.IsTop:
				self.TopComponentList.append(Component)
			# Find the instance if member of Full component list
			for MissingInstance in Component.MissingInstanceList:
				Found = False
				for FullInstance in Component.InstanceList:
					if FullInstance.EntityName == MissingInstance.EntityName:
						Found = True
				# Add the missing component to the final Instance list
				if Found==False:
					MissingInstance.IsTop=False
					Component.InstanceList.append(MissingInstance)
			Component.MissingInstanceList = [] # Empty the list of missing instances
	#--------------------------------------------------------------
	def GetComponent(self, EntityName=""):
		"""
		Seach entity in component list and return it.
		"""
		if EntityName=="": return None
		for Component in self.ComponentList:
			if Component.EntityName == EntityName:
				return Component
		return None
	#--------------------------------------------------------------
	def GetComponentInstance(self, DUTInstanceName):
		"""
		Seach instance in component list and return it.
		"""
		for C in self.ComponentList:
			if C.InstanceName == DUTInstanceName:
				return C
		return None
	#--------------------------------------------------------------
	def BuildPathNames(self):
		"""
		Build path name of every signal in every component.
		"""
		#print "* Build Path Names"
		for Component in self.ComponentList:
			CurComponent=Component
			#print "Parents for", Component.EntityName, ":"
			while(CurComponent!=None):
				if(not CurComponent.IsTop):
					# Update signal pathnames
					for Port in Component.PortList:
						Port.AddPath(CurComponent.InstanceName)
					for IntSig in Component.IntSigList:
						IntSig.AddPath(CurComponent.InstanceName)
					CurComponent=CurComponent.GetParent()
					#print "--->", CurComponent.EntityName
				else:
					break

#======================================================================	
class Component:
	#-----------------------------------------------------------------------------------------
	def __init__(self, TopEntityName=None, InstanceName=None, ArchiName=None, DataBase = None, Parent=None, FilePath=None):
		if(TopEntityName==None): raise NameError("[Design.__init__] - Nothing to parse")
		self.IsTop        = True # Boolean
		self.IsSelected   = False # Boolean
		self.Parent       = Parent # Component
		self.DataBase     = DataBase # GuiInterface object
		self.EntityName   = TopEntityName # String
		self.InstanceName = "" if InstanceName==None else InstanceName # if InstanceName else TopEntityName
		self.FilePath     = FilePath # String
		self.InstanceList = [] # Component List
		
		if self.DataBase!=None:
			DataBase.setTop(self.EntityName)
			self.IsMissing = False # Boolean
#			self.ArchiList    = self.GetArchis() # String List
			
#			if ArchiName==None:
#				logging.debug("[{0}({1})] Implicit architecture. Now seek for potential architectures.".format(self.InstanceName, self.EntityName))
#				Results = Parser.StringVector()
#				DataBase.getPotentialArchitectures(self.InstanceName, Results)
#				PAs=[]
#				logging.debug("Results: {0}".format(list(Results)))
#				for PA in list(Results):
#					logging.debug("Potential architecture: {0}".format(str(PA)))
#					PAs.append(PA)
#				if len(PAs):
#					ArchiName = PAs[-1]
			self.ArchiName = ArchiName
			
#			self.ModelName    = self.EntityName + "." + self.ArchiName # String
			self.PortList     = self.GetPorts() # Signal List
			self.IntSigList   = self.GetIntSigs() # Signal List
			self.MissingInstanceList = self.GetMissingInstances() # Component List
			self.ConstList    = [] # For future implementation # Signal List
			#print "COMPONENT INSTANCIATION:"
			#print self
		else:
			self.IsMissing = True
			self.ArchiName = None
			self.PortList     = [] # Signal List
			self.IntSigList   = [] # Signal List
			self.MissingInstanceList = [] # Component List
			self.ConstList    = [] # For future implementation # Signal List
#	#-----------------------------------------------------------------------------------------
#	def GetArchis(self):
#		"""
#		Return a list of architectures available for this component entity.
#		"""
#		logging.debug("List architectures available for this component")
#		ArchiList = []
#		Archis = Parser.StringVector() # C++ type 
#		self.DataBase.getArchitectureList(self.EntityName, Archis) # Recherche des differentes architectures de l'entite top 
#		for i in range(len(Archis)): # Convert to python list
#			item = str(Archis[i]).strip()
#			#print "\tArchi found:", item
#			if(item!=""):
#				ArchiList.append(item)
#		
#		logging.debug("Architectures: parsed.")
#		if(len(ArchiList)<1): 
#			raise NameError("[Component.__init__] - No architecture found")
#		return ArchiList
	#-----------------------------------------------------------------------------------------
	def GetGenerics(self):
		"""
		Return a list of generics declared in the component entity.
		"""
		logging.debug("List generics available for this component")
		Generics = {}
#		if not isinstance(self.ArchiList[0], str): return {}
#		Arch   = self.ArchiList[0]
#		Entity = self.EntityName
#		Code = str(self.DataBase.getRawGenerics(Entity, Arch))
#		if len(Code.strip()):
#			Code = Code[Code.find('(')+1:Code.rfind(')')]
#			GenList = Code.split(';')
#			for Gen in GenList:
#				# Try to get Generic init value
#				if Code.rfind(':=')!=-1: 
#					GInit = Code[Code.rfind(':=')+2:].strip()
#					# Get Generic type
#					GType = Code[Code.find(':')+1:Code.rfind(':=')].strip()
#				else: 
#					GInit = ""
#					# Get Generic type
#					GType = Code[Code.find(':')+1:].strip()
#				# Get Generic size
#				for Token in ('downto', 'to'):
#					Res = Code.strip('(').strip(')').lower().split(Token)
#					if len(Res)>1:
#						GSize = int(Res[0].split()[-1].strip('('))-int(Res[1].split()[0])+1
#						break
#				# Keep only type identifier (not the size)
#				GType = GType.split()[0].split('(')[0].strip()
#				# Get Generic type
#				GName = Code[:Code.find(':')].strip()
#				Generics["{0}/{1}/{2}".format(GName, GSize, GType)]=GInit
		return Generics

	#-----------------------------------------------------------------------------------------
	def GetPorts(self):
		"""
		Return a list of ports of this component entity.
		"""
		logging.debug("List ports available for this component")
		Ports = Parser.SignalVector() # Liste vide de GuiInterfaceSignal
		PortList = []
		if(not self.DataBase.getPorts("", Ports)):
			for i in range(len(Ports)): # Convert to python list
			#for Port in Ports:
				# Append to list a Signal object
				Port = Ports[i]
				PortList.append(Signal(Name=Port.getName(), IO=Port.getIO(), Type=Port.getType(), Size=Port.getSize(), IsInstru=Port.getInstrumentable()))
		else:
			logging.error("Error looking for entity '"+self.EntityName+"' to get ports.")
		return PortList
	#-----------------------------------------------------------------------------------------
	def GetIntSigs(self):
		"""
		Return a list of internal signals of this component entity.
		"""
		logging.debug("List internal signals available for this component")
		IntSigs = Parser.SignalVector() # Liste vide de GuiInterfaceSignal
		IntSigList = []
		if(not self.DataBase.getInternalSignals("", IntSigs)):
			for i in range(len(IntSigs)): # Convert to python list
			#for IntSig in IntSigs:
				# Append to list a Signal object
				IntSig=IntSigs[i]
				IntSigList.append(Signal(Name = IntSig.getName(), Type = IntSig.getType(), Size = IntSig.getSize(), IsInstru = IntSig.getInstrumentable()))
		else:
			logging.error("Error looking for model of entity '"+self.EntityName+"' and archi '"+self.ArchiName+"' to get internal sigs.")
		return IntSigList
	#-----------------------------------------------------------------------------------------	
	def GetMissingInstances(self):
		"""
		Return a list of instances of this component that source file are not found.
		"""
		logging.debug("List instances without source")
		Instances = Parser.ComponentVector() # Liste de GuiInterfaceComponent
		InstanceList = []
		if self.DataBase.getInstances("", Instances):
			logging.error("Unable to get list of instance of {0}.".format(" ".join([self.EntityName,])))
			return []
			
		for i in range(len(Instances)): # Convert to python list
		#for Instance in Instances:
			Instance   = Instances[i]
			InstanceList.append(Component(TopEntityName=Instance.getEntityName(), InstanceName=Instance.getInstanceName(), ArchiName=Instance.getArchitectureName(), DataBase = None))
#			logging.error("> Architecture name of {0} is {1}".format(Instance.getEntityName(), Instance.getArchitectureName()))
		return InstanceList
	#-----------------------------------------------------------------------------------------	
	def GetParent(self):
		"""
		Return a component parent in its hierarchy.
		"""
		return self.Parent
	#-----------------------------------------------------------------------------------------
	def AddParent(self, ParentComponent, InstanceName):
		"""
		Set this component as a child of its parent.
		Tag it as not a TOP any more if it was, and give it a instance name.
		"""				
		# Component recognized as instance !
		ParentComponent.InstanceList.append(self)
		# Tag as not Top Entity any more
		self.IsTop = False
		# Save his instance name
		self.InstanceName = InstanceName
		self.Parent=ParentComponent
	#-----------------------------------------------------------------------------------------	
	def GetSources(self):
		"""
		Return a list of HDL source paths in a dependancy order (last=top).
		"""
		SourceList=[]
		# Build the list in the proper order
		for Instance in self.InstanceList: # Browse every component of the hierarchy
			SourceList+=Instance.GetSources()
		# Top at last !
		if self.FilePath: SourceList.append(self.FilePath)
		return SourceList
	#----------------------------------------------------------------------
	def __str__(self):
		CompString = "* Entity:'"+str(self.EntityName)+"'\n"
		CompString += "* Architecture:'"+str(self.ArchiName)+"'\n"
		CompString += "* InstanceName:'"+str(self.InstanceName)+"'\n"
#		CompString += "* ModelName:'"+str(self.ModelName)+"'\n"
		CompString += "* PortList:'"+str(self.PortList)+"'\n"
		CompString += "* IntSigList:'"+str(self.IntSigList)+"'\n"
		CompString += "* ConstList:'"+str(self.ConstList)+"'\n"
#		CompString += "* From File:'"+self.DataBase.getDefinitionFile(self.ModelName)+"'"
		return CompString	

#======================================================================
class Signal:
	"Contains all the features that are part of a signal"
	#----------------------------------------------------------------------
	def __init__(self, Name = "Unkown_signal", IO = None, Type = [], Size = None,  IsInstru = False):
		self.Name   = Name # String
		self.IO     = IO.upper() if isinstance(IO, str) else None # String
		self.Type   = Type # often a vhdl source text copy
		self.Size   = Size # String or int
		self.IsInstru = IsInstru # Boolean
		if(self.Size>1):
			# Name to be written into stimSigValues.txt or traceSigNames.txt
			self.PathName = self.Name+"("+str(self.Size-1)+":0)" # String
		else:
			self.PathName = self.Name # String

	#----------------------------------------------------------------------
	def AddPath(self, Path):
		#print "#", self.PathName
		self.PathName = Path+" "+self.PathName
		self.PathName = self.PathName.strip()

	#----------------------------------------------------------------------
	def __repr__(self):
		return self.PathName

	#----------------------------------------------------------------------
	def __str__(self):
		return self.PathName

#======================================================================
def IsVerilog(FilePath):
	if re.match(r".*\.v$", FilePath): return True
	return False

#======================================================================
def IsVHDL(FilePath):
	if re.match(r".*\.vhd$", FilePath): return True
	return False
	
#================================================================
if __name__ == "__main__":
	
	from HdlLib.Utilities import ColoredLogging
	ColoredLogging.SetActive(True)
	#====================LOGGING CONFIGURATION=================
	from HdlLib.Utilities import ConsoleInterface
	ConsoleInterface.ConfigLogging(Version="1.0", ModuleName="pySystems")
	#==========================================================

	FileList = ['../../IP/calculus8bit/src/add4bit.vhd', '../../IP/calculus8bit/src/calculus4bit.vhd', '../../IP/calculus8bit/src/mux4bit.vhd', '../../IP/calculus8bit/src/shift4bit.vhd', '../../IP/calculus8bit/src/sub4bit.vhd', ]#'../../IP/calculus8bit/src/TB_calculus8bit.vhd'
	D = Design(FileList)
	





