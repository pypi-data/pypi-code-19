#!/usr/bin/python

import os, sys, logging

from lxml import etree

from SysGen.Condition import Condition
from SysGen.Assignment import AssignmentSignal, AssignmentStatement
from functools import reduce
from Utilities.Misc import SyntheSysError
 
#======================================================================
class ProtocolStep:
	#----------
	def __init__(self, DirProto, Label, CtrlDict, SyncCtrl, DataDict, ValList, Interface):
		"""
		Setup parameter and reset counters.
		"""
		self.DirProto=DirProto
		self.Label=Label
		self.Target={}
		self.Target.update(Interface.Mapping)
		self.Ctrl=CtrlDict#self.GetTargets(CtrlDict)
		self.SyncCtrl=SyncCtrl
		AssignedDict={}
		for DName, DInstance in DataDict.items():
			AssignedDict[DName]=AssignmentSignal(DInstance)
		self.Data=AssignedDict#self.GetTargets(AssignedDict)
		self.Interface=Interface
		self.ValList=ValList
		self.Registers={}
#		input("NEW PROTOCOL STEP\nLabel={0}\nCtrl={1}\nData={2}".format(self.Label, self.Ctrl, self.Data))
	#----------
	def AddXMLElmtTo(self, ItfElmt):
		"""
		Add protocol XML element to ItfElmt.
		"""
		XMLElmt=etree.SubElement(ItfElmt, "protocol",  
				         label   = self.Label,
				         signals = ",".join(list(self.Data.keys())+list(self.Ctrl.keys())), 
				         values  = ",".join([str(x) for x in self.ValList]),
				         )
	#---------------------------------------------------------------
	def Copy(self, Interface=None):
		"""
		Return abject with same attributes.
		"""
		if Interface is None: Interface=self.Interface
		Copy=ProtocolStep(
				DirProto=self.DirProto, 
				Label=self.Label, 
				CtrlDict={}, 
				SyncCtrl=self.SyncCtrl.copy(), 
				DataDict={}, 
				ValList=self.ValList[:], 
				Interface=Interface
				)
		Copy.Ctrl=dict((C.GetName(),C) for C in [x.Copy() for x in list(self.Ctrl.values())])
		Copy.Data=dict((D.GetName(),D) for D in [x.Copy() for x in list(self.Data.values())])
		return Copy
	#----------------------------------------------------------------------
	def RemoveData(self):
		"""
		Remove Data signals from current step.
		"""
		DataRemoved=(len(self.Data)!=0)
		for DName, DAssignment in self.Data.items():
			if DName in self.SyncCtrl:
				self.SyncCtrl.pop(DName)
		self.Data={}
		return DataRemoved
	#----------------------------------------------------------------------
	def RemoveCtrl(self):
		"""
		Remove Data signals from current step.
		"""
		for CName, C in self.Ctrl.items():
			if CName in self.SyncCtrl:
				self.SyncCtrl.pop(CName)
		self.Ctrl={}
		return 
	#----------------------------------------------------------------------
	def Reset(self, Direction=None):
		"""
		reset data assignments parameters.
		"""
		for D in list(self.Data.values()):
			D.Reset()
	#----------------------------------------------------------------------
	def GetLabel(self):
		"""
		return step label.
		"""
		return self.Label
	#----------------------------------------------------------------------
	def GetSyncCtrl(self, CtrlName):
		"""
		Return state Name given other step
		"""
		if CtrlName in self.SyncCtrl: return self.SyncCtrl[CtrlName]
		else: return None
	#----------------------------------------------------------------------
	def GetStateName(self, OtherStep=None, AssignedData=None):
		"""
		Return state Name given other step
		"""
		return "{0}{1}".format(self.GetLabel(), ("_"+(OtherStep.GetLabel()) if OtherStep else ""))+("" if not AssignedData else "_"+str(AssignedData))
	#----------------------------------------------------------------------
	def GetTargets(self, SigDict):
		"""
		Return dict of copy of signals with name of target.
		"""
		Targets={}
		for SName, S in SigDict.items():
			if not SName in self.Target: 
				Target=S.Copy()
				Targets[SName]=Target
			else:
				Target=S.Copy()
				Target.SetName(self.Target[SName])
				Targets[Target.GetName()]=Target
		return Targets
	#----------------------------------------------------------------------
	def Complement(self, Interface=None):
		"""
		Replace data/ctrl names by target.
		"""
		PStep=self.Copy(Interface=Interface)
#		PStep.Data={}
		for SName, S in self.Data.items():
			if SName in self.Target:
				Sig=PStep.Data[SName]
				PStep.Data[self.Target[SName]]=Sig
				Sig.SetName(self.Target[SName])
				Sig.Sig.InverseDirection()
				PStep.Data.pop(SName)
