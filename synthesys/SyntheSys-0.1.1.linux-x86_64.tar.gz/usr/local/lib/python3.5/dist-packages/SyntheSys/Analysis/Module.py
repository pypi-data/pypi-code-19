import logging
import os, sys, datetime
import collections
try: import pickle
except ImportError: import pickle as pickle
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))
from SyntheSys.Utilities.Timer import Timer
from SyntheSys.Analysis import Tracer
from SyntheSys.Analysis.Data import Data
from SyntheSys.Analysis.Reduce import Reduce
import networkx as nx
try: import networkx as nx
except ImportError: import pickle as pickle

from SyntheSys.Analysis.Operation import Operation as Op
from SyntheSys.Analysis import Tracer, TBValues
from SyntheSys.Synthesis.Graphs import DataFlowGraph
#from SyntheSys.Analysis import TaskGraph

TargetList=[]
#===========================================================================
def Synthesizable(HighLevelModuleClass):
	"""
	Class decorator (static decorator) for "HighLevelModule" objects.
	Save algorithm marked method.
	"""
	#logging.debug("Seeking algorithm method of HighLevelModule '{0}'".format(HighLevelModuleClass))
	Algo = None
	TB   = None
	for Name, Method in HighLevelModuleClass.__dict__.items():
		if hasattr(Method, "IsAlgo"):
#			raw_input("Found Algo method")
			Algo=Method
		elif hasattr(Method, "IsTB"):
#			raw_input("Found testbench method")
			TB=Method
	if Algo : HighLevelModuleClass._Algorithm=Algo
	if TB   : HighLevelModuleClass._Testbench=TB
	#logging.debug("Build class '{0}'".format(HighLevelModuleClass))
	return HighLevelModuleClass

#=========================================================
class HighLevelModule():
	_TargetHW=None # Common to all modules
	DATAFLOW_TRACKING=False
	RECORD_VALUES=False
	NO_WRAPPING=True
	#--------------------------------------------------------------------
	def __init__(self):
		"""
		Initialization of the HighLevelModule attributes.
		
		Data is output when only written in a HighLevelModule.
		Data is input when only read by a HighLevelModule. 
		Data is inout when both read and written by a HighLevelModule. 
		"""
		_Algorithm=lambda *args, **kargs: logging.error("No algorithm function defined.")
		_Testbench=lambda *args, **kargs: logging.error("No testbench function defined.")
		self.CDFG=None # Data Flow Graph
		self.TaskGraph=None # Task communication Graph
#		self.ArgList  = []
		self.ArgDict  = {}
		self.ReturnList = []
#		self.InternalDict = []
		
#		self.BRANCH_BROWSING=False
		
		self.Implementation=None
		# Get Module instance Name
		self._Name=self.__class__.__name__
		self.AlgoName=self._Name
#		frame = inspect.currentframe().f_back
		
		self._TBValues=TBValues.TBValues()
	#-------------------------------------------------
	def GetName(self):
		"""GETTER"""
		return self._Name
	#-------------------------------------------------
	def SetName(self, Name):
		"""SETTER"""
		self._Name=Name
	Name=property(GetName, SetName)
	#--------------------------------------------------------------------
	def __reset__(self):
		"""
		re-initialize attributes.
		"""
		self.CDFG=None # Data Flow Graph
		self.TaskGraph=None # Task communication Graph
#		self.ArgList  = []
		self.ArgDict  = {}
		self.ReturnList = []
#		self.InternalDict = []
		
		HighLevelModule.DATAFLOW_TRACKING=False
#		HighLevelModule.BRANCH_BROWSING=False
		HighLevelModule.RECORD_VALUES=False
		
		# Get Module instance Name
		self._Name=self.__class__.__name__
#		frame = inspect.currentframe().f_back
		
		self._TBValues=TBValues.TBValues()
		return 
	#----------------------------------------------------------------------
	def SetTaskGraph(self, TaskGraph):
		"""
		Draw task communication graph of current module.
		"""
		if not TaskGraph is None:
			self.TaskGraph=TaskGraph
	#----------------------------------------------------------------------
	def GetTaskGraph(self):
		"""
		Return task communication graph of current module.
		"""
		return self.TaskGraph
	#--------------------------------------------------------------------
	def GetTBValues(self):
		"""
		Return _TBValues attribute.
		"""
		return self._TBValues
	#--------------------------------------------------------------------
	def GetName(self):
		"""
		Return _AlgoName attribute. 
		"""
		return self.AlgoName
	#--------------------------------------------------------------------
	def UpdateCDFG(self):
		"""
		Create a networkx graph and call Tracer object recursive method to fill the graph. 
		"""
