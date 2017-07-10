#! /usr/bin/python

"""
Create an Operation when any data is consumed and/or any is produced:
	1. a signal Operation attributes (built in Operators)
	2. a method where Data Operation is called

"""
import logging, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import SyntheSys.SysGen
from Utilities.Misc import SyntheSysError
# For finding parent calling method in a method:
# import inspect
# print 'caller name:', inspect.stack()[1][3]
from SyntheSys.SysGen import XmlLibManager
LibServices=None
XMLLIB=None

#=================================================================
def InitLibrary():
	"""
	Initialize LibServices global variables with the list of 
	Service found in library.
	"""
	global LibServices, XMLLIB
	XMLLIB=XmlLibManager.XmlLibManager(SyntheSys.SysGen.BBLIBRARYPATH)
	LibServices=XMLLIB.ListServices()
		
#=========================================================
class Operation:
	OpNumber=0
	Instances=[]
	Selector=None
	""" 
	Abstraction of generic Operations.
	Object for synchronous data flow representation/simulation.
	"""		
	#-------------------------------------------------
	def __init__(self, Name="UnknownOperation", InputList=[], ExtraArg={}, AlgoFunction=None):
		"""
		Initialization of the Operation attributes.
		"""
		self._Name      = Name
		
		self._CStep     = None # For scheduling

		if Operation.Selector is None or self.IsSwitch():
			self.Inputs     = InputList
		else: 
			self.Inputs=[]
#			print("For one input chain:")
			TestGroup=Operation.Selector[3]
			if not(TestGroup is None):
				if self.IsSelect() or self.IsSwitch(): pass
				else:
					TestGroup.SetTest(TestedData=Operation.Selector[0], Position=Operation.Selector[4])
			for I in InputList:
#				print("> Sel:", S.GetSwitched(Operation.Selector[1]))
#				input()
				S=I.DataSelection(Operation.Selector[0], Operation.Selector[2], TestGroup=TestGroup)
				self.Inputs.append(S.GetSwitched(Operation.Selector[1]))
				
		self.Outputs    = []
		self.ExtraArg   = ExtraArg
		self.ConstInputs = []
		
		self._AlgoFunction=AlgoFunction
		
		try:    self._Symbol = SYMBOL_DICT[Name]
		except: self._Symbol = None
		
		self._Module = None
		self.Node    = None
		
		Operation.Instances.append(self)	
#		logging.debug("New Operation '{0}'".format(self))
		Operation.OpNumber+=1	
		
		self.EarliestStart=0
		self.LatestStart=0
	#-------------------------------------------------
	def GetName(self):
		"""
		Return __name__ attribute
		"""
		return self._Name
	#-------------------------------------------------
	def TypeSignature(self):
		"""
		return input types
		"""
		if len(self.Inputs)>0:
			Types=[]
			for D in self.Inputs:
				if D.SyntheSys__Container is None:
					Types.append(type(D.SyntheSys__PythonVar))
				else:
					Types.append(type(D[0].SyntheSys__PythonVar))
			return tuple(Types)
		else:
			return None
	#-------------------------------------------------
	def IsSelect(self):
		return False
	#-------------------------------------------------
	def IsSwitch(self):
		return False
	#-------------------------------------------------
	def GetService(self, Constraints=None):
		"""
		Return service corresponding to name and argument types.
		"""
		global LibServices
		ServName=None
		if self._Name in ["INPUT", "OUTPUT"]:
			if Constraints is None:
				ServName="SimuCom"
			else:
				return Constraints.GetCommunicationService(ServDict=LibServices)
#		elif self._Name=="SELECT" :
#			ServName="CtrlDepManager"
		else:
			ServName=self._Name
			
#		print("ServName:", ServName)
#		print("LibServices:", "\n".join(sorted([S for S in LibServices])))
#		for I in self.Inputs:
#			print("I:", I)
#			print("I:", I.SyntheSys__PythonVar)
#			input()
		if ServName in LibServices:
			return LibServices[ServName]
		else:
			logging.warning("[SyntheSys.Operation.GetService] No such service {0}.".format(ServName))
			raise TypeError
			return None
	#-------------------------------------------------
	def IsInput(self):
		"""
		Return True if operation is an input task, false otherwise.
		"""
		if self._Name == "INPUT": return True
		else: return False
	#-------------------------------------------------
	def IsOutput(self):
		"""
		Return True if operation is an output task, false otherwise.
		"""
		if self._Name == "OUTPUT": return True
		else: return False
	#-------------------------------------------------
	def GetInputs(self, TestedData=True):
		"""
		Return list of input data
			Ignore option TestedData (only used in overloaded functions)
		"""