#		PStep.Ctrl={}
		for SName, S in self.Ctrl.items():
			if SName in self.Target:
				Sig=PStep.Ctrl[SName]
				PStep.Ctrl[self.Target[SName]]=Sig
				Sig.SetName(self.Target[SName])
				Sig.InverseDirection()
				PStep.Ctrl.pop(SName)
		for k,v in self.Target.items():
			PStep.Target[v]=k
		return PStep
	#----------------------------------------------------------------------
	def GetCtrl(self, Direction=None):
		"""
		return list of control signal.
		"""
		if self.Interface.CurIndex is None: 
			if Direction is None: CtrlList=list(self.Ctrl.values())
			else: CtrlList=[S for S in list(self.Ctrl.values()) if S.Direction==Direction]
		else:
			if Direction is None: CtrlList=[x[self.Interface.CurIndex] for x in list(self.Ctrl.values())]
			else: CtrlList=[S for S in [x[self.Interface.CurIndex] for x in list(self.Ctrl.values())] if S.Direction==Direction]
		return CtrlList
	#----------------------------------------------------------------------
	def GetData(self, Direction=None):
		"""
		return list of Data signal.
		"""
		if Direction is None: return list(self.Data.values())
		else: return [S for S in list(self.Data.values()) if Direction in S.Sig.Direction]
	#----------------------------------------------------------------------
	def HasDataToBeWritten(self):
		"""
		Return True if there is data left to be assigned.
		"""
		ToBeAssigned=[] 
		ToBeAssigned.extend([x for x in self.Data.values() if x.HasNonAssignedBits()])
		return len(ToBeAssigned)>0
	#----------------------------------------------------------------------
	def AddData(self, DataSig, IsRegister=False):
		"""
		Append data assignment to Data dictionary attribute.
		"""
		if IsRegister is True: 
			self.Registers[DataSig.GetName()]=DataSig
		if isinstance(DataSig, AssignmentSignal):
			self.Data[DataSig.GetName()]=DataSig
		else:
			self.Data[DataSig.GetName()]=AssignmentSignal(DataSig)
	#----------------------------------------------------------------------
	def GetInputs(self):
		"""
		return list of input signal.
		"""
		return self.GetCtrl(Direction="IN")+self.GetData(Direction="IN")
	#----------------------------------------------------------------------
	def GetOutputs(self):
		"""
		return list of output signal.
		"""
		return self.GetCtrl(Direction="OUT")+self.GetData(Direction="OUT")
	#----------------------------------------------------------------------
	def HasCtrl(self, Direction=None):
		"""
		return True if Ctrl output list is not empty, false otherwise.
		"""
		return True if len(self.GetCtrl(Direction=Direction))>0 else False
	#----------------------------------------------------------------------
	def HasData(self, Direction=None):
		"""
		return True if data output list is not empty, false otherwise.
		"""
		return True if len(self.GetData(Direction=Direction))>0 else False
	#----------------------------------------------------------------------
	def EnteringConditions(self):
		"""
		return Condition instance => And condition on each ctrl input.
		"""
		ECond=Condition()
		InputStepCtrl=self.GetCtrl(Direction="IN")
		if len(InputStepCtrl)>0:
			ECond.AddANDCond("__eq__", *InputStepCtrl) # Step => Signal1 and Signal2 and...
		return ECond  
	#----------------------------------------------------------------------
	def HasDataToAssign(self):
		"""
		return True if current Data has available bits to be assign false otherwise.
		"""
		# CURRENT STEP DATA
		DataAssignments=self.GetData(Direction="OUT")
#		logging.warning("[AssignSignals:{0}] DataAssignments: {1}".format(self, DataAssignments))
		if len(DataAssignments)==0: 
			logging.debug("[{0}] Nothing to assign in this step".format(self))
			return False
		else:
			for DataToAssign in DataAssignments:
				if DataToAssign.HasNonAssignedBits():
					return True
				else:
					return False
	#----------------------------------------------------------------------
	def HasAssignmentData(self):
		"""
		return True if current output Data has available bits for assignment false otherwise.
		"""
		# CURRENT STEP DATA
		DataAssignments=self.GetData(Direction="IN")
#		logging.warning("[AssignSignals:{0}] DataAssignments: {1}".format(self, DataAssignments))
		if len(DataAssignments)==0: 
			logging.debug("[{0}] Nothing for assignment in this step".format(self))
			return False
		else:
			for DataForAssignment in DataAssignments:
				if DataForAssignment.HasNonAssignedBits():
					return True
				else:
					return False