#		logging.debug("Build a new data flow graph")
		self.CDFG = DataFlowGraph.NewCDFG(ArgDict=self.ArgDict, ReturnList=self.ReturnList)

#		logging.debug("DFG connected components: {0}".format(nx.connected_components(self.CDFG)))
		return self.CDFG
	#--------------------------------------------------------------------
	def Exec(self, *args, **kwargs):
		"""
		Execute the algorithm function.
		"""
#		logging.debug("[HighLevelModule.Exec] Execute algorithm function '{0}'".format(self._Algorithm))
		return self._Algorithm(*args, **kwargs)
	#--------------------------------------------------------------------
	def GetLatency(self, Constraints):
		"""
		Return latency in clock cycles according to Constraints.
		"""
		pass
	#--------------------------------------------------------------------
	def GetThroughput(self, Constraints):
		"""
		Return latency in clock cycles according to Constraints.
		"""
		pass
	#--------------------------------------------------------------------
	def SetService(self, ServiceName):
		"""
		Add a new instance of Implementation to HighLevelModule object for a specified hardware.
		"""
		self.Implementation=Implementation(ServiceName)
		return self.Implementation
#	#--------------------------------------------------------------------
#	def GetImplementation(self, HW):
#		"""
#		Add a new instance of Implementation to HighLevelModule object for a specified hardware.
#		"""
#		if HM in self._Implementations:
#			return self._Implementations[HM]
#		else:
#			raise NameError("No Implementation set for hardware '{0}'".format(HW))
#	#--------------------------------------------------------------------
#	def GetInterfaceDatas(self):
#		"""
#		Return list of Data used as arguments and returned from HighLevelModule algorithm function.
#		"""
#		InterfaceSig = {}
#		InterfaceSig.update(self.ArgDict)
#		InterfaceSig.update({R._Name:R for R in self.ReturnList})
#		return InterfaceSig
	#--------------------------------------------------------------------
	def GetConstants(self):
		"""
		Return list of Data used as constant in HighLevelModule algorithm function.
		"""
		return dict((N, S) for N, S in self.ArgDict.items() if S.IsConstant==True)
#	#--------------------------------------------------------------------
#	def GetDataArgs(self):
#		"""
#		Generate Data objects from inputs arguments of algorithm method and return them.
#		"""
#		logging.debug("Generate Data objects from inputs arguments of algorithm method and return them.")
#		Args = map(lambda x: x if not isinstance(x, list) else [t for t in x], self.ArgList)
#		#Kwargs = {k:v() for k,v in self.ArgDict.iteritems()}	
#		logging.debug("New args : {0}.".format(args))
#		return Args, self.ArgDict
	#--------------------------------------------------------------------
	def IsBlackBox(self):
		"""
		Return True if module has to be considered as a black box.
		"""
#		if HighLevelModule._TargetHW in self._Implementations:
			# TODO: consider constraints
#			return True
#		else: return False
#		logging.debug("Add Task : '{0}'.".format(self.__name__))
		return not (self.Implementation is None)
	#--------------------------------------------------------------------
	def BlackBoxFunction(self, *args, **kwargs):
		"""
		Create an Operation with module name, and return Datas from Operation output.
		"""
		if len(args)>0:
			if isinstance(args[0], HighLevelModule):
				args=list(args[1:])
#		ModuleName = "{0}".format(self.__class__.__name__)
		Inputs = self.Implementation.InputsInArguments(*args, **kwargs)
		Outputs, ROutputs = self.Implementation.OutputsInArguments(*args, **kwargs) # Outputs=Names, ROutputs=Datas
		InputDatas=list(Inputs.values())
		ModOp  = Op(self.Implementation.ServiceName, InputList=InputDatas)
		
