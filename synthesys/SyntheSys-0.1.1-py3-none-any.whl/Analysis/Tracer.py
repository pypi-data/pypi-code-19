
#import myhdl
import logging, os, sys
import weakref
from .Operation import Operation as Op
from .Operation import ResetOperations
from SyntheSys.Analysis.Select import SelectOperation

from SyntheSys.Analysis.Misc import Misc
	
#=========================================================
class Tracer:
	"""For data path/flow tracking"""
	TracerNumber=0
	Instances=[]
	InstancesNames=[]
	Constants=[]
#	MergeList=[]
	MergedData=[]
	Interface=[]
#	ParallelFlow=False
#	ParallelInstances=[]
#	PipeReads=[]
#	PipeWrite=None
#	ForkedIDList=[]
	SkipLines=[] # Used to detect lines already executed (previous values must be returned)
	SkipReturn=None # Used to detect return expressions already evaluated (previous values must be returned)
	SelectNode=None
	#-------------------------------------------------
	def __init__(self, Name, Operation, Parents=[], PythonVar=None, Context=None, IsInterface=False):
		"""
		Initialization of the Tracer attributes.
		"""
		Tracer.TracerNumber+=1
		self.SyntheSys__ID          = Tracer.TracerNumber
		self.SyntheSys__Name        = Name
		self.SyntheSys__Parents     = [] if Operation is None else Operation.Inputs # map(lambda x: x.SyntheSys__Assignments[-1] if len(x.SyntheSys__Assignments) else x, filter(lambda x: isinstance(x, Tracer), Parents))
		self.SyntheSys__Context     = Context
		self.SyntheSys__PythonVar   = PythonVar
		self.SyntheSys__IsInterface = IsInterface
		self.Size=32 # TODO : Set it properly
		
		self.SyntheSys__Children    = {} # operation : Child
		self.SyntheSys__Assignments = []
		self.AssignedTo   = []
		self.AssignedIdx  = None
		
		self.SyntheSys__Producer = Operation
		if Operation: 
			if not self.SyntheSys__Producer.IsSwitch(): self.SyntheSys__Producer.Outputs.append(self)
		
		self.SyntheSys__CallingMethod = Misc.GetCallingMethod()
		
		if len(Parents)==0 and (IsInterface is False):
			self.SyntheSys__IsConstant=True
			Tracer.Constants.append(self)
		else:
			self.SyntheSys__IsConstant=False
			for P in self.SyntheSys__Parents:
				P.AddChildren(Operation, self)
		
		if IsInterface is True: Tracer.Interface.append(self)
		Tracer.Instances.append(self)
		
		ID=self.NodeID()
		
		self.SyntheSys__Selectors={} # For conditional branching
		self.SyntheSys__ToBeMergeWith=None
		
		if ID in Tracer.InstancesNames:
			if self.SyntheSys__IsConstant:
				FirstInstance=Tracer.Instances[Tracer.InstancesNames.index(ID)]
				for P in FirstInstance.SyntheSys__Parents:
					P.AddChildren(Operation, self)
					P.RemoveChildren(Operation, self)
				self.SyntheSys__Parents+=FirstInstance.SyntheSys__Parents
				self.SyntheSys__Children.update(FirstInstance.SyntheSys__Children)
				self.SyntheSys__Selectors.update(FirstInstance.SyntheSys__Selectors)
				FirstInstance.SyntheSys__Selectors.clear()
			else:
				self.SyntheSys__ToBeMergeWith=Tracer.Instances[Tracer.InstancesNames.index(ID)]
				# TODO : merge same data
