#! /usr/bin/python
"""
Select operations
"""
import logging, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import SyntheSys.SysGen
from SyntheSys.Analysis.Operation import Operation
from SyntheSys.Analysis import Operation as OpMod

#=========================================================
class SelectGroup(Operation):
	Instances=[]
	"""Abstraction of a group of Select tasks"""
	#-------------------------------------------------
	def __init__(self, SelectList=[]):
		"""
		Initialization of the SelectGroup attributes.
		"""
		self._Name      = "SELECT_GROUP"
		SelectGroup.Instances.append(self)
		self.SelectList=SelectList
		self._CStep=None
		self._Module=None
		
		self.EarliestStart=0
		self.LatestStart=0
	#-------------------------------------------------
	@property
	def Outputs(self):
		return [self.GetFinalOutput(),]
	#-------------------------------------------------
	def AddSelect(self, SelectInstance):
		"""
		Add SelectInstance to SelectList if not already.
		"""
		if not SelectInstance in self.SelectList:
			self.SelectList.append(SelectInstance)
			return True
		else:
			return False
	#-------------------------------------------------
	def GetBranchID(self, SourceTask):
		"""
		return BranchID corresponding to provided source task for this select group.
		"""
		BranchID=0
		for Sel in self.SelectList:
			for Input in Sel.GetInputs():
				InputTask=Input.SyntheSys__Producer
				if SourceTask is InputTask:
					return BranchID
				if not InputTask.IsSelect(): BranchID+=1
		raise TypeError("[DataFlow.SelectGroup.GetBranchID] Given source task '{0}' does not provide data to '{1}'.".format(SourceTask, self))
	#--------------------------------------------------------------------
	def GetFinalOutput(self):
		"""
		RETURN final output task of select list.
		"""
		for SelectInstance in self.SelectList:
			O=SelectInstance.GetSelectOutput()
#			print("O:",O)
#			print("O.GetConsumers():", O.GetConsumers())
			Consumers=O.GetConsumers()
			if len(Consumers)==0: return O
			for D, OpList in Consumers:
#				print("OpList:", OpList)
				if OpList:
					for Op in OpList:
						if Op in self.SelectList: continue
						else: return D
				else: return D
		logging.error("[SyntheSys.Analysis.SelectGroup.GetFinalOutput] Cannot find final output task of select list."); 
		raise TypeError
	#--------------------------------------------------------------------
	def GetSelectedTasks(self):
		"""
		Return the dictionary {TestedData:[SelectInput0, SelectInput1...]}. 
		Each key corresponds to a "select" task.
		"""
		FinalOutput=self.GetFinalOutput()
		SelectedTasks={}
		for SelectInstance in self.SelectList:
			SrcList=[]
			
			for I in SelectInstance.Inputs:
				SrcList.append(I)
			# TODO : manage the ELSE branch
			Selector=SelectInstance.TestedData
			SelectedTasks[Selector]=SrcList
		return SelectedTasks, FinalOutput
	#--------------------------------------------------------------------
	def GetPreviousTasks(self, SkipBranch=False):
		"""
		Return a list of Operations producing input data.
		"""
		PrecedenceList = []
		for M in self.SelectList:
			for MP in M.GetPreviousTasks(SkipBranch=SkipBranch):
				if MP.IsSelect():
#					if MP.SelectGroup is self.SelectGroup:
#						PrecedenceList.extend(MF.GetPreviousTasks(SkipBranch=SkipBranch))
#					else:
					PrecedenceList.append(MP.SelectGroup)
				else:
					PrecedenceList.append(MP)
					
		# TODO : Add to previous the TestGroup that controls the select group
		
				
		return PrecedenceList
	#--------------------------------------------------------------------
	def GetNextTasks(self, SkipBranch=False):
		"""
		Return a list of Operations consuming output data.
		"""
		FollowingList = []
		for M in self.SelectList:
			for MF in M.GetNextTasks(SkipBranch=SkipBranch):
				if MF.IsSelect():
#					if MF.SelectGroup is self.SelectGroup:
#						FollowingList.extend(MF.GetNextTasks(SkipBranch=SkipBranch))
#					else:
					FollowingList.append(MF.SelectGroup)
				else:
					FollowingList.append(MF)
		
#		print("FollowingList:",[str(f) for f in FollowingList])
		return sorted(list(set(FollowingList)))
#	#--------------------------------------------------------------------
#	def Makespan(self, TaskMapping):
#		"""
#		Calculate the earliest and latest start time for this task.
#		"""
#		TSmin=0
##		print("[{0}] Start Makespan:".format(self))
#		for Successor in self.GetPreviousTasks(SkipBranch=True):
##			print("[{0}]> Previous:".format(self), Successor)
#			STSmin, STSmax=Successor.Makespan(TaskMapping)
#			TSmin=max(TSmin, STSmin+TaskMapping[Successor].Latency)
#				
#		Module=TaskMapping[self]
#		DII=Module.GetDataIntroductionInterval()
##		print("[{0}] DII:".format(self), DII)
#		TSmax=TSmin + DII - 1
##		print("[{0}] found Makespan:".format(self), TSmin, "->",TSmax)
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
		NbOutput=max(1, len(Outputs))
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
		ServName="SelectCtrl"
		if ServName in OpMod.LibServices:
			return OpMod.LibServices[ServName]
		else:
			return None
	#-------------------------------------------------
	def IsSelect(self):
		"""
		Return False
		"""
		return False
	#-------------------------------------------------
#	def IsSelect(self):
#		"""
#		Return False
#		"""
#		return False
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
	def GetInputs(self):
		"""
		Return list of input data
		"""
		#----------
		def GetSelectInput(SelectInstance, RefMG):
			Inputs=[]
			if SelectInstance.SelectGroup is RefMG:
				for Input in SelectInstance.GetInputs():
					if Input.SyntheSys__Producer.IsSelect():
						Inputs.extend(SelectInstance.GetInputs()) 
					else:
						Inputs.append(Input)
			else:
				Inputs.extend(SelectInstance.SelectGroup.GetOutputs())
			return Inputs
		#----------
		
		DataInputs=[]
		for M in self.SelectList:
			for Input in M.GetInputs():
				if Input.SyntheSys__Producer.IsSelect():
					DataInputs.extend(GetSelectInput(SelectInstance=Input.SyntheSys__Producer, RefMG=self))
				else:
					DataInputs.append(Input)
		return DataInputs
	#-------------------------------------------------
	def GetOutputs(self):
		"""
		Return output data of last Select
		"""
		for M in self.SelectList:
			for O in M.GetOutputs():
				if O.SyntheSys__Children:
					for Op, OutputList in O.SyntheSys__Children.items():
						if not Op.IsSelect():
							return OutputList
				else:
					return [O,]
		raise TypeError("[SyntheSys.Analysis.SelectGroup.GetOutputs] No Select output found ! Must be a mistake somewhere...")
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
		return str(self)
	#-------------------------------------------------
	def __lt__(self, Other):
		"""
		Operation: <
		"""
		return False
	#-------------------------------------------------
	def __repr__(self):
		"""
		return string representation.
		"""
		return "SelectGroup(SelectList={0})".format(repr(self.SelectList))
	#-------------------------------------------------
	def __str__(self):
		"""
		return string representation.
		"""
		return "SelectGroup[{0}]".format(SelectGroup.Instances.index(self))

#=========================================================
		
	
	
	
	
	
	
	
	
		
		