#	#----------------------------------------------------------------------
#	def AssignSignals(self, AdapterFSM, LastState, SourceProtocol):
#		"""
#		Assign source data to step data.
#		"""
#		# CURRENT PROTOCOl ASSIGNMENTS
#		DataAssignments=self.GetData(Direction="OUT")
##		logging.warning("[AssignSignals:{0}] DataAssignments: {1}".format(self, DataAssignments))
#		if len(DataAssignments)==0: 
#			logging.debug("[{0}] Nothing to assign in this step".format(self))
#			return LastState
#			
#		NewState=LastState
##		SourceProtocol.Reset()
#		for DataToAssign in DataAssignments:
#			# Assign Data D 
#			logging.debug("[{0}] Data to assign: '{1}'".format(self, DataToAssign))
#			D=AssignmentSignal(DataToAssign)
#			if SourceProtocol.AssignFromCurrentSource(D, LastState)==False: 
#				SourceProtocol.SetDirection("OUT")
#				NewState=self.AssignData(AdapterFSM, LastState, D, SourceProtocol)
#				SourceProtocol.SetDirection("IN")
#				LastState=NewState
#			
#		return NewState	 
#	#----------------------------------------------------------------------
#	def AssignData(self, AdapterFSM, LastState, DataToAssign, SourceProtocol):
#		"""
#		Assign source data to step data.
#		"""
#		NewState=LastState
##		NbStatesCreated=0
#		while(DataToAssign.HasNonAssignedBits()):
#			StepName=self.GetStateName(SourceProtocol.CurrentStep(), AssignedData=DataToAssign)
#			logging.info("{0} assignment => Get source...".format(DataToAssign))
#			#----------------Get sources for this assignment-------------------
#			Sources, NewState=SourceProtocol.AssignFromNextSource(AdapterFSM, LastState, StepName=StepName+"_{0}".format(DataToAssign), ProtocolDest=self.Proto)
#			if len(Sources)==0: 
#				return NewState
#			else:
#				logging.debug("Source for assignment: '{0}'".format(Sources))
#			#------------------Get step entering condition----------------------
##			ECond=self.EnteringConditions()#+SourceProtocol.CurrentStep().EnteringConditions()
##			logging.warning("[{0}] Entering condition: '{1}'".format(self, ECond))
##			#-----------------Get states for this Step--------------------------
##			NewState=AdapterFSM.AddState(Previous=LastState, Cond=ECond, Name="{0}_{1}".format(StepName, NbStatesCreated))
#			LastState=NewState
#			#-----------------------Assign data---------------------------------
#			Assignments=DataToAssign.AssignTo(map(lambda x: AssignmentSignal(x), Sources))
#			for S0,S1 in Assignments:
#				if S0!=None: # Enough place for Sources in D 
#					logging.debug("Assign '{0}' to '{1}' in '{2}'".format(S1, S0, NewState))
#					NewState.AddAssignment([(None, [(S0,S1),]),])
#			#----------Don't forget to assign output control signals----------
#			for C in self.GetCtrl(Direction="OUT"):#+SourceProtocol.CurrentStep().GetOutputCtrlSignals():
#				C_HDL=C.HDLFormat()
#				C_HDL.Value=1
#				NewState.AddAssignment([(None, [(C_HDL, C_HDL.Value),]),])
#			#--------------------------------------------------------------------
##			NbStatesCreated+=1
#			
#		return NewState
	#----------------------------------------------------------------------
	def AssignDataFrom(self, SrcStep, SrcProt=None, Cond=None):
		"""
		Assign source data to step data.
		return list of Data signal with associated assignments.
		"""
#		if SrcProt is None: pass
#		else: 
#			SrcStep=SrcProt.CurrentStep()
#			while len(SrcStep.GetData(Direction="OUT"))==0:
#				SrcStep=SrcProt.Next()
		Assignments=AssignmentStatement()
#		NbStatesCreated=0
		Regs=[]
		for DIn in self.GetData("IN"):
			if DIn.GetName() in self.Registers: Regs.append(DIn.Sig)
			logging.info("{0} assignment => Get source...".format(DIn))
			#----------------Get sources for this assignment-------------------
			for DOut in SrcStep.GetData("OUT"):
				if DOut.GetName() in SrcStep.Registers: Regs.append(DOut.Sig)
#				logging.debug("Source for assignment: '{0}'".format(DOut))
				if not DOut.HasNonAssignedBits(): continue
				A=DOut.AssignTo(DIn)
				if not A is None:
					Assignments.Add(
						Assignee=A, 
						Assignor=None, 
						Cond=Cond)
				else:
					logging.error("Failed to assign '{0}' to '{1}'".format(DOut, DIn))
					
				if not DOut.HasNonAssignedBits():
					return Assignments, Regs
			#--------------------------------------------------------------------