#				self.SyntheSys__Name+="(Dup)"
#				ID=self.NodeID()
#				logging.error("[Tracer.py] Fusion of same ID data not supported yet.")
#				sys.exit(1)
				
		Tracer.InstancesNames.append(ID)
		#-------------------
		self.SyntheSys__TBValues = []	
		self.SyntheSys__Container = None
		self.SyntheSys__Index=0
	#-------------------------------------------------
	def GetName(self):
		"""GETTER"""
		return self.SyntheSys__Name
	#-------------------------------------------------
	def SetName(self, Name):
		"""SETTER"""
		self.SyntheSys__Name=Name
	Name=property(GetName, SetName)
	#-------------------------------------------------
	def GetID(self):
		"""GETTER"""
		return self.SyntheSys__Name
	#-------------------------------------------------
	def SetID(self, ID):
		"""SETTER"""
		self.SyntheSys__ID=ID
	ID=property(GetID, SetID)
	#-------------------------------------------------
	def SetAsInterface(self):
		"""
		Add Tracer to Interface list.
		"""
		Tracer.Interface.append(self)
	#-------------------------------------------------
	def AddChildren(self, Operation, *Children):
		"""
		Initialization of the Tracer attributes.
		"""
		if Operation in self.SyntheSys__Children: # Children={operation : Child,}
#			self.SyntheSys__Children[Operation]+=map(lambda x: weakref.ref(x), Children)
			self.SyntheSys__Children[Operation]+=Children
		else:
#			self.SyntheSys__Children[Operation]=map(lambda x: weakref.ref(x), Children)
			self.SyntheSys__Children[Operation]=Children
#		logging.info("Add Tracer child {0} to {1}".format(repr(Children), repr(self)))
		return True
	#-------------------------------------------------
	def GetFollowingTracers(self):
		"""
		return iterator on _children attributes values.
		"""
		for Children in self.SyntheSys__Children.values():
			for Child in Children:
				yield Child
	#-------------------------------------------------
	def RemoveChildren(self, Operation, *Children):
		"""
		Initialization of the Tracer attributes.
		"""
		if Operation in self.SyntheSys__Children: # Children={operation : Child,}
#			self.SyntheSys__Children[Operation]+=map(lambda x: weakref.ref(x), Children)

			for Child in Children:
				if Child in self.SyntheSys__Children[Operation]:
					self.SyntheSys__Children[Operation].remove(Child)
				else:
					logging.error("[Data.RemoveChildren] Child {0} not in {1}'s children.".format(repr(Child), repr(self)))
		else:
			logging.error("[Data.RemoveChildren] Operation {0} not in {1}'s operations.".format(repr(Operation), repr(self)))
			return False
		return True
	#-------------------------------------------------
	def LastAssignment(self):
		"""
		Return last assigned signal
		"""
		if len(self.SyntheSys__Assignments):
			return self.SyntheSys__Assignments[-1]
		else:
			return self
	#-------------------------------------------------
	def NodeID(self, ShowID=False, LastAssignment=False):
		"""
		Return Graph unique ID.
		"""
		if len(self.AssignedTo):
			if ShowID: 
				NodeID=self.SyntheSys__Producer.GetOutputName(ShowID)
				if NodeID is None: NodeID=str(self.SyntheSys__ID)
			else: NodeID="{0}_{1}".format(self.AssignedTo[0].SyntheSys__Name, self.AssignedIdx)
		else:
			if self.SyntheSys__Producer: 
				NodeID=self.SyntheSys__Producer.GetOutputName(ShowID)
				if NodeID is None:
					if ShowID: NodeID=str(self.SyntheSys__ID)
					else: NodeID=self.SyntheSys__Name
			else:
				if ShowID: NodeID=str(self.SyntheSys__ID)
				else: NodeID=self.SyntheSys__Name
				
		if len(NodeID)>10:
#			print("Too long", Name)
			NodeID = "{0}...{1}".format(NodeID[:6], self.SyntheSys__ID)
#			print("self.SyntheSys__Name:", self.SyntheSys__Name)
		else:
#			print("Good length")
			NodeID = NodeID
		return NodeID
	#-------------------------------------------------------------
	def Assign(self, Value):
		"""
		Add new Tracer assignment to assignments list.
		"""
		if isinstance(Value, Tracer):
			self.SyntheSys__Assignments.append(Value)
			Value.AssignedTo.append(self)
			Value.AssignedIdx=len(self.SyntheSys__Assignments)
#			Value._Name="{0}_{1}".format(self.SyntheSys__Name, len(self.SyntheSys__Assignments)-1)
			return True
		else:
			logging.error("Value assigned must be a Tracer instance.")
			return False 
	#-------------------------------------------------------------
	def GetSize(self):
		"""
		Return bitwidth necessary for keeping Tracer precision.
		"""
		if len(self.SyntheSys__Parents):
			PTypes = map(lambda x: x.GetProperty()["Type"], self.SyntheSys__Parents)
			if int in PTypes:
				return 32 # TODO
			else:
				logging.error("[GetSize] Unsupported type '{0}'".format(PTypes[0]))
		else:
			if self.SyntheSys__PythonVar!=None:
				if isinstance(self.SyntheSys__PythonVar, int):
					return 32 # TODO
			else:
				logging.error("[GetSize] Cannot infere size if Tracer don't have parents or has not constant value.")
		return 0 # TODO
	#-------------------------------------------------------------
	def GetDirection(self):
		"""
		Return string representing direction of Tracer : In, Out or InOut.
		"""
		# TODO : manage InOuts
		if len(self.SyntheSys__Children): return "In"
		else: return "Out"
	#-------------------------------------------------------------
	def GetType(self):
		"""
		Return string of VHDL type for this signal.
		"""
		return "std_logic_vector"
	#-------------------------------------------------------------
	def IsSelected(self):
		"""
		return True if Tracer has a SELECT operator that consume it.
		"""
		if isinstance(self.SyntheSys__Producer, SelectOperation):
			return True
		else:
			return False
	#-------------------------------------------------------------
	def Merge(self, TestedData, SelectValue, Other, SelectG):
		"""
		Add self's parents/children and Other parents/Children in data flow.
		Self is the True value. Other the False value.
		TODO:
			Retours dans le ELSE si pas de retours dans les if/elif
				if x:
					c=a+b
				else:
					return a-b	
				return c+1
			Si manque un retour dans un branchement et que la fonction retourne une expression.
				if x:
					return a+b
				return a-b	
		"""
#		print("Tracer.MergedData:", Tracer.MergedData)
#		print("[Merge] TestedData  :", TestedData)
#		print("[Merge] SelectValue :", SelectValue)
#		print("[Merge] Other       :", Other)
#		print("[Merge] Self        :", self)
		if Other is None: # We have only the true value
			if self.IsSelected():
				logging.error("[Tracer.Merge] True value already set for merge !")
				raise TypeError()
#				return self.GetSelectOp().GetSelectOutput()
			SelectOp=SelectOperation(TestedData=TestedData, InputList=list(), SelectG=SelectG)
			SelectOp.AddToSelect(self.LastAssignment(), SelectValue)
#			Tracer.MergeList.append(SelectOp)
			O=SelectOp.GetSelectOutput()
			Tracer.MergedData.append(O)
#			print(SelectOp.Inputs)
#			print("O =>", O)
			return O
		if self.IsSelected(): # True value has been set, only set the False value