#		Serv=self.GetService()
#		BBItf=Serv.GetInterfaces("BasicBlock", Direction="IN")[0]
#		InputList=[]
#		for I in self.Inputs:
#			print("   D:", str(D))
#			for D in BBItf.DataList:
#				print("      I:", str(I))
#				if D.Name==I.Name:
#					InputList.append(I)
#		print(self)
#		print("InputList:", InputList)
#		input()
#		return InputList

		return self.Inputs
	#-------------------------------------------------
	def GetOutputs(self):
		"""
		Return list of output data
		"""
		return self.Outputs
	#-------------------------------------------------
	def GetSymbol(self):
		"""
		Return symbol representation of operation (+, -, *, etc)
		"""
		return self._Symbol
	#-------------------------------------------------
	def GetOutputName(self, ShowID=False):
		"""
		Return output representation with Operation symbol
		"""	
		if self._Symbol:
			if len(self.Inputs)>1:
				InputNames=[x.NodeID(ShowID) for x in self.Inputs]
#				if self.IsSwitch():
				return self._Symbol.join(InputNames)
			else:
				return None
		else: 
			return "{0}({1})".format(self._Name.replace('_',''), ','.join([x.NodeID(ShowID) for x in self.Inputs]))
	#-------------------------------------------------
	def GetOutputProperty(self, Property):
		"""
		Return specified property value
		"""
		if Property=="Type":
			if self._Name in OUTPUT_TYPES_DICT:
				return OUTPUT_TYPES_DICT[self._Name](*self.Inputs, **self.ExtraArg)
			else:
				return None
			
		elif Property=="Size":
			if self._Name in OUTPUT_SIZE_DICT:
				return OUTPUT_SIZE_DICT[self._Name](*self.Inputs, **self.ExtraArg)
			else:
				return None
		
		else:
			logging.error("[GetSize] Unsupported type '{0}'".format(PTypes[0]))
	#-------------------------------------------------
	def GetName(self):
		"""
		Return __name__ attribute
		"""
		return self._Name
	#-------------------------------------------------
	def GetSymbol(self):
		"""
		Return _Symbol attribute
		"""
		return self._Symbol
	#--------------------------------------------------------------------
	def GetPreviousTasks(self, SkipBranch=False):
		"""
		Add a list of Operations producing input data.
		"""
		PrecedenceList = []
		for I in self.Inputs: 
			Task = I.SyntheSys__Producer
			if Task is None: continue

			if SkipBranch is False and Task.IsSwitch():
#				if Task in PrecedenceList : pass
#				else: 
				PrecedenceList.append(Task.TestGroup)
			elif SkipBranch is False and Task.IsSelect():
#				if Task in PrecedenceList : pass
#				else: 
#					if self.IsSelect():
#						if self.SelectGroup is Task.SelectGroup:
#							PrecedenceList+=Task.GetPreviousTasks(SkipBranch=SkipBranch)
#						else:
#							PrecedenceList.append(Task.SelectGroup)
#					else:
				PrecedenceList.append(Task.SelectGroup)
#				for T in Task.GetPreviousTasks(SkipBranch=SkipBranch):
#					PrecedenceList.append(T)
			#PrecedenceList.append(None);continue
			elif Task.GetName()=="__setitem__":
				PrecedenceList+=Task.GetPreviousTasks(SkipBranch=SkipBranch)
			else:
				PrecedenceList.append(Task)
		return PrecedenceList
	#--------------------------------------------------------------------
	def AddNextTask(self, Task):
		"""
		Add an operator as producing output data.
		"""
		self.Outputs.extend(Task.GetInputs())
		return True
	#--------------------------------------------------------------------
	def GetNextTasks(self, SkipBranch=False):
		"""
		Add a list of Operations consuming output data.
		"""
		FollowingList = []
		
		if self.IsSwitch(): Outputs=self.Outputs.values()
		else: Outputs=self.Outputs
		
		for T in Outputs:
			if T is None: continue