#			NbStatesCreated+=1
		return None, Regs
	#----------------------------------------------------------------------
	def __repr__(self):
		"""
		Return string representation.
		"""
		return "ProtocolStep(DirProto={0}, Label={1}, CtrlDict={2}, SyncCtrl={3}, DataDict={4}, ValList={5}, Interface={6}))".format(repr(self.DirProto), repr(self.Label), repr(self.Ctrl), repr(self.SyncCtrl), repr({DName:A.Sig for DName, A in self.Data.items()}), repr(self.ValList), repr(self.Interface))
	#----------------------------------------------------------------------
	def __str__(self):
		"""
		Return string representation.
		"""
		return self.Label+"("+str(tuple(self.Ctrl.keys())+tuple(self.Data.keys()))+"):"+str(self.SyncCtrl)	
					
		
#======================================================================
class DirectedProtocol:
	#----------------------------------------------------------------------
	def __init__(self, Interface, Name="UnknownDirectedProtocol"):
		"""
		Setup parameter and reset counters.
		"""
		self.__name__=Name
#		logging.debug("Create a new DirectedProtocol instance '{0}', direction '{1}'".format(self.__name__, Direction))
		self.Interface=Interface
		self.DataDict={}
		self.CtrlDict={}
		self.Registers={} # Pair of Data : [RegAssignment, ...]
		self.RegValues={} # Pair of RegName : RegValue
		self.RegisterAssignments={}
		
		self.GetSignalDict()
#		for DataName, RDictList in Registers.iteritems():
#			self.Registers[DataName]=map(lambda x: x["Signal"], RDictList) 
#		self._Direction=Interface.Direction
		self._CurrentStepIndex=0
		self._CurrentIndex=None
		self._Steps=[]
		self.AddRegisters(Interface.Registers, Interface.Mapping, Interface.Direction, Interface.CurIndex)
		self._SerializationFactor=1