#			print("[Merge] self.SyntheSys__Producer.TestedData:", self.SyntheSys__Producer.TestedData, "TestedData:", TestedData)
#			if self.SyntheSys__Producer.TestedData is TestedData:
#				self.SyntheSys__Producer.AddToSelect(Other, SelectValue)
#				SelectOp=self.SyntheSys__Producer
#				O=SelectOp.GetSelectOutput().LastAssignment()
#				Tracer.MergedData.append(O)
#				return O
#			else:
			if SelectValue is True: # Add new merge operation => ELIF
				SelectOp=SelectOperation(TestedData=TestedData, InputList=list(), SelectG=SelectG)
				SelectOp.AddToSelect(Other, SelectValue)#self.SyntheSys__Producer.GetSelectOutput().LastAssignment()
				O=SelectOp.GetSelectOutput().LastAssignment()
				self.SyntheSys__Producer.AddToSelect(O, not SelectValue)
				return self
			else: # Add False value to the merge operation => ELSE
				SelectOp=self.SyntheSys__Producer#SelectOperation.Instances[-1]
				SelectOp.AddToSelect(Other, SelectValue)#self.SyntheSys__Producer.GetSelectOutput().LastAssignment()
				O=SelectOp.GetSelectOutput().LastAssignment()
				Tracer.MergedData.append(O)
				return O
#			print("[Merge] SelectOp      :", SelectOp)
#			print("[Merge] Merge output :", O)
#			print("[Merge] New Self     :", self)
		elif Other.IsSelected(): # Merged False value merged with non merged True value
#			if Other._Producer.TestedData is TestedData:
#				Other._Producer.AddToSelect(self.LastAssignment(), SelectValue)
#				SelectOp=Other._Producer
#			else:
			SelectOp=SelectOperation(TestedData=TestedData, InputList=list(), SelectG=SelectG)
			SelectOp.AddToSelect(self, SelectValue)#self.SyntheSys__Producer.GetSelectOutput().LastAssignment()
			SelectOp.AddToSelect(Other._Producer.GetSelectOutput(), not SelectValue)
#			Other._Producer.AddToSelect(SelectOp.GetSelectOutput().LastAssignment(), not SelectValue)
			O=SelectOp.GetSelectOutput()
			Tracer.MergedData.append(O)
			return O
		else:
			SelectOp=SelectOperation(TestedData, InputList=[], SelectG=SelectG)
			SelectOp.AddToSelect(self.LastAssignment(), SelectValue=not SelectValue)
			SelectOp.AddToSelect(Other.LastAssignment(), SelectValue=SelectValue)
#			Tracer.MergeList.append(SelectOp)
			O=SelectOp.GetSelectOutput()
			Tracer.MergedData.append(O)
			return O
			