#			if len(T.SyntheSys__Children)==0: FollowingList.append(None); continue
			else:
				for Task, CList in T.SyntheSys__Children.items():
					if SkipBranch is False and (Task.IsSwitch() or Task.IsSelect()):
						if Task.IsSwitch():
							FollowingList.append(Task.TestGroup)
						else:
							if self.IsSelect():
								if self.SelectGroup is Task.SelectGroup:
									for T in Task.GetNextTasks(SkipBranch=SkipBranch):
										FollowingList.append(T)
								else:
									FollowingList.append(Task.SelectGroup)
									
							else:
								FollowingList.append(Task.SelectGroup)
					elif Task.GetName()=="__setitem__":
						FollowingList+=Task.GetNextTasks(SkipBranch=SkipBranch)
					else:
						FollowingList.append(Task)
		return list(set(FollowingList))
#		return sorted(list(set(FollowingList)))
	#--------------------------------------------------------------------
	def ResetStartTimes(self):
		"""
		Initialise to 0 EarliestStart and LatestStart attributes.
		"""
		self.EarliestStart, self.LatestStart = 0, 0
	#--------------------------------------------------------------------
	def RecurseNextSetupEarliestStart(self, TaskMapping, Sched):
		for Successor in self.GetNextTasks(SkipBranch=False):
			Successor.SetupEarliestStart(TaskMapping, Sched)
		for Successor in self.GetNextTasks(SkipBranch=False):
			Successor.RecurseNextSetupEarliestStart(TaskMapping, Sched)
	#--------------------------------------------------------------------
	def SetupEarliestStart(self, TaskMapping, Sched, FpgaDesign=None):
		"""
		Calculate the earliest start time for this task.
		 ! Must be called after all previous task's earliest starts have been calculated.
		"""
		if self.EarliestStart>0: return self.EarliestStart # Already processed
#		print("# ", self, '(CStep={0})'.format(self._CStep), ":")
		# Process delay (for shared IP)------------
		CurMod=TaskMapping[self]
		Delay=0
#		print(",".join(str(x) for x in Sched[CurMod]))
		if CurMod in Sched:
			if self in Sched[CurMod]:
				Index=int(self._CStep%max(CurMod.Latency,1))
	#			print("Index:", Index)
				for t in Sched[CurMod][Index:Sched[CurMod].index(self)]:
					if t is None or t is self: continue
	#				print(t, "is not", self)
	#				print("  >t:", t, '(CStep={0})'.format(t._CStep))
					if t._CStep==self._CStep:
						Delay+=CurMod.Latency
		self.EarliestStart+=Delay
		#------------------------------------------
		for Predecessor in self.GetPreviousTasks(SkipBranch=False):
#			print("\tPredecessor :", Predecessor, "-->", Predecessor.EarliestStart)
			Mod=TaskMapping[Predecessor]
#			print("\t1 Lat:", Mod.Latency)
			Lat=Mod.Latency
			PredecessorStart=Predecessor.EarliestStart
			# Process communication latency------------
			if FpgaDesign is None:
				ComLatency=0
			else:
				ComLatency=FpgaDesign.ComLatency(Mod, CurMod)
				
			self.EarliestStart=max(self.EarliestStart, PredecessorStart+Lat+ComLatency) # Max des Minimum des précédents
#			print("\tself.EarliestStart :", self.EarliestStart)
#		print("EarliestStart of {0}:".format(self), self.EarliestStart)
		
		return self.EarliestStart
	#--------------------------------------------------------------------
	def SetupLatestStart(self, TaskMapping, OutputTask):
		"""
		Calculate the latest start time for this task.
		 ! must be called after SetupEarliestStart()
		"""
#		print("SetupLatestStart:", self)
		if self.LatestStart>0: return self.LatestStart # Already processed
		if self is OutputTask:
			self.LatestStart = self.EarliestStart
			if self.LatestStart==0: 
				Msg="Overall latency is null... unable to get latest start time. Please setup EarliestStart first !"
				logging.error(Msg)
				raise SyntheSysError(Msg)
		else:
			SuccMinLatestStart=float('inf')
			for Successor in self.GetNextTasks(SkipBranch=False):