#		print("[BlackBoxFunction] args:", args)
#		print("[BlackBoxFunction] kwargs:", kwargs)
#		input()
		ListArgs=[x.SyntheSys__PythonVar for x in args]
		#DictArgs={k:v.SyntheSys__PythonVar for k,v in kwargs.iteritems()}
		DictArgs={}
		for k,v in kwargs.items():
			DictArgs[k]=v.SyntheSys__PythonVar

		for i, (ArgName, ArgDefaultValue) in enumerate(self.Implementation.Inputs.items()):
			if i<(len(args)): continue
			if ArgName in DictArgs: continue
			D=Data(Name=ArgName, PythonVar=ArgDefaultValue, Operation=None, Parents=[])
			DictArgs[ArgName]=D
			InputDatas.append(D)
		# Return output not in arguments
		ToReturnDatas = []
		
		HighLevelModule.NO_WRAPPING=True
		ValuesReturned=self._Algorithm(*ListArgs, **DictArgs)
		HighLevelModule.NO_WRAPPING=False
		HighLevelModule.DATAFLOW_TRACKING=False
#		print("ValuesReturned:", ValuesReturned)
#		HighLevelModule.DATAFLOW_TRACKING=False
		if isinstance(ValuesReturned, tuple):
			for i, Val in enumerate(ValuesReturned):
				Name=ROutputs.pop()
				S = Data(Name=Name, PythonVar=Val, Operation=ModOp, Parents=InputDatas)
				ToReturnDatas.append(S)
		else:
			Name=ROutputs.pop(0)
			S = Data(Name=Name, PythonVar=ValuesReturned, Operation=ModOp, Parents=InputDatas)
			ToReturnDatas.append(S)
			
		# Assign output arguments
		for O in Outputs:
			if O in kwargs:
				S = Data(Name=O, PythonVar=DictArgs[AName], Operation=ModOp, Parents=InputDatas)
				continue
			for A in args:
				if A.SyntheSys__Name==O:
					S = Data(Name=O, PythonVar=ListArgs[args.index(A)], Operation=ModOp, Parents=InputDatas)
					break
					
		if len(ToReturnDatas)==1: return ToReturnDatas[0]
		else: return tuple(ToReturnDatas)
	#--------------------------------------------------------------------
	def SetTBValues(self, ArgDict):
		"""
		Add token-like value to argument data.
		"""
		for DName, D in self.ArgDict.items():
			if not D.AddTBVal(ArgDict[D.Name]): # Add as token
				return False
		return True
	#--------------------------------------------------------------------
	def __call__(self, *args, **kwargs):
		"""
		Callable : launch algorithm function
		"""
		if self.IsBlackBox():
			for a in args+tuple(kwargs.values()):
				if not isinstance(a, Tracer.Tracer):
					return self._Algorithm(*args, **kwargs)
			return self.BlackBoxFunction(*args, **kwargs)
		else:
			return self._Algorithm(*args, **kwargs)
			
#===========================================================================
class Implementation:
	"""
	Represent a black box Implementation with sources.
	"""
	#-------------------------------------------------------------------
	def __init__(self, ServiceName):
		
		if not type(ServiceName)==str:
			logging.error("Argument must be a str representation of a library service.")
			sys.exit(1)
		self.ServiceName=ServiceName
		
		self.Inputs  = {}
		self.Outputs = {}
		
#	#-------------------------------------------------------------------
#	def AddSources(self, Sources=[]):
#		"""
#		Add source files to self._SourceList variable
#		"""
#		if not type(Sources)==list:
#			logging.error("Argument must be a list of paths.")
#			return False
##		logging.debug("SourceList: {0}".format(self._SourceList))
#		self._SourceList+=Sources
#		return True
		
	#-------------------------------------------------------------------
	def SetInterface(self, Inputs={}, Outputs={}):
		"""
		Add source files to self._SourceList variable
		keys are Data names and values are python variables
		"""
		if not (isinstance(Inputs, collections.OrderedDict) and isinstance(Outputs, collections.OrderedDict)):
			logging.error("[{0}] Inputs and Outputs arguments must be ordered dictionaries (keys are Data names and values are python variables)".format(self.ServiceName))
		self.Inputs  = Inputs
		self.Outputs = Outputs
		return 
		
	#--------------------------------------------------------------------
	def InputsInArguments(self, *args, **kwargs):
		"""
		For each argument, return only inputs
		"""
		Inputs=collections.OrderedDict()
		for i, Name in enumerate(self.Inputs):
			if i==len(args): break
			Inputs[Name]=args[i]

		for Name, Sig in kwargs.items():
			if Name in Inputs: raise NameError("Argument '{0}' given twice !".format(Name))
			elif Name in self.Inputs:
				Inputs[Name]=Sig.LastAssignment()	
		return Inputs
		
	#--------------------------------------------------------------------
	def OutputsInArguments(self, *args, **kwargs):
		"""
		For each argument, return only Outputs
		"""
		Outputs=collections.OrderedDict()
		ROutputs=[]
		for i, Name in enumerate(self.Inputs):
			if i==len(args): break
			Outputs[Name]=args[i]
			
		for Name, Sig in kwargs.items():
			if Name in self.Outputs:
				Outputs[Name]=Sig
		for Name, Sig in self.Outputs.items():
			if Name not in kwargs:
				ROutputs.append(Name)
		return Outputs, ROutputs
		