#		input("NEW DirectedProtocol\Name={0}".format(Name))
	#------------------------------------
	def SetFromXML(self, XMLElements):
		"""
		Get parameters from XML description.
		"""
		for ProtocolElmt in XMLElements:
			Attr = ProtocolElmt.attrib
			L=Attr.get("label")
			P=Attr.get("position")
			SigString=Attr.get("signals")
			ValString=Attr.get("values")
			if SigString is None:
				try: self.AddNewStep(Label=L, CtrlDict={}, DataDict={}, ValList={})
				except: 
					Msg="Unable to create protocol step '{0}'.".format(L)
					logging.error(Msg)
					raise SyntheSysError(Msg)
			else:
				# Get list of signals:
				SigList=[x.strip() for x in SigString.split(',')]
				while "" in SigList: SigList.remove("")
				
				# Get list of values:
				if ValString is None: 
					ValList=[1 for i in range(len(SigList))]
				else:
					ValList=[x.strip() for x in ValString.split(',')]
					while "" in ValList: ValList.remove("")
					# Fill values for implicit signals:
					if len(ValList)<len(SigList):
						ValList+=[1 for i in range(len(SigList)-len(ValList))]
					# or trunk the value list if too much values:
					elif len(ValList)>len(SigList):
						logging.warning("[ProtocolStep] Number of value exceed the number of signal. Excedent ignored.")
						ValList=ValList[:len(SigList)]
						
				
				try: self.AddNewStep(Label=L, SigList=SigList, ValList=ValList)
				except: 
					Msg="Unable to create protocol step '{0}' (SigList={1}).".format(Label, SigList)
					logging.error(Msg)
					raise SyntheSysError(Msg)
	#----------------------------------------------------------------------
	def Copy(self):
		"""
		Return abject with same attributes.
		"""
		Copy=DirectedProtocol(self.Interface, Name="UnknownDirectedProtocol")
		Copy.__name__=self.__name__
		Copy.DataDict=self.DataDict.copy()
		Copy.CtrlDict=self.CtrlDict.copy()
		Copy.Registers=self.Registers.copy()
		Copy.RegValues=self.RegValues.copy()
		Copy.RegisterAssignments=self.RegisterAssignments.copy()
		Copy._CurrentStepIndex=self._CurrentStepIndex
		Copy._CurrentIndex=self._CurrentIndex
		Copy._Steps=self._Steps
		Copy._SerializationFactor=self._SerializationFactor
		return Copy
	#----------------------------------------------------------------------
	def GetElmt(self):
		"""
		Copy protocol with all signal sliced.
		"""
		Copy=self.Copy()
		Copy.DataDict={k:v.Divide(self.Interface.Size) for k,v in self.DataDict.items()}
		Copy.CtrlDict={k:v.Divide(self.Interface.Size) for k,v in self.CtrlDict.items()}
		for S in Copy.IterSteps():
			S.Ctrl={k:v.Divide(self.Interface.Size) for k,v in S.Ctrl.items()}
			# TODO: same for data assignments
		return Copy
	#----------------------------------------------------------------------
	def GetSize(self):
		"""
		Return number of steps incuding repetitions for registers.
		"""
		Size=len(self._Steps)
		NBRep=1
		for S in self._Steps:
			for D in S.Data:
				if D in self.Registers:
					NBRep+=len(self.Registers[Data])
		return Size*NBRep
	#----------------------------------------------------------------------
	def AppendCtrl(self, Slave):
		"""
		if only data, add data to last step else append steps.
		"""
		logging.debug("OLD MASTER:")
		for i, S in enumerate(self.IterSteps()):
			logging.debug("\t["+str(i)+"]> "+str(S))
		logging.debug("OLD SLAVE:")
		for i, S in enumerate(Slave.IterSteps()):
			logging.debug("\t["+str(i)+"]> "+str(S))
			
		NewMaster = self.Copy()
		NewSlave  = Slave.Copy()
		
		SlaveSteps=list(NewSlave.IterSteps())
		MasterSteps=list(NewMaster.IterSteps())
		
		# Duplicate master steps for each register to be assigned
		for DName, RDList in self.Registers.items():
			for RD in reversed(RDList):
				NewMaster._Steps+=[S.Copy() for S in MasterSteps]
				S=NewSlave.AddNewStep(Label="Register assignment", SigList=(), ValList=(), Position=0)
				R=RD["Signal"];R.Direction="INOUT"
				S.AddData(R, IsRegister=True)
			
		# Move ctrl from slave to master
		for Step in SlaveSteps:
			NewSlaveStep=Step.Copy()
			#--------------------------------------
			# Duplicate slave steps for each register to be assigned
			TempRegs=[]
			RestoreTempSteps=None
			for D, DAss in NewSlaveStep.Data.items():
				SavingStep=None
				if D in Slave.Registers: # Save in temporary register
					#--------------------
					Reg=NewSlave.DataDict[D].Copy()
					Reg.SetName(D+"_TEMP")
					if SavingStep is None: 
						SavingStep=NewSlave.AddNewStep(Label="Save in temporary register", SigList=(), ValList=(), Position=0)
					TempRegs.append(Reg)
					#---Master steps for temporary read
					RestoreTempSteps=[S.Copy() for S in SlaveSteps]
					for S in RestoreTempSteps:
						Reg.Direction="INOUT"
						if S.RemoveData(): S.AddData(Reg, IsRegister=True)
					SavingStep.AddData(Reg, IsRegister=True)
					#--------------------
					for RD in Slave.Registers[D]:
						SS=[S.Copy() for S in SlaveSteps]
						for S in SS:
							R=RD["Signal"];R.Direction="INOUT"
							if S.RemoveData(): S.AddData(R, IsRegister=True)
						NewMaster._Steps+=SS
						S=NewSlave.AddNewStep(Label="Register assignment", SigList=(), ValList=(), Position=-1)
						SlaveData=NewSlave.DataDict[D].Copy()
						SlaveData.Direction="IN"
						S.AddData(SlaveData, IsRegister=False)
			#--------------------------------------
			NewSlaveStep.RemoveData()
			Step.RemoveCtrl() # Keep data for assignment
			#--------------------------------------
			if RestoreTempSteps: NewMaster._Steps+=RestoreTempSteps
			#--------------------------------------
			NewMaster._Steps[-1].Ctrl.update(NewSlaveStep.Ctrl)
				
		logging.debug("MASTER:")
		for i, S in enumerate(NewMaster.IterSteps()):
			logging.debug("\t["+str(i)+"]> "+str(S))
		logging.debug("SLAVE:")
		for i, S in enumerate(NewSlave.IterSteps()):
			logging.debug("\t["+str(i)+"]> "+str(S))
		return NewMaster, NewSlave
	#----------------------------------------------------------------------
	def GetInternalRegisters(self):
		"""
		return a dictionary of registers to be declared.
		"""
		# Registers are AssignmentSignal
		for RName, R in self.GetRegisters().items():
			R.SetIndex(None) # When indexing interfaces, registers are indexed => Wrong declaration format.
		return self.GetRegisters()
	#----------------------------------------------------------------------
	def MapAsFSM(self, AdapterFSM, Slave):
		"""
		Fill FSM.
		"""
		Master, Slave = self.AppendCtrl(Slave) # if only data, add data to last step else append steps
		
		FSMParams={}
		OutCtrls=[]
		InternalDict={}
		
		#----List of ctrl signals----
		AssignedCtrlList=Master.GetAssignedCtrl(Copy=True)+Slave.GetAssignedCtrl(Copy=True)
		AdapterFSM.AddResetAssignmentSignals(AssignedCtrlList)
		#----------------------------
		Slave.Reset()
		# INIT CONDITIONS
		if Master._Steps[0].HasCtrl("OUT"):
			InitEnteringCondition=Condition()
			InitEnteringCondition.AddANDCond(*Master._Steps[0].GetCtrl("OUT"))
		else:
			InitEnteringCondition=None
			
		for MasterStep in Master.IterSteps():
			MasterStep.Reset() # Clear assignment of input data
			#######################===-ENTERING CONDITIONS-===###################
			if MasterStep.HasCtrl("OUT"):
				EnteringCond=Condition()
				EnteringCond.AddANDCond(*MasterStep.GetCtrl("OUT"))
			else:
				EnteringCond=None
	
			#######################===-DATA ASSIGNMENTS-===###################
			if MasterStep.HasData("OUT"):
				for Data in MasterStep.GetData("OUT"):
					A, RegList=Slave.AssignDataFrom(MasterStep, Cond=None)
					AdapterFSM.AddAssignment(A) 
					if len(RegList): # Resets + Declarations
						for R in RegList: 
							InternalDict[R.GetName()]=R
					else:# Loop tag
						AdapterFSM.SetTag(Tag="LoopMarker", Anteriority=None) # For Data serialization loop
							
			#######################===-CTRL ASSIGNMENTS-===###################
