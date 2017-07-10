#! /usr/bin/python
"""
Test groups
"""
import logging, os, sys

import SyntheSys.SysGen
from SyntheSys.Analysis.Switch import SwitchOperation
from SyntheSys.Analysis.Operation import Operation
from SyntheSys.Analysis import Operation as OpMod

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "SyntheSys.SysGen")))
import SyntheSys.SysGen
import collections

#=========================================================
class TestGroup(Operation):
	Instances=[]
	""" 
	Abstraction of list of test.
	Object for grouping tests/selectors.
	"""		
	#-------------------------------------------------
	def __init__(self, TestChain, Selectors, SelectGroup=None):
		"""
		Initialization of the Operation attributes.
			TestChain   = {Position:TestedData,}
			SelectGroup = instance of SelectGroup
			Selectors   = {Selector:Switch,}
			_CStep      = control step (integer or None)
		"""
		self._Name      = "TEST_GROUP"
		TestGroup.Instances.append(self)
		self.TestChain=TestChain
		self.SelectGroup=SelectGroup
		self.Selectors=collections.OrderedDict()
		self._CStep=None
		
		self.EarliestStart=0
		self.LatestStart=0
	#-------------------------------------------------
	def GetTestedDataFrom(self, T):
		"""
		Return Index and TestedData if one of the input tested Data comes from the given task T.
		Otherwise return None tuple.
		"""
		for Position, TestedData in self.TestChain.items():
			if TestedData.SyntheSys__Producer is T:
				return Position, TestedData
		return None, None
	#-------------------------------------------------
	def NbSwitchedData(self):
		"""
		"""
		return len(self.TestChain)
	#-------------------------------------------------
#	def AddSwitch(self, Selector, SwitchOp):
#		"""
#		Add given switch to the Switches attribute.
#		"""
#		self.Switches[Selector]=SwitchOp
#		return True
	#-------------------------------------------------
	def SetTest(self, TestedData, Position):
		"""
		Add TestedData to TestList at given position
		"""
		if Position in self.TestChain: 
			raise NameError("[TestGroup] Position already set")
		self.TestChain[Position]=TestedData
		return 
	#-------------------------------------------------
	def GatherSelectors(self):
		"""
		Update list of selectors
		"""
#		print("GatherSelectors")
#		print("self.TestChain:",self.TestChain)
#		input()
		# Setup dict of Sel:Data
		for Pos, TD in self.TestChain.items():
			for Sel in SwitchOperation.Instances:
				if Sel.Selector is TD:
					try: self.Selectors[TD].append(Sel)
					except: self.Selectors[TD]=[Sel,]
		return 
	#-------------------------------------------------
	def GetSelectors(self):
		"""
		return list of select operators
		"""
		SelList=[]
		for TD, SList in self.Selectors.items():
			SelList.extend(SList)
		return SelList
	#--------------------------------------------------------------------
	def GetPreviousTasks(self, SkipBranch=False):
		"""
		Return a list of Operations producing input data.
		"""
		PrecedenceList = []
		for TestedData in self.TestChain.values(): 
			Task = TestedData.SyntheSys__Producer
			if Task is None: continue
			elif SkipBranch is True and (Task.IsSwitch() or Task.IsSelect()):
				for T in Task.GetPreviousTasks(SkipBranch=SkipBranch):
					PrecedenceList.append(T)
			elif Task.GetName()=="__setitem__":
				PrecedenceList+=Task.GetPreviousTasks(SkipBranch=SkipBranch)
			else:
				PrecedenceList.append(Task)
				
		# TODO : add Switched data too
		for Sel in SwitchOperation.Instances:
			if not (Sel.TestGroup is self): continue
			for SelectedInput in Sel.Inputs:
				if SelectedInput.SyntheSys__Producer is None: continue
				elif SkipBranch is True and (SelectedInput.SyntheSys__Producer.IsSwitch() or SelectedInput.SyntheSys__Producer.IsSelect()):
					for Prev in SelectedInput.SyntheSys__Producer.GetPreviousTasks(SkipBranch=SkipBranch):
						PrecedenceList.append(Prev)
				else:
					PrecedenceList.append(Prev)
#		print("PrecedenceList:", sorted(PrecedenceList))
#		input()
		return sorted(PrecedenceList)
	#--------------------------------------------------------------------
	def GetNextTasks(self, SkipBranch=False):
		"""
		Return a list of Operations consuming output data.
		"""
		FollowingList = []
#		for TestedData in self.TestChain.values():
		for Sel in SwitchOperation.Instances:
			if not (Sel.TestGroup is self): continue
			for SelectedOutput in Sel.Outputs.values():
				for SelData, ConsumerList in SelectedOutput.GetConsumers(IncludeControl=False):
					for Task in ConsumerList:
						if SkipBranch is True and (Task.IsSwitch() or Task.IsSelect()):
							for T in Task.GetNextTasks(SkipBranch=SkipBranch):
								FollowingList.append(T)
						elif Task.GetName()=="__setitem__":
							FollowingList+=Task.GetNextTasks()
						else:
							FollowingList.append(Task)
			
#		print("FollowingList:", sorted(FollowingList))
#		input()				
		return sorted(list(set(FollowingList)))
	#--------------------------------------------------------------------
	def GetSwitchedTasks(self):
		"""
		Return the dictionary {InputData:[TargetTask0, TargetTask1...]}
		"""
		SwitchedTasks=collections.OrderedDict()
		for Selector, SWList in self.Selectors.items():
			SwitchedTasks[Selector]=collections.OrderedDict()
			for SW in SWList:
				SwitchedTasks[Selector][SW.InputData]=[NT for NT in SW.GetNextTasks(SkipBranch=True)]