#				print("Successor:",Successor) 
				Lat=TaskMapping[Successor].Latency
		
				if Successor.LatestStart==0: Successor.SetupLatestStart(TaskMapping, OutputTask) # Already processed
				SuccMinLatestStart=min(SuccMinLatestStart, Successor.LatestStart) # Max des Minimum des précédents

			self.LatestStart = SuccMinLatestStart - TaskMapping[self].Latency
#		print("SetupLatestStart of {0} : ".format(self), self.LatestStart)
#		print("    with succ:", [str(op) for op in self.GetNextTasks(SkipBranch=True)])
		
		for Predecessor in self.GetPreviousTasks(SkipBranch=False):
#			print("Predecessor:",Predecessor)
			Predecessor.SetupLatestStart(TaskMapping, OutputTask)
		
#		DII=CurModule.GetDataIntroductionInterval()
#		TSmax=TSmin + DII - 1

#		print("[{0}] DII:".format(self), DII)
	#--------------------------------------------------------------------
	def Makespan(self):
		"""
		Return the earliest and latest start time attributes previously setup for this task.
		"""
#		print("[{0}] Makespan:".format(self), self.EarliestStart, "->", self.LatestStart)
#		input()
		return self.EarliestStart, self.LatestStart
	#--------------------------------------------------------------------
	def Schedule(self, CStep, Module):
		"""
		Set CStep attribute.
		"""
		if Module is None:
			logging.error("[Schedule] No module specified.")
			return 
		self._CStep=CStep
		self._Module=Module
	#--------------------------------------------------------------------
	def Unschedule(self):
		"""
		Set CStep attribute to None.
		"""
		self._CStep=None
		self._Module=None
	#--------------------------------------------------------------------
	def IsScheduled(self):
		"""
		return True if a CStep is assigned to this operation.
		"""
		return self._CStep is not None
	#--------------------------------------------------------------------
	def GetStartTime(self):
		"""
		return self._CStep attribute.
		"""
		return self._CStep
	#--------------------------------------------------------------------
	def PortSimilarity(self, TaskList):
		"""
		Port similarity represents the bit-width similarity between 
		the input ports of two compatible operations. 
		The larger the port similarity, the more shared hardware 
		utilization will be, and the more hardware area can be saved.
		"""
		SimSum=0
		NbInput=len(self.Inputs)
		for T in TaskList:
			if T is self: continue
			Sizes=[(self.Inputs[i].Size, T.Inputs[i].Size) for i in range(NbInput)]
			Ratios=[min(SelfS, OtherS)/max(SelfS, OtherS) for (SelfS, OtherS) in Sizes]
			Sim=sum(Ratios)/NbInput
			SimSum+=Sim
		return SimSum
	#--------------------------------------------------------------------
	def SourceSimilarity(self, TaskList):
		"""
		Common sources can reduce the multiplexer and routing resources 
		when the two operations are shared.
		"""
		SimSum=0
		
		NbInput=len(self.Inputs)
		for T in TaskList:
			if T is self: continue
			CommonSources=0
			for i in range(NbInput):
				if self.Inputs[i] is T.Inputs[i]:
					CommonSources+=1
			SimSum+=CommonSources
			
		return SimSum/NbInput
	#--------------------------------------------------------------------
	def SinkSimilarity(self, TaskList):
		"""
		Common sink operations can reduce the routing resources 
		when the two operations are shared.
		Sharing with lower a sink similarity requires a longer routing net.
		"""
		SimSum=0
		
		NbOutput=len(self.Outputs)
		for T in TaskList:
			if T is self: continue
			CommonSources=0
			for i in range(NbOutput):
				if self.Outputs[i] is T.Outputs[i]:
					CommonSources+=1
			SimSum+=CommonSources
			
		return SimSum/NbOutput
	#--------------------------------------------------------------------
	def DepSatisfied(self):
		"""
		Return True if Previous operation are scheduled.
		"""
		for Task in self.GetPreviousTask(): 
			if Task is None:
				pass
			elif not Task.IsScheduled():
				return False
		return True
	#--------------------------------------------------------------------
	def SetModule(self, Module):
		"""
		Save module to where task is mapped.
		"""
		self._Module=Module
		return True
	#--------------------------------------------------------------------
	def GetModule(self):
		"""
		Return module to where task is mapped.
		"""
		return self._Module
	#-------------------------------------------------
	def GetStim(self):
		"""
		Return list of input stimuli
		"""
		Stim=[]
		for I in self.Inputs:
			Stim.append(I.GetTBValues()[:])
		return Stim