#			if MasterStep.HasCtrl("IN"):
			OutCtrls=[x.GetName() for x in MasterStep.GetCtrl("IN")]
			for C in AssignedCtrlList:
				CtrlName=C.GetName()
				if CtrlName in OutCtrls: 
					SyncCond=MasterStep.GetSyncCtrl(CtrlName=CtrlName)
					CtrlAssignments=AssignmentStatement()
					CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=1, Cond=SyncCond, Desc="")
					if SyncCond:
						CtrlAssignments.Add(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc="")
					AdapterFSM.AddAssignment(CtrlAssignments, OnTransition=False)
				else: #---Assign 0 to other ctrl signals---
					AdapterFSM.AddAssignment(AssignmentStatement(Assignee=C.HDLFormat(), Assignor=0, Cond=None, Desc=""), OnTransition=False)
						
			########################===-STATE CREATION-===####################
			if not Master.IsLastStep(MasterStep): CurrentState=AdapterFSM.AddState(Cond=EnteringCond) # Conditional change
		
			#------------------------------------
			if not Slave.CurrentStep().HasDataToBeWritten():
				Slave.CurrentStep().Reset()
				Slave.Next(Loop=False)
				
		# Close FSM loop and create a mini loop if a serialization factor > 1  
		AdapterFSM.CloseLoop(None, Serialization=Master.GetSerializationFactor(), LoopStep=AdapterFSM.GetStepByTag("LoopMarker")) # Use InitEnteringCondition condition
		return FSMParams, InternalDict
	#----------------------------------------------------------------------
	def AddXMLElmtTo(self, ItfElmt):
		"""
		Add protocol XML element to ItfElmt.
		"""
		for PStep in self._Steps:
			PStep.AddXMLElmtTo(ItfElmt)
		return True
	#------------------------------------
	def SetSerializationFactor(self, SerializationFactor):
		"""
		Set SerializationFactor attribute.
		"""
		if SerializationFactor is None: self._SerializationFactor=1
		else: self._SerializationFactor=SerializationFactor
		return self._SerializationFactor
	#------------------------------------
	def GetSerializationFactor(self):
		"""
		Return SerializationFactor attribute.
		"""
		return self._SerializationFactor
	#----------------------------------------------------------------------
	def Complement(self, Interface=None):
		"""
		Complement steps.
		"""
		P=DirectedProtocol(Interface=Interface, Name=self.__name__)
		for PStep in self._Steps:
			PComp=PStep.Complement(Interface=Interface)
			P._Steps.append(PComp)
			
		return P
	#------------------------------------
	def GetSignalDict(self):
		"""
		Build dictionaries for signals from interface.
		"""
		# Get Step signals-----------------------------
		self.DataDict={}
		# Build dictionaries-----------------------------