#				print("Selector:", Selector)
#				print("SW.InputData:", SW.InputData)
#				print("NextTasks:", [NT._Name for NT in SW.GetNextTasks(SkipBranch=True)])
#				input()
				# TODO : manage the ELSE branch
		return SwitchedTasks
#	#--------------------------------------------------------------------
#	def Makespan(self, TaskMapping):
#		"""
#		Calculate the earliest and latest start time for this task.
#		"""
#		TSmin=0
#		for Successor in self.GetPreviousTasks(SkipBranch=True):
#			STSmin, STSmax=Successor.Makespan(TaskMapping)
#			TSmin=max(TSmin, STSmin+TaskMapping[Successor].Latency)
#			
#		Module=TaskMapping[self]
#		DII=Module.GetDataIntroductionInterval()
##		print("[{0}] DII:".format(self), DII)
#		TSmax=TSmin + DII - 1
##		print("[{0}] Makespan:".format(self), TSmin, "->",TSmax)
#		
#		return TSmin, TSmax
	#--------------------------------------------------------------------
	def PortSimilarity(self, TaskList):
		"""
		Port similarity represents the bit-width similarity between 
		the input ports of two compatible operations. 
		The larger the port similarity, the more shared hardware 
		utilization will be, and the more hardware area can be saved.
		"""
		SimSum=0
		Inputs=self.GetInputs()
		NbInput=len(Inputs)
		for T in TaskList:
			if T is self: continue
			Sizes=[(Inputs[i].Size, T.GetInputs()[i].Size) for i in range(NbInput)]
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
		
		Inputs=self.GetInputs()
		NbInput=len(Inputs)
		for T in TaskList:
			if T is self: continue
			CommonSources=0
			for i in range(NbInput):
				if Inputs[i] is T.GetInputs()[i]:
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
		Outputs=self.GetOutputs()
		NbOutput=len(Outputs)
		for T in TaskList:
			if T is self: continue
			CommonSources=0
			for i in range(NbOutput):
				if Outputs[i] is T.GetOutputs()[i]:
					CommonSources+=1
			SimSum+=CommonSources
			
		return SimSum/NbOutput
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
	def GetStartTime(self):
		"""
		return self._CStep attribute.
		"""
		return self._CStep
	#-------------------------------------------------
	def GetService(self, AddCommunication=True):
		"""
		Return service corresponding to name and argument types.
		"""
		ServName="CtrlDepManager"
		if ServName in OpMod.LibServices:
			return OpMod.LibServices[ServName]
		else:
			return None
	#-------------------------------------------------
	def IsInput(self):
		"""
		Return False
		"""
		return False
	#-------------------------------------------------
	def IsOutput(self):
		"""
		Return False
		"""
		return False
	#-------------------------------------------------
	def GetInputs(self, TestedData=True):
		"""
		Return list of input data
		"""
		DataInputs=[]
		for Sel in SwitchOperation.Instances:
			if not (Sel.TestGroup is self): continue
			InputData = Sel.Inputs[0]
			Append=True
			for IData in DataInputs:
				if IData is InputData:
					Append=False
			if Append is False: continue
			else: DataInputs.append(InputData)
		if TestedData is True:
			DataInputs.extend(self.TestChain.values())
		return DataInputs
	#-------------------------------------------------
	def GetOutputs(self):
		"""
		Return list of output data
		"""
		Outputs=[]
		for Sel in SwitchOperation.Instances:
			if not (Sel.TestGroup is self): continue
			Outputs.extend(Sel.Outputs.values())
		# TODO : Consider SELECT
		return Outputs
	#-------------------------------------------------
	def GetSWDataIndex(self, InputSWData):
		"""
		return the index of input switched data.
		"""
		for Selector, SWList in self.Selectors.items():
			for i,SW in enumerate(SWList):
				if InputSWData is SW.InputData:
					return i
		logging.error("Data '{0}' not switched by '{1}'.".format(InputSWData, self))
		raise TypeError
	#-------------------------------------------------
	def TypeSignature(self):
		"""
		return empty tuple.
		"""
		return tuple()
	#-------------------------------------------------
	def GetName(self):
		"""
		return string representation.
		"""
		return "TestGroup[{0}]".format(TestGroup.Instances.index(self))
	#-------------------------------------------------
	def __lt__(self, Other):
		"""
		Operation: <
		"""
		return True
	#-------------------------------------------------
	def __repr__(self):
		"""
		return string representation.
		"""
		return "TestGroup(TestChain={0}, Selectors={1}, SelectGroup={2})".format(repr(self.TestChain), repr(self.Selectors), repr(self.SelectGroup))
	#-------------------------------------------------
	def __str__(self):
		"""
		return string representation.
		"""
		return "TestGroup[{0}]".format(TestGroup.Instances.index(self))

#=========================================================
		
#=========================================================
def ReplaceDummyTests(Dummy, TestedData):
	"""
	Replace every occurence of Dummy as a selector by TestedData.
	"""
#	print("[SwitchOperation.Replace] Replace {0} by {1}".format(Dummy, TestedData))
	for TG in TestGroup.Instances:
		for Pos in TG.TestChain.keys():
	#		print("Selector:", S)
			if TG.TestChain[Pos] is Dummy:
	#			print("Found => replace it !")
				TG.TestChain[Pos]=TestedData
				
	for D in TG.TestChain.values():
		D.SyntheSys__Children[TG]=TG.GetOutputs()
#		print("D.SyntheSys__Children:", D.SyntheSys__Children)
#	input()
	return
	
#=========================================================
def GatherSelectors():
	"""
	Update list of selectors for each TestGroup instance
	"""
	# Setup dict of Sel:Data
	for TG in TestGroup.Instances:
		TG.GatherSelectors()
	return 
		
	
	
	
	
	
	
	
	
		
		