##--------------------------------------------------
#def TimeStamp(Format='%fus'):
#	return datetime.datetime.now().strftime(Format)
	
##--------------------------------------------------
#def MergeDataFlowBranches():
#	"""
#	Merge fork branches of data flow according to Nodes IDs.
#	"""
#	if Tracer.Tracer.ParallelFlow: 
#		# Merge graphs
##		logging.debug("Dump list of instances.")
#		for r in Tracer.Tracer.PipeReads:
#			ParallelInstances = pickle.load(r)
#			Merge(ParallelInstances)
#		for PID in Tracer.Tracer.ForkedIDList:
#			logging.debug("[{0}] Waiting PID '{1}'".format(os.getpid(), PID))
#			os.waitpid(PID, 0)
#		if Tracer.Tracer.PipeWrite!=None:
#			pickle.dump(Tracer.Tracer.ParallelInstances, Tracer.Tracer.PipeWrite)
#		sys.exit(0) # Do not process graph in child process
#	else: 
#		for r in Tracer.Tracer.PipeReads:
#			ParallelInstances = pickle.load(r)
#			Merge(ParallelInstances)
#		# Merge graphs
#		for PID in Tracer.Tracer.ForkedIDList:
#			logging.debug("[{0}] Waiting PID '{1}'".format(os.getpid(), PID))
#			os.waitpid(PID, 0)
#			
			
##===================================================================
#def Merge(ParallelInstances):
#	"""
#	Merge graph nodes according to Node IDs.
#	"""
#	#logging.debug("Load and merge list of instances.")
#	#---
#	#InstancesDict = {x.NodeID(): x for x in Tracer.Tracer.Instances}
#	InstancesDict={}
#	for x in Tracer.Tracer.Instances:
#		InstancesDict[x.NodeID()]=x
#	#---
#	for D in ParallelInstances:
#		ID = D.NodeID()
#		if ID in InstancesDict:
#			InstancesDict[ID].Merge(D)
#		else:
#			Tracer.Tracer.Instances.append(D)
#	#---
	
	

#===========================================================================
def ExtractDataFlow(AlgoFunc, TestBenchFunc, *Args, **Kwargs):
	"""
	Algo analysis (Data flow extraction).
	"""
	Mod=HighLevelModule()
	Mod._Algorithm=AlgoFunc
	Mod._Testbench=TestBenchFunc
#	Mod.__reset__()
	
	HighLevelModule.DATAFLOW_TRACKING=True
#	HighLevelModule.BRANCH_BROWSING=True
	HighLevelModule.RECORD_VALUES=False
	HighLevelModule.NO_WRAPPING=False
	Kwargs["SyntheSys_HighLevelModule"]=Mod
#	print("AlgoFunc:",AlgoFunc)
#	print("TestBenchFunc:",TestBenchFunc)
#	print("Args:",Args)
#	print("Kwargs:",Kwargs)
	RetSig = Mod._Algorithm(*Args, **Kwargs) # Resets Mod._Algorithm.DATAFLOW_TRACKING
#	MergeDataFlowBranches()
	HighLevelModule.NO_WRAPPING=True
	HighLevelModule.DATAFLOW_TRACKING=False
	
	# Now merge equivalent Reduces
#	NewList=[]
#	while(len(Reduce.Instances)>0):
#		P=Reduce.Instances.pop(0)
#		ToBeRemoved=[]
#		for OtherP in Reduce.Instances:
#			if OtherP is P: continue
#			if OtherP.Inputs is P.Inputs:
#				# Merge the two Reduces
#				OtherP.SubstituteBy(P)
#				ToBeRemoved.append(OtherP)
#		for R in ToBeRemoved:
#			R.Remove()
#		NewList.append(P)
#	Reduce.Instances=NewList
	
	return Mod
	
	
	
	
	