#	#--------------------------------------------------------------------
#	def ConsumeToken(self):
#		"""
#		?
#		"""
#		pass
#	#--------------------------------------------------------------------
#	def ProduceToken(self):
#		"""
#		?
#		"""
#		pass
	#-------------------------------------------------
#	def __hash__(self):
#		"""
#		Return unique identifier from string.
#		"""
#		print(self, "=>", hash(str(self)))
#		return hash(str(self))
	#---------------------------------------------------------------------------------------------------
	# COMPARATORS
	#---------------------------------------------------------------------------------------------------
	def __lt__(self, Other):
		"""
		Operation: <
		"""
		if not isinstance(Other, Operation):
			return True
		else:
			return Operation.Instances.index(self) < Operation.Instances.index(Other)
	#---------------------------------------------------------------------------------------------------
	# DISPLAY
	#-------------------------------------------------
	def __repr__(self):
		"""
		Return symbol of Operation if present, else name
		"""
#		"<Operation({0}[{1}])>".format(self._Name, Operation.Instances.index(self))
		return "SyntheSys.DataFlow.Operation(Name={0}, InputList={1}, ExtraArg={2}, AlgoFunction={3})".format(repr(self._Name), repr(self.Inputs), repr(self.ExtraArg), repr(self._AlgoFunction))
	#-------------------------------------------------
	def __str__(self):
		"""
		Return symbol of Operation if present, else name
		"""
#		if self._Symbol!=None: return self._Symbol
#		else: 
		return "   {0}[{1}]  ".format(self._Name, Operation.Instances.index(self))
		
#=========================================================
def ResetOperations():
	"""
	Re-Initialization of the class attributes.
	"""
	Operation.OpNumber=0
	Operation.Instances=[]
			
#=========================================================
SYMBOL_DICT={
		"__setitem__": None,
		"__getitem__": None,
		"__lt__":      "<",
		"__le__":      "<=",
		"__eq__":      "==",
		"__ne__":      "!=",
		"__gt__":      ">",
		"__ge__":      ">=",
		"__add__":     "+",
		"__sub__":     "-",
		"__mul__":     "*",
		"__truediv__": "/",
		"__div__":     "/",
		"__init__":    None, # Memory init for list typed Datas
}

STANDARD_TYPES=list(SYMBOL_DICT.keys())


#=========================================================
OUTPUT_TYPES_DICT={
		"__getitem__": lambda *x, **y: x[0].SyntheSys__Container[y["Key"]].GetProperty()["Type"],
		"__setitem__": lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__lt__":      lambda *x, **y: bool(),
		"__le__":      lambda *x, **y: bool(),
		"__eq__":      lambda *x, **y: bool(),
		"__ne__":      lambda *x, **y: bool(),
		"__gt__":      lambda *x, **y: bool(),
		"__ge__":      lambda *x, **y: bool(),
		"__add__":     lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__sub__":     lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__mul__":     lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__truediv__": lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__div__":     lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__pow__":     lambda *x, **y: x[0].LastAssignment().GetProperty()["Type"],
		"__init__":    lambda *x, **y: type(y["InitValue"]), # Memory init for list typed Datas
}

#=========================================================
OUTPUT_SIZE_DICT={
		"slice":       lambda *x, **y: x[1]-x[0],
		"__add__":     lambda *x, **y: max(*[i.GetSize() for i in x])+1,
		"__sub__":     lambda *x, **y: max(*[i.GetSize() for i in x])+1,
		"__mul__":     lambda *x, **y: max(*[i.GetSize() for i in x])*2, # TODO: fix
		"__truediv__": lambda *x, **y: max(*[i.GetSize() for i in x]),
		"__div__":     lambda *x, **y: max(*[i.GetSize() for i in x]),
		"__pow__":     lambda *x, **y: sum(*[i.GetSize() for i in x])+1,
		"__init__":    lambda *x, **y: y["InitValue"], # Memory init for list typed Datas
}

	
		
		
		
		
		
		
		
		
		
		
		