#		Size=self.Interface.GetSize(Eval=True)
		for d in self.Interface.GetSignals(Ctrl=False, Data=True,  Directions=["IN", 'OUT']):
			self.DataDict[d.Name]=d#.Divide(Size) if Size>1 else d
		self.CtrlDict={}
		for c in self.Interface.GetSignals(Ctrl=True,  Data=False, Directions=["IN", 'OUT']):
			self.CtrlDict[c.Name]=c#.Divide(Size) if Size>1 else c 
		
		return self.DataDict, self.CtrlDict
	#----------------------------------------------------------------------
	def AddRegisters(self, Registers, Mapping, Direction, Index):
		"""
		Register = Pair of {Data : {Position:P, Name:RegName, Signal:S, Direction:D, Value:V,}}
		Fill self.Registers with signals
		Fill self.RegisterAssignments with assignment signals
		"""
		Reg={}
		RegAss={}
		self.Registers=Registers
		for Data in list(Registers.keys()):
			TargetData=Mapping[Data] if Data in Mapping else Data
			RegAss[TargetData]=[]
			for RDict in Registers[Data]:
				
				if Index: 
					A=AssignmentSignal(RDict["Signal"][Index])
				else:  
					A=AssignmentSignal(RDict["Signal"])
				RegAss[TargetData].append(A)
				
				self.RegValues[RDict["Name"]]=RDict["Value"]
				
		self.RegisterAssignments.update(RegAss)
		return
	#----------------------------------------------------------------------
	def __getitem__(self, Index):
		"""
		Set Current index value (protocol index/ interface index).
		"""
		if isinstance(Index, int):
			self._CurrentIndex=Index
		else:
			self._CurrentIndex=None
		return self
	#----------------------------------------------------------------------
	def GetRegisters(self):
		"""
		return dictionaries of indexed registers.
		"""
		if isinstance(self._CurrentIndex, int):
			RDict={}
			for DName, RDList in self.Registers.items():
				for RD in RDList: 
					RDict[RD["Name"]]=RD["Signal"][self._CurrentIndex]
			return RDict
		else:
			RDict={}
			for DName, RDList in self.Registers.items():
				for RD in RDList: 
					RDict[RD["Name"]]=RD["Signal"]
			return RDict
	#----------------------------------------------------------------------
	def GetRegisterAssignments(self):
		"""
		return dictionaries of indexed register assignments.
		"""
		return self.RegisterAssignments
	#----------------------------------------------------------------------
	def GetRegValues(self):
		"""
		return dictionaries of register values.
		"""
		return self.RegValues
	#----------------------------------------------------------------------
	def GetAssignedCtrl(self, Copy=False):
		"""
		return list of Ctrl signals assigned in each ProtocolStep.
		"""
		AssignedCtrlList=[x for x in list(self.CtrlDict.values()) if x.Direction=="IN"]
		if isinstance(self._CurrentIndex, int):
			AssignedCtrlList=[x[self._CurrentIndex] for x in AssignedCtrlList]
		if Copy is True:
			return	[x.Copy() for x in AssignedCtrlList]
		else:
			return	AssignedCtrlList
	#----------------------------------------------------------------------
	def Reset(self):
		"""
		reset step counter.
		"""
		for Step in self._Steps: 
			Step.Reset()
		self._CurrentStepIndex=0
	#----------------------------------------------------------------------
	def NbSteps(self):
		"""
		return generator of steps.
		"""
		return len(self._Steps)
	#----------------------------------------------------------------------
	def Next(self, Loop=False):
		"""
		Increment step counter.
		"""
		if self._CurrentStepIndex<len(self._Steps)-1:
			self._CurrentStepIndex+=1
			return self._Steps[self._CurrentStepIndex]
		else: 
			if Loop is True:
				self.Reset()
				return self._Steps[self._CurrentStepIndex]
			return None
	#----------------------------------------------------------------------
	def IterSteps(self):
		"""
		return generator of steps.
		"""