#		#--------------------------
#		def GetNodeIDs(Items):
#			if isinstance(Items, list) or isinstance(Items, tuple):
#				for I in Items:
#					return [I.NodeID(),]
#			else:
#				return [Items.NodeID(),]
#		#--------------------------
#		SelfParentNames   = map(lambda x: x.NodeID(), self.SyntheSys__Parents)
#		SelfChildrenNames = []
#		if len(self.SyntheSys__Children):
#			for Children in self.SyntheSys__Children.values():
#				SelfChildrenNames+= GetNodeIDs(Children)
#		else: SelfChildrenNames=[]
#		for P in Other._Parents:
#			if P.NodeID() not in SelfParentNames:
#				self.SyntheSys__Parents.append(P)
#				P._Children[Other._Producer._Name]=[self,]
#		OtherChildren = Other._Children.iteritems()
#		for O, C in OtherChildren:
#			for SubC in C: # For each child of Others
#				if SubC.NodeID() not in SelfChildrenNames: # If not already in self.SyntheSys__Children
#					self.SyntheSys__Children[O]=SubC
#					SubC._Parents.append(self)
#					SubC._Parents.remove(Other)
	#-------------------------------------------------
	def GetProperty(self, Property):
		"""
		Return Tracer property value
		"""
		if self.SyntheSys__Producer is None:
			return type(self.PythonVar)
		else:
			return self.SyntheSys__Producer.GetOutputProperty(Property)
	#-------------------------------------------------
	def GetProducer(self):
		"""
		Return _Producer attribute
		"""	
		return self.SyntheSys__Producer
	#-------------------------------------------------
	def GetParents(self, IgnoreCtrl=True):
		"""
		yield list of dependencies with or without control dependencies.
		"""
		for P in self.SyntheSys__Parents:
			if not (P.SyntheSys__Producer is None):
				if P.SyntheSys__Producer.IsSwitch(): continue
			if self.SyntheSys__Producer.IsSelect(): continue
			elif self.SyntheSys__Producer.IsSwitch(): continue
			yield P
	#-------------------------------------------------
	def GetConsumers(self, IncludeControl=False, IO=True):
		"""
		return list of operations that consume this data.
		"""
		Consumers=[]
		if isinstance(self.SyntheSys__PythonVar, list) or isinstance(self.SyntheSys__PythonVar, tuple):
			for Key,D in self.SyntheSys__Container.items():
				Consumers.append( (D, D.SyntheSys__Children.keys()) )

		OpList=[]
		for ConsOp, Children in self.SyntheSys__Children.items():
			if ConsOp.IsSwitch():
				if IncludeControl is True:
					OpList.append(ConsOp.TestGroup) # Task associated with SWITCH
				else:
					for Child in Children:
						for D, ConsOpList in Child.GetConsumers(IncludeControl=False):
							OpList+=ConsOpList
			elif ConsOp.IsSelect():
				if IncludeControl is True:
					OpList.append(ConsOp.SelectGroup) # Task associated with SELECT
				else:
					for Child in Children:
						for D, ConsOpList in Child.GetConsumers(IncludeControl=False):
							OpList+=ConsOpList
			elif ConsOp._Name=="__setitem__":
				for O in ConsOp.GetOutputs():
					for D, ConsOpList in O.GetConsumers(IncludeControl=False):
						OpList+=ConsOpList
					
			else:
				if (ConsOp.IsInput() or ConsOp.IsOutput()) and IO is False: continue
				else:
					OpList.append(ConsOp)
						
		if len(OpList)>0:
			Consumers.append( (self, OpList) )
#			return [(self, OpList),]
		return Consumers
	#-------------------------------------------------
	def AddTBVal(self, Val):
		"""
		Add value (like a token) to TB value list.
		"""
		if isinstance(self.SyntheSys__PythonVar, list) or isinstance(self.SyntheSys__PythonVar, tuple):
#			try: self.SyntheSys__Container[len(Val)-1]
#			except IndexError: 
#				logging.error("Argument must be a length {0} iterator.".format(len(self.SyntheSys__PythonVar)))
#				return False
			self.SyntheSys__TBValues.append(Val)
#			if len(Val)!=len(self.SyntheSys__Container):
#				logging.error("TB values of token '{0}' has more item ({1}) than expected ({2})".format(self.Name, len(Val), len(self.SyntheSys__Container)))
#				input()
			for i,V in enumerate(self.SyntheSys__Container):
				self.SyntheSys__Container[V].AddTBVal(Val[i]) 
		else:
			self.SyntheSys__TBValues.append(Val)
		return True
	#-------------------------------------------------
	def GetTBValues(self):
		"""
		return values list (token-like).
		"""
		return self.SyntheSys__TBValues
		
	#-------------------------------------------------
#	def __hash__(self):
#		"""
#		Defines behavior for when hash() is called on an instance of your class. It has to return an integer, and its result is used for quick key comparison in dictionaries. Note that this usually entails implementing __eq__ as well. Live by the following rule: a == b implies hash(a) == hash(b).
#		"""
#		return self.SyntheSys__ID # hash(self.SyntheSys__ID)
		
#=========================================================
def ResetTracer():
	"""
	Re-Initialization of the class attributes.
	"""
	Tracer.TracerNumber=0
	Tracer.Instances=[]
	Tracer.InstancesNames=[]
	Tracer.Branch=None
	Tracer.ParallelFlow=False
	Tracer.ParallelInstances=[]
	Tracer.PipeReads=[]
	Tracer.PipeWrite=None
	Tracer.ForkedIDList=[]
	ResetOperations()
	
	
	
		
		