#		logging.debug("Steps: {0}".format(self._Steps))
		for S in self._Steps:
			yield S
	#----------------------------------------------------------------------
	def IsLastStep(self, S):
		"""
		Increment step counter.
		"""
		return S==self._Steps[-1]
	#----------------------------------------------------------------------
	def CurrentStep(self, Loop=False):
		"""
		return index of Current step if it do not overlapse the number of steps.
		"""
		if len(self._Steps)==0: return None
		elif self._CurrentStepIndex<len(self._Steps):
			return self._Steps[self._CurrentStepIndex]
		else:
			if Loop==True: return self._Steps[0]
			return None
	#----------------------------------------------------------------------
	def AddNewStep(self, Label, SigList, ValList, Position=None):
		"""
		Add step dictionary to step list.
		"""
		SigNames=[]
		SyncCtrl={}
		for i, SString in enumerate(SigList):
			SplitSig=SString.split(':')
			if len(SplitSig)>1:
				SyncSigName,SigName=SplitSig
				SigNames.append(SigName)
				if SigName in self.CtrlDict:
					Sig=self.CtrlDict[SigName].Copy()
				elif SigName in self.DataDict:
					Sig=self.DataDict[SigName].Copy()
				if SyncSigName in self.CtrlDict:
					CondSig=self.CtrlDict[SyncSigName].Copy()
				elif SyncSigName in self.DataDict:
					CondSig=self.DataDict[SyncSigName].Copy()
				#-----
				C=Condition()
				CondSig.Size=1
				#-----
				SplitVal=ValList[i].split(':')
				if len(SplitVal)>1:
					CondSig.SetValue(SplitVal[0])
					Sig.SetValue(SplitVal[1])
				else:
					Sig.SetValue(SplitVal[0])
				#-----
				C.AddANDCond(CondSig)
				SyncCtrl[SigName]=C
				#-----
			else:
				SigNames.append(SString)
				V = ValList[i]
				if SString in self.CtrlDict: 
					if isinstance(V, int):pass
					elif ':' in V:
						print("SString:", SString)
						print("ValList[i]:", V)
						raise TypeError
						
					self.CtrlDict[SString].SetValue(V)
				elif SString in self.DataDict: 
					# evaluate ':' separated values
					if isinstance(V,str):
						V=int(V.split(':')[0])
					self.DataDict[SString].SetValue(V)
				
		CtrlDict=dict((k, v) for k, v in list(self.CtrlDict.items()) if k in SigNames)
		DataDict=dict((k, v) for k, v in list(self.DataDict.items()) if k in SigNames)
		Step=ProtocolStep(DirProto=self, Label=Label, CtrlDict=CtrlDict, SyncCtrl=SyncCtrl, DataDict=DataDict, ValList=ValList, Interface=self.Interface)
		if Position is None:
			self._Steps.append(Step)
		else:
			self._Steps.insert(Position, Step)
		return Step
	#----------------------------------------------------------------------
	def AssignDataFrom(self, Step, Prot=None, Cond=None):
		"""
		
		"""
		CurrentStep=self._Steps[self._CurrentStepIndex]
		A, Regs=CurrentStep.AssignDataFrom(Step, SrcProt=Prot, Cond=Cond)
		
		return A, Regs
	#----------------------------------------------------------------------
	def AssignRegister(self, DataAssignment, RegAssignment):
		"""
		
		"""
		if DataAssignment is None:
			logging.warning("[AssignRegister] no data assignment specified. Received '{0}'.".format(DataAssignment))
			return None
		
		if RegAssignment.HasNonAssignedBits():
			logging.warning("Assign it !")
			if DataAssignment.Sig.Direction=="OUT":
				A=DataAssignment.AssignTo(RegAssignment)
			else:
				A=RegAssignment.AssignTo(DataAssignment)
			return A
		logging.warning("No available bits in registers to be assigned !")
		return None
	#----------------------------------------------------------------------
	def HasRegToBeWritten(self):
		"""
		Return True if there is registers left to be assigned.
		"""
		ToBeAssigned=[x for x in reduce(lambda x, y: x+y, list(self.RegisterAssignments.values()), []) if x and x.HasNonAssignedBits()]
		
		return True if len(ToBeAssigned)>0 else False
	#----------------------------------------------------------------------
	def PopRegToBeWritten(self):
		"""
		Return True if there is registers left to be assigned.
		"""
		RegList=[]
		for D in sorted(self.RegisterAssignments.keys()):
			RegList=self.RegisterAssignments[D]
			for R in RegList:
				if R.HasNonAssignedBits():
					return R
		return None
	#----------------------------------------------------------------------
	def HasDataToBeRead(self):
		"""
		Return True if there is data left to be read.
		"""
		ToBeRead=[] 
		Data=[] 
		for DList in [x.GetData("OUT") for x in self._Steps]:
			Data.extend(DList)
		ToBeRead.extend([x for x in Data if x.HasNonAssignedBits()])
		
		return True if len(ToBeRead)>0 else False
	#----------------------------------------------------------------------
	def HasRegToBeRead(self):
		"""
		Return True if there is registers left to be read.
		"""
		if len(self.RegisterAssignments)==0: return False
		ToBeRead=[x for x in reduce(lambda x, y: x+y, list(self.RegisterAssignments.values())) if x.HasNonAssignedBits()]
		
		return True if len(ToBeRead)>0 else False
	#----------------------------------------------------------------------
	def PopRegToBeRead(self):
		"""
		Return True if there is registers left to be read.
		"""
		RegList=[]
		for D in sorted(self.RegisterAssignments.keys()):
			RegList=self.RegisterAssignments[D]
			for R in RegList:
				if R.HasNonAssignedBits():
					return R
		return None
	#----------------------------------------------------------------------
	def __bool__(self):
		"""
		return False if step list empty else True.
		"""
		return len(self._Steps)>0
	#----------------------------------------------------------------------
	def __str__(self):
		"""
		Return string representation.
		"""
		return "{0}-{1}[{2}]".format(self.__name__, self.Interface.Direction, [str(P) for P in self.IterSteps()])
	#----------------------------------------------------------------------
	def __repr__(self):
		"""
		Return string representation.
		"""
		return str(self)
		
#======================================================================
def GetProtocol(Interface):
	"""
	RESET OUTPUT SIGNALS
	"""
	return Proto
		

		
