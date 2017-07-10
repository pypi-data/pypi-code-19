import os, sys, logging
from SyntheSys.Analysis.Tracer import Tracer
from SyntheSys.Analysis.SkipLines import SkipLines, SkipReturn
from SyntheSys.Analysis import Switch, Select, TestGroup, SelectGroup
from SyntheSys.Analysis.Operation import Operation as Op
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from Utilities import Misc

import inspect

#=========================================================
class Data(Tracer):
	"""
	Object that replace variables in algorithm for Data Path tracking.
	"""
	BRANCH_BROWSING=True
	BranchStack=[] # Used for storing boolean return values of conditional branches, for each level of nested branching
	#-------------------------------------------------
	def __init__(self, Name=None, PythonVar=None, Parents=[], Operation=None, Context=None, IsInterface=False):
		"""
		Initialization of the Data attributes.
		"""
		super().__init__(
			Name=Name if not Name is None else repr(PythonVar), 
			Operation=Operation, 
			PythonVar=PythonVar, 
			Parents=Parents, 
			Context=Context, 
			IsInterface=IsInterface
			) # For data path/flow  
			
		self.SyntheSys__Container=None
		if not PythonVar is None: # Input data
			if isinstance(PythonVar, list) or isinstance(PythonVar, tuple):
				self.SyntheSys__Container={}
#				for i, V in enumerate(PythonVar): 
#					S=Data(Name="{0}[{1}]".format(Name, i), PythonVar=V, Parents=[self,], IsInterface=IsInterface)#, Operation=O)
#					self.SyntheSys__Container.append(S)
#				if isinstance(PythonVar, tuple):
#					self.SyntheSys__Container=tuple(self.SyntheSys__Container)
			else: pass
		else: # Standard python types
			if len(Parents)==0:
				logging.error("Data object must either have a parent data (with an Operation) or be generated from python variable".format(self))
				print("Name:",Name)
				print("self.SyntheSys__Name:",self.SyntheSys__Name)
				print("Parents:",Parents)
				print("PythonVar:",PythonVar)
				raise TypeError
				sys.exit(1)
	##################################################
# TODO: Handle
#	int 	Nombre entier optimise
#	long 	Nombre entier de taille arbitraire
#	float 	Nombre a virgule flottante
#	complex 	Nombre complexe
#	str 	Chaine de caractere
#	unicode 	Chaine de caractere unicode
#	tuple 	Liste de longueur fixe
#	list 	Liste de longueur variable
#	dict 	dictionnaire
#	file 	Fichier
#	bool 	Booleen
#	NoneType 	Absence de type
#	NotImplementedType 	Absence d'implementation
#	function 	fonction
#	HighLevelModule 	HighLevelModule		
	#-------------------------------------------------
	def DataFlow__IsData(self, GivenData):
		"""
		return True if instance is given data 
		or if input of a __setitem__ producer is data.
		"""
		if self is GivenData:
			return True
		else:
			if self.SyntheSys__Producer is None:
				return GivenData.NodeID()==self.NodeID()
			if self.SyntheSys__Producer._Name=="__setitem__":
				return self.SyntheSys__Producer.GetInputs()[0].DataFlow__IsData(GivenData)
			else:
				if GivenData.SyntheSys__Producer._Name=="__setitem__":
					return GivenData.SyntheSys__Producer.GetInputs()[0].DataFlow__IsData(self)
				else:
					return GivenData.NodeID()==self.NodeID()
	#-------------------------------------------------
	def Copy(self, S, Operation=None):
		"""
		Duplicate Data object : copy every attributes
		"""
#		logging.debug("Copy Data '{0}'".format(repr(S)))
		self.SyntheSys___type__   = S.__type__
		self.SyntheSys___size__   = len(S)
		self.SyntheSys__Container = S.SyntheSys__Container # TODO: not right
	#-------------------------------------------------
	def GetCopy(self, NewName=None, Op=None, PythonVar=None):
		N=NewName if NewName else self.SyntheSys___name__
		PV=self.SyntheSys__PythonVar if PythonVar is None else PythonVar
		Child = Data(Name=N, Parents=Op.Inputs if Op else [], Operation=Op, PythonVar=PV)
		return Child
	#-------------------------------------------------
	def __iter__(self):
		"""
		Iterator for looping over a sequence backwards.
		"""
#		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		for i, Elmt in enumerate(self.SyntheSys__PythonVar):
			yield self[i]
#			if D.SyntheSys__Container:
#				yield D.SyntheSys__Container
#			else:
#				yield D
	#-------------------------------------------------
	def __next__(self):
		"""
		returns the next value of self.SyntheSys__Container and is 
		implicitly called at each loop increment.
		raises a StopIteration exception when there are no more 
		value to return, which is implicitly captured by looping 
		constructs to stop iterating.
		"""
#		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		if self.SyntheSys__Index > len(self.SyntheSys__Container)-1:
			raise StopIteration
		else:
			self.SyntheSys__Index += 1
			return self.SyntheSys__Container[self.SyntheSys__Index]
	#-------------------------------------------------
	def __repr__(self):
		"""
		Compute the 'official' string representation of the Data object.
		"""
		return "<pySystems Data {0} ID={1}>".format(self.NodeID(), self.ID)
			
	#-------------------------------------------------
	def __str__(self):
		"""
		Return string representation of Data value.
		"""
		return self.NodeID()
	#---------------------------------------------------------------------------------------------------
	# COMPARATORS
	#---------------------------------------------------------------------------------------------------
	def __lt__(self, Other):
		"""
		Operation: <
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__lt__", InputList=[Parent1, Parent2]))
		return Child
	#-------------------------------------------------
	def __le__(self, Other):
		"""
		Operation: <=
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__le__", InputList=[Parent1, Parent2]))
		return Child
	#-------------------------------------------------
	def __eq__(self, Other):
		"""
		Operation: ==
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__eq__", InputList=[Parent1, Parent2]))
		return Child
			
	#-------------------------------------------------
	def __ne__(self, Other):
		"""
		Operation: !=
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__ne__", InputList=[Parent1, Parent2]))
		return Child
			
	#-------------------------------------------------
	def __gt__(self, Other):
		"""
		Operation: >
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__gt__", InputList=[Parent1, Parent2]))
		return Child
			
	#-------------------------------------------------
	def __ge__(self, Other):
		"""
		Operation: >=
		"""
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):	
			Parent2=Other.LastAssignment()
		else:			
			Parent2 = Data(PythonVar=Other)
		Child = Data(Parents=[Parent1, Parent2,], Operation=Op("__ge__", InputList=[Parent1, Parent2]))
		return Child
		
	#-------------------------------------------------
	def __cmp__(self, Other):
		"""
		Called by comparison operations if rich comparison (see above) is not defined.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return
	#-------------------------------------------------
	def __bool__(self):
		"""
		Called to implement truth value testing and the built-in operation bool()
		Should return False or True, or their integer equivalents 0 or 1.
		"""
#		print("> __bool__ call")
		# Block 'else' sub-block data production.
		
		
#		BaseFrame=inspect.currentframe().f_back
#		print("\nBaseFrame", BaseFrame)
#		OuterFrame=inspect.getouterframes(BaseFrame)[0]
#		print("\nCurrent Frame", OuterFrame)
#		Frame=OuterFrame[0]
#		LineNb=OuterFrame[2]
#		print("\nFRAME 1", "(",Frame, ")")
#		SrcLines, Offset=inspect.getsourcelines(Frame)
#		print("\nSrcLines", SrcLines)
#		StartIndex=LineNb-Offset
#		print("\nStartIndex", StartIndex)
#		print("LineNb", LineNb)
#		print("Offset", Offset)
#		print("Number of lines:", len(SrcLines))
#		print("Item:", SrcLines[StartIndex])
#		print(SrcLines[StartIndex:])
		
		
		
		# TODO: c = a if x else b
		if Data.BRANCH_BROWSING is True:
			return CondBranchAnalysis(TestedData=self)
		else:
			if self.SyntheSys__PythonVar is None: return False
			else: return bool(self.SyntheSys__PythonVar)
		
	#-------------------------------------------------
	def __nonzero__(self):
		"""
		Called to implement truth value testing and the built-in operation bool()
		Should return False or True, or their integer equivalents 0 or 1.
		"""
		print("> __nonzero__ call")

		# TODO: c = a if x else b
		if Data.BRANCH_BROWSING is True:
#			# Executer le bloc correspondant a un retour True
#			# Retourner False
#			return False
#		
#			r,w=os.pipe()
#			r,w=os.fdopen(r,'rb',0), os.fdopen(w,'wb',0)
#			#****************************************************************************
#			# NEEDED SO AS NOT TO FREEZE THE SYSTEM WHEN TOO MANY FORK ARE MADE
#			while len(Tracer.ForkedIDList):
#				PID = Tracer.ForkedIDList.pop(0)
#				logging.debug("[{0}] Waiting PID '{1}'".format(os.getpid(), PID))
#				os.waitpid(PID, 0)
#				logging.debug("[{0}] PID '{1}' successfully joined !".format(os.getpid(), PID))
#			#****************************************************************************
#	#		raw_input(inspect.getouterframes(inspect.currentframe())[2])
#			self.BranchNode=BranchNode(Name="Branch", Input=self)
#			ProcessID=os.fork()
#			if ProcessID==0:
#				# Child process
#				r.close()
#				Tracer.PipeWrite=w
#				del Tracer.ForkedIDList[:]
#				del Tracer.PipeReads[:]
#				Tracer.ParallelFlow=True
#	#			Tracer.Instances=[self,] # Reset list of Datas produced
#				Tracer.MuxCtrl=self # Mark first data produced in TrueBlock execution
#				return True
#			else:
#				# Parent process
#				w.close()
#				Tracer.PipeReads.append(r)
#				Tracer.ForkedIDList.append(ProcessID)
#				# TODO: Merge graphs
#				MergeModels(Tracer.Instances, Tracer.ParallelInstances)
#				Tracer.MuxCtrl=self # Mark first data produced in FalseBlock execution

			# Mark this data producer (TestOp) as the SELECTOR of future operation instances
			return CondBranchAnalysis(TestedData=self)
		else:
			if self.SyntheSys__PythonVar is None: return False
			else: return self.SyntheSys__PythonVar.__nonzero__()
			
	#---------------------------------------------------------------------------------------------------
	#---------------------------------------------------------------------------------------------------
	def __len__(self):
		"""
		Called to implement the built-in function len()
		"""
#		logging.debug("[__size__] Size={0}".format(self.SyntheSys___size__))
		return len(self.SyntheSys__PythonVar)
	#---------------------------------------------------------------------------------------------------
	def keys(self):
		logggin.error("Only called for dict like data. Not implemented yet.")
		raise TypeError
#		return self.SyntheSys__Container
	#-------------------------------------------------
	def __getitem__(self, Key):
		"""
		Called to implement evaluation of Data[key]
		key = integers and slice objects
		"""
		logging.debug("Get item {0} of {1}".format(Key, self))
		if self.SyntheSys__Container is None:
			raise KeyError("Object '{0}' not iterable".format(self.Name))
#			if isinstance(Key, int):
#				if Key>=0 and Key<len(self.SyntheSys__Container): # TODO: support python convention key=-1
#					return self.SyntheSys__Container[Key]
#				elif Key<0 and len(self.SyntheSys__Container)+Key>=0:
#					return self.SyntheSys__Container[len(self.SyntheSys__Container)+Key]
#				else: raise KeyError("Key '{0}' out of range.)".format(Key))
#			elif isinstance(Key, slice):
#			else:
#				logging.error("Data Operation '{0}' not available yet for slice keys.".format(inspect.stack()[0][3]))
#				return None # TODO
		else:
			
			PV=self.SyntheSys__PythonVar[Key]
			if Key in self.SyntheSys__Container:
				return self.SyntheSys__Container[Key]
			elif isinstance(Key, int):
				if Key<0:
					Key=len(self.SyntheSys__PythonVar)+Key
					if Key in self.SyntheSys__Container:
						return self.SyntheSys__Container[Key]
			
			D=Data(Name="{0}[{1}]".format(self.SyntheSys__Name, Key), PythonVar=PV, Parents=[self,], IsInterface=False)#, Operation=O)
			self.SyntheSys__Container[Key]=D
			return D
#		elif isinstance(Key, int):
#			NewSig = Data(
#					Name="{0}[{1}]".format(self.SyntheSys___name__, Key), 
#					PythonVar=self.SyntheSys__PythonVar[Key],
#					Parents=[self,], 
#					Operation=Op("__getitem__", InputList=[self,], ExtraArg={"Key":Key}))
##			if isinstance(self.SyntheSys___type__, list):
##				if Key<len(self.SyntheSys___type__): NewSig.__type__==self.SyntheSys___type__[Key]
##				else: raise KeyError("Key '{0}' out of range".format(Key))
#			return NewSig
#		else:
#			logging.error("Data Operation '{0}' not support '{1}'({2}) keys.".format(inspect.stack()[0][3], type(Key), Key))
#			return None # TODO
						
	#-------------------------------------------------
	def __setitem__(self, Key, Value):
		"""
		Called to implement assignment to self[key]=Value
		"""
#		logging.debug("[__setitem__] Set item {0} of '{1}' to value '{2}'".format(Key, self, Value))
		if isinstance(Value, self.__class__): 
			SigVal = Data(
					Name="{0}_{1}={2}".format(
							self.SyntheSys__Container[Key].NodeID(), 
							len(self.SyntheSys__Container[Key].SyntheSys__Assignments)+1, 
							Value.NodeID()), 
					PythonVar=Value.SyntheSys__PythonVar,
					Parents=[Value,], 
					Operation=Op(Name="__setitem__", InputList=[Value,], ExtraArg={"Key":Key}))
		else: 
			# Constant Data
			SigVal = Data(Name=str(Value), PythonVar=Value)
			
		
		if isinstance(Key, int):
			if Key<0: Key=len(self.SyntheSys__PythonVar)+Key
			if Key in self.SyntheSys__Container:
				self.SyntheSys__Container[Key].Assign(SigVal)
				return 
			if Key>=len(self.SyntheSys__PythonVar): # TODO: support python convention key=-1
				raise KeyError("Key '{0}' out of range.".format(Key)).NodeID()
	
		#---------------
		if Key in self.SyntheSys__Container:
			self.SyntheSys__Container[Key].Assign(SigVal)
			return 
		
		#---------------
		self.SyntheSys__Container[Key]=SigVal
#		logging.debug("{0} assignments: '{0}'".format(repr(self.SyntheSys__Container[Key]), repr(self.SyntheSys__Container[Key]._Assignments)))
			
	#-------------------------------------------------
	def __delitem__(self, key):
		"""
		Called to implement deletion of self[key]
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return
			
	#-------------------------------------------------
	def __reversed__(self):
		"""
		Called (if present) by the reversed() built-in to implement reverse iteration. 
		It should return a new iterator object that iterates over all the objects in the container in reverse order.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __contains__(self, item):
		"""
		Called to implement membership test Operations. 
		Should return true if item is in self, false Otherwise.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __setslice__(self, i, j, sequence):
		"""
		Called to implement assignment to self[i:j].
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __delslice__(self, i, j):
		"""
		Called to implement deletion of self[i:j].
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __add__(self, Other):
		"""
		Operation: +
		"""
#		logging.debug("Operation '{0}'+'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__add__] Tracer.MergedData:",  Tracer.MergedData)
#				print("Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[add] {0}+{1} => Inst:".format(self, Other), Inst)
				return Inst
#		print("Argument {0} is a merge: {1}".format(self, self.IsMerged()))
		# New name must take into account the last assignment (cf. Method "Name")
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar+Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=self.SyntheSys__PythonVar+Other
		D=Data(
			Name="{0}+{1}".format(Parent1, Parent2), 
			Operation=Op("__add__", InputList=[Parent1, Parent2]), 
			PythonVar=PythonVar,
			Parents=[Parent1, Parent2])
			
		return D
			
	#-------------------------------------------------
	def __sub__(self, Other):
		"""
		Operation: -
		"""
#		logging.debug("Operation '{0}'-'{1}'.".format(self, Other))
		#Test if current calling line has to be skipped.
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__sub__] Tracer.MergedData:", Tracer.MergedData)
#				print("Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[sub] {0}-{1} => Inst:".format(self, Other), Inst)
				return Inst
				
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar-Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=list())
			PythonVar=self.SyntheSys__PythonVar-Other
			
		D=Data(
			Name="{0}-{1}".format(Parent1, Parent2), 
			Operation=Op("__sub__", InputList=[Parent1, Parent2]),
			PythonVar=PythonVar,
			Parents=[Parent1, Parent2])
		return D
			
	#-------------------------------------------------
	def __mul__(self, Other):
		"""
		Operation: *
		"""
#		logging.debug("Operation '{0}'*'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__mul__] Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[mult] {0}*{1} => Inst:".format(self, Other), Inst)
				return Inst
				
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar*Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=self.SyntheSys__PythonVar*Other
		D=Data(
			Name="{0}*{1}".format(Parent1, Parent2), 
			Operation=Op("__mul__", InputList=[Parent1, Parent2]),
			PythonVar=PythonVar, 
			Parents=[Parent1, Parent2])
			
		return D
			
	#-------------------------------------------------
	def __floordiv__(self, Other):
		"""
		Operation: // 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __mod__(self, Other):
		"""
		Operation: %
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __divmod__(self, Other):
		"""
		Operation: divmod()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __pow__(self, Other, modulo=None):
		"""
		Operation: pow() and **
		"""
#		logging.debug("Operation '{0}'*'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__mul__] Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[mult] {0}*{1} => Inst:".format(self, Other), Inst)
				return Inst
				
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar*Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=pow(self.SyntheSys__PythonVar, Other)
		D=Data(
			Name="{0}^{1}".format(Parent1, Parent2), 
			Operation=Op("__pow__", InputList=[Parent1, Parent2]),
			PythonVar=PythonVar, 
			Parents=[Parent1, Parent2])
			
		return D
			
	#-------------------------------------------------
	def __lshift__(self, Other):
		"""
		Operation: <<
		"""
		Child = self[1:].append(0) # remove upleft bit add 0 to the upright bit
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return Child
			
	#-------------------------------------------------
	def __rshift__(self, Other):
		"""
		Operation: >> 
		"""
		if self.Signed:
			Child = self[:-1].insert(0, 0)
			# remove upright bit add 0 to the upleft bit
		else:
			Child = self[:-1].insert(1, 0)
			# remove upright bit add 0 to the upleft bit
			
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return Child
			
	#-------------------------------------------------
	def __and__(self, Other):
		"""
		Operation: &
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __xor__(self, Other):
		"""
		Operation: ^
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __or__(self, Other):
		"""
		Operation: |
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __div__(self, Other):
		"""
		Operation: /
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __truediv__(self, Other):
		"""
		Operation: / (when futur.division is called)
		"""
#		logging.debug("Operation '{0}'/'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
				Inst=Tracer.MergedData.pop(0)
#				print("[mult] {0}*{1} => Inst:".format(self, Other), Inst)
				return Inst
				
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar/Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=self.SyntheSys__PythonVar*Other
		D=Data(
			Name="{0}/{1}".format(Parent1, Parent2), 
			Operation=Op("__truediv__", InputList=[Parent1, Parent2]),
			PythonVar=PythonVar, 
			Parents=[Parent1, Parent2])
			
		return D
			
	#-------------------------------------------------
	def __radd__(self, Other):
		"""
		Binary +
		"""
#		logging.debug("Operation '{0}'+'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__add__] Tracer.MergedData:",  Tracer.MergedData)
#				print("Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[add] {0}+{1} => Inst:".format(self, Other), Inst)
				return Inst
#		print("Argument {0} is a merge: {1}".format(self, self.IsMerged()))
		# New name must take into account the last assignment (cf. Method "Name")
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar+Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=self.SyntheSys__PythonVar+Other
		D=Data(
			Name="{0}+{1}".format(Parent1, Parent2), 
			Operation=Op("__radd__", InputList=[Parent1, Parent2]), 
			PythonVar=PythonVar,
			Parents=[Parent1, Parent2])
			
		return D
#		frame,filename,line_number,function_name,lines,index=inspect.getouterframes(inspect.currentframe())[1]
##		raw_input("Calling line: {0}".format(lines[0]))
#		OtherName = lines[0].split("+=")[0].strip() # TODO: get the last name of the string
#		if not isinstance(Other, Data):
#			Other = Data(Name=OtherName, PythonVar=Other)
#		Parent1=self.LastAssignment()
#		Parent2=Other.LastAssignment()
#		return Data(
#				Name="{0}+{1}.".format(Parent2, Parent1), 
#				Operation=Op("__add__", InputList=[Parent1, Parent2]), 
#				PythonVar=self.SyntheSys__PythonVar+Other.SyntheSys__PythonVar,
#				Parents=[Parent1, Parent2])
			
	#-------------------------------------------------
	def __rsub__(self, Other):
		"""
		Binary-
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rmul__(self, Other):
		"""
		Binary *
		"""
#		logging.debug("Operation '{0}'*'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
#				print("[Data.__mul__] Tracer.MergedData:", Tracer.MergedData)
				Inst=Tracer.MergedData.pop(0)
#				print("[mult] {0}*{1} => Inst:".format(self, Other), Inst)
				return Inst
				
		Parent1=self.LastAssignment()
		if isinstance(Other, Data):
			Parent2=Other.LastAssignment()
			PythonVar=self.SyntheSys__PythonVar*Other.SyntheSys__PythonVar
		else:
			Parent2=Data(
				Name="Const({0})".format(Other), 
				Operation=None, 
				PythonVar=Other,
				Parents=[])
			PythonVar=self.SyntheSys__PythonVar*Other
		D=Data(
			Name="{0}*{1}".format(Parent1, Parent2), 
			Operation=Op("__mul__", InputList=[Parent1, Parent2]),
			PythonVar=PythonVar, 
			Parents=[Parent1, Parent2])
			
		return D
			
	#-------------------------------------------------
	def __rdiv__(self, Other):
		"""
		Binary /
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rtruediv__(self, Other):
		"""
		Binary /
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rfloordiv__(self, Other):
		"""
		Binary /
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rmod__(self, Other):
		"""
		Binary  %
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rdivmod__(self, Other):
		"""
		Binary divmod()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rpow__(self, Other):
		"""
		Binary pow() and **
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rlshift__(self, Other):
		"""
		Binary <<
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rrshift__(self, Other):
		"""
		Binary >>
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rand__(self, Other):
		"""
		Binary &
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __rxor__(self, Other):
		"""
		Binary ^
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ror__(self, Other):
		"""
		Binary |
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __iadd__(self, Other):
		"""
		Operation and assignment: += 
		"""
		return self+Other
			
	#-------------------------------------------------
	def __isub__(self, Other):
		"""
		Operation and assignment: -= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __imul__(self, Other):
		"""
		Operation and assignment: *= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __idiv__(self, Other):
		"""
		Operation and assignment: /= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __itruediv__(self, Other):
		"""
		Operation and assignment: //= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ifloordiv__(self, Other):
		"""
		Operation and assignment: //=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __imod__(self, Other):
		"""
		Operation and assignment: %=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ipow__(self, Other, modulo=None):
		"""
		Operation and assignment:  **= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ilshift__(self, Other):
		"""
		Operation and assignment: <<=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __irshift__(self, Other):
		"""
		Operation and assignment: >>=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __iand__(self, Other):
		"""
		Operation and assignment:  &=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ixor__(self, Other):
		"""
		Operation and assignment: ^=
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __ior__(self, Other):
		"""
		Operation and assignment: |= 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __neg__(self):
		"""
		Unary arithmetic operations: -
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __pos__(self):
		"""
		Unary arithmetic operations: +
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __abs__(self):
		"""
		Unary arithmetic operations: abs()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __invert__(self):
		"""
		Unary arithmetic operations: ~
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __complex__(self):
		"""
		Function: complex()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __int__(self):
		"""
		Function: int()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return
			
	#-------------------------------------------------
	def __long__(self):
		"""
		Function: long()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __float__(self):
		"""
		Function: float()
		"""
#		logging.debug("Operation '{0}'/'{1}'.".format(self, Other))
		for SkipL in Tracer.SkipLines:
			if SkipL.SkipCurrent() is True:
				Inst=Tracer.MergedData.pop(0)
#				print("[mult] {0}*{1} => Inst:".format(self, Other), Inst)
				return Inst
		
		Parent = self.LastAssignment()
		D=Data(
			Name="float({0})".format(Parent), 
			Operation=Op("__float__", InputList=[Parent, ]),
			PythonVar=float(self.SyntheSys__PythonVar), 
			Parents=[Parent, ]
			)
			
		return D
			
	#-------------------------------------------------
	def __oct__(self):
		"""
		Functions: oct()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __hex__(self):
		"""
		Functions: hex()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __index__(self):
		"""
		Implements Operation.index()
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
			
	#-------------------------------------------------
	def __coerce__(self, Other):
		"""
		Called to implement 'mixed-mode' numeric arithmetic. 
		Should either return a 2-tuple containing self and Other converted to a common numeric type, or None if conversion is impossible.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return

	#-------------------------------------------------
	def __round__(self, n):
		"""
		Implements behavior for the buil in round() function. n is the number of decimal places to round to.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __floor__(self):
		"""
		Implements behavior for math.floor(), i.e., rounding down to the nearest integer.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __ceil__(self):
		"""
		Implements behavior for math.ceil(), i.e., rounding up to the nearest integer.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __trunc__(self):
		"""
		Implements behavior for math.trunc(), i.e., truncating to an integral. 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __int__(self):
		"""
		Implements type conversion to int.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __long__(self):
		"""
		Implements type conversion to long.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __complex__(self):
		"""
		Implements type conversion to complex.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __oct__(self):
		"""
		Implements type conversion to octal.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __hex__(self):
		"""
		Implements type conversion to hexadecimal.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __index__(self):
		"""
		Implements type conversion to an int when the object is used in a slice expression. If you define a custom numeric type that might be used in slicing, you should define __index__.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __trunc__(self):
		"""
		Called when math.trunc(self) is called. __trunc__ should return the value of `self truncated to an integral type (usually a long).
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 

		
	#-------------------------------------------------
	def __coerce__(self, Other):
		"""
		Method to implement mixed mode arithmetic. __coerce__ should return None if type conversion is impossible. Otherwise, it should return a pair (2-tuple) of self and Other, manipulated to have the same type. 
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __unicode__(self):
		"""
		Defines behavior for when unicode() is called on an instance of your class. unicode() is like str(), but it returns a unicode string. Be wary: if a client calls str() on an instance of your class and you've only defined __unicode__(), it won't work. You should always try to define __str__() as well in case someone doesn't have the luxury of using unicode.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return "{0}".format(self.SyntheSys___name__)

		
#	#-------------------------------------------------
#	def __format__(self, formatstr):
#		"""
#    		Defines behavior for when an instance of your class is used in new-style string formatting. For instance, "Hello, {0:abc}!".format(a) would lead to the call a.__format__("abc"). This can be useful for defining your own numerical or string types that you might like to give special formatting options.
#		"""
#		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
#		return 

		
	#-------------------------------------------------
	def __dir__(self):
		"""
		Defines behavior for when dir() is called on an instance of your class. This method should return a list of attributes for the user. Typically, implementing __dir__ is unnecessary, but it can be vitally important for interactive use of your classes if you redefine __getattr__ or __getattribute__ (which you will see in the next section) or are Otherwise dynamically generating attributes.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
		
	#-------------------------------------------------
	def __sizeof__(self):
		"""
		Defines behavior for when sys.getsizeof() is called on an instance of your class. This should return the size of your object, in bytes. This is generally more useful for Python classes implemented in C extensions, but it helps to be aware of it.
		"""
		logging.error("Data Operation '{0}' not available yet.".format(inspect.stack()[0][3]))
		return 
	#-------------------------------------------------
	def __hash__(self):
		"""
		Defines behavior for when hash() is called on an instance of your class. It has to return an integer, and its result is used for quick key comparison in dictionaries. Note that this usually entails implementing __eq__ as well. Live by the following rule: a == b implies hash(a) == hash(b).
		"""
		return hash(str(self)) #self.ID # hash(self.ID)
	#-------------------------------------------------
	def DataSelection(self, Selector, FalseSelector=None, TestGroup=None):
		"""
		return Data output of SelectionOperator for specified TestedData.
		"""
#		print("Selector:", Selector)
#		print("self.SyntheSys__Selectors:",self.SyntheSys__Selectors)
#		print("self:",self)
		if Selector in self.SyntheSys__Selectors:
#			input()
			return self.SyntheSys__Selectors[Selector]
		else:
#			print("NO, SELECTOR NOT IN",self,"'s __Selectors__")
#			input()
			if FalseSelector in self.SyntheSys__Selectors:
				SelectInput=self.SyntheSys__Selectors[FalseSelector].GetSelected(Selection=False)
			else:
				SelectInput=self
			S=Switch.SwitchOperation(InputData=SelectInput, Selector=Selector, TestGroup=TestGroup)
			self.SyntheSys__Selectors[Selector]=S
			return S

#=========================================================
def GetSize(Element):
	"""
	Return bit width of a python variable : TODO
	"""
	if isinstance(Element, int):
		Size = 1 # TODO
	elif isinstance(Element, list):
		Size = len(Element)
	else:
		Size = 0
		logging.error("Cannot determine bitwidth of '{0}' element '{1}'".format(type(Element), Element))
	return Size
    
#=========================================================
def GetCondBlock(OuterFrameNb=2):
	"""
	return a 3 sized tuple:
		TrueValue, TrueBlock, BlockContext
	"""
	# First get 2 outerframe
	frame,filename,line_number,function_name,lines,index=inspect.getouterframes(inspect.currentframe())[OuterFrameNb]
	# Then evaluate the test and find Next indentation block value to return
#	raw_input("TEST LINE: {0}".format(lines))
#	raw_input("Frame source: {0}".format(inspect.getsourcelines(frame)))
#	raw_input("line_number: {0}".format(line_number))
#	raw_input("function_name: {0}".format(function_name))
	FrameLines, StartLine = inspect.getsourcelines(frame)
	#-----
	TrueBlock = GetNextIndentedBlock(SourceLines=FrameLines, LineNb=line_number-StartLine)
	#-----
	logging.debug("TrueBlock: {0}".format(TrueBlock))
	#-----
	return TrueBlock, frame.f_locals, frame.f_globals
    
#=========================================================
def GetNextIndentedBlock(SourceLines, LineNb=0):
	"""
	return code of indented block just after specified line
	"""
	# First find the level of indentation of line at LineNb
	IndentLevel=GetIndentLevel(SourceLines[LineNb])
	BlockLines=[]
	for Line in SourceLines[LineNb+1:]:
		if GetIndentLevel(Line)>IndentLevel:
			BlockLines.append(Line.replace('\t', '', IndentLevel+1))
		else:
			break
	if SourceLines[LineNb].find(':')!=-1:
		return SourceLines[LineNb][SourceLines[LineNb].find(':')+1:]+''.join(BlockLines)
	else:
		return ''.join(BlockLines)
    
#=========================================================
def GetIndentLevel(Line):
	"""
	return indented level of specified line
	"""
	return Line.find(Line.lstrip())
    
#=========================================================
def MergeModels(Instances, PInstances):
	"""
	return indented level of specified line
	"""
	pass

#=========================================================
def ByteCode(VarName):
	import inspect
	CurFrame = inspect.currentframe()
	CallingFrames = inspect.getouterframes(CurFrame, 2)
	
	print("CallingFrames[2]")
	print(CallingFrames[2])
	input()
	print("Index:", CallingFrames[2][5])
	StartLineNb=CallingFrames[2][2]
	print("StartLineNb:", )
	input()
	CodeLine=CallingFrames[2][4][CallingFrames[2][5]]
	print("Code line:", CodeLine)
	input()
	print("VarName:", VarName)
	print("Branch type: '{0}'".format(CodeLine[:CodeLine.index(VarName)].split()[-1]))
	input()
	import dis
	import opcode, code
	FCode=CallingFrames[2][0].f_code
	dis.dis(FCode)
	CodeList=list(FCode.co_code)
	print("CodeList:", CodeList)
	input()
	# Finds the offsets which are starts of lines in the source code. 
	LineStarts=dis.findlinestarts(FCode) # They are generated as (offset, lineno) pairs.
	# Get the start line offset of the test
	for Offset, LineNb in LineStarts:
		print(LineNb)
		if StartLineNb<=LineNb:
			StartOffset=Offset
			break
	# Get the start and end offset of the sub-block
	# 1 - first find the first non already read "POP_JUMP_IF_FALSE"
	# 2 - save the offset-1
	POPJPCode = opcode.opmap['POP_JUMP_IF_FALSE']
	print("POPJPCode:", POPJPCode)
	input()
	for i, OpCode in enumerate(CodeList[StartOffset:]):
		print(OpCode)
		if OpCode==POPJPCode:
			print("i:", i)
			EndOffset=CodeList[StartOffset+i+1]
			StartOffset=StartOffset+i+3 # 3 bytes for arguments
			break
	print("StartOffset:", StartOffset)
	print("EndOffset:", EndOffset)
	input()
	
	# Remove all code that is not in the conditional sub-block
	CodeList=CodeList[StartOffset:EndOffset-1]
	if CodeList[-2]==opcode.opmap['JUMP_FORWARD']:
		CodeList=CodeList[:-3]
		
	print("New CodeList:", CodeList)
	input()
	# int argcount, int nlocals, int stacksize, int flags, PyObject *code, PyObject *consts, PyObject *names, PyObject *varnames, PyObject *freevars, PyObject *cellvars, PyObject *filename, PyObject *name, int firstlineno, PyObject *lnotab
	TrueCondCode = type(FCode)(
			0,
			0,
			0,
			0,
			0,
			bytes(CodeList),
			tuple(),
			tuple(),
			tuple(),
			str(),
			str(),
			int(),
			bytes()
			)
	TrueCondCode = type(FCode)(
			0,#FCode.co_argcount,
			0,#FCode.co_kwonlyargcount,
			FCode.co_nlocals,
			FCode.co_stacksize,
			FCode.co_flags,
			bytes(CodeList),
			FCode.co_consts,
			FCode.co_names,
			FCode.co_varnames,
			FCode.co_filename,
			FCode.co_name,
			FCode.co_firstlineno,
			FCode.co_lnotab,
			FCode.co_freevars,
			FCode.co_cellvars
			)
	exec(TrueCondCode)
	
	
NESTED_TEST_CODE=[]
NESTED_TEST_CODE_LINE_NB=0


#=========================================================
def GetConditionalBlocks(TestedData):
	"""
	return a list of sub-block sub-lines
	"""
	global NESTED_TEST_CODE
	global NESTED_TEST_CODE_LINE_NB
	CurFrame = inspect.currentframe()
	CallingFrames = inspect.getouterframes(CurFrame, 2)
	CallingFrame  = CallingFrames[3][0]
	try: 
		SourceLines, StartLineNb=inspect.getsourcelines(CallingFrame)
		TestLineNb=CallingFrames[3][2]-StartLineNb
		NESTED_TEST_CODE=SourceLines
		NESTED_TEST_CODE_LINE_NB=TestLineNb
	except: 
		SourceLines=NESTED_TEST_CODE
		StartLineNb=NESTED_TEST_CODE_LINE_NB
		TestLineNb=CallingFrames[3][2]+StartLineNb-1
	# Inline if/else
	# Normal if/else statements
	BranchReturnValue=False
	TestLine=SourceLines[TestLineNb]
	if TestLine.expandtabs().lstrip().startswith('while'):
		pass
	elif TestLine.expandtabs().lstrip().startswith('if'):
		Data.BranchStack.append([])
		pass
	elif TestLine.expandtabs().lstrip().startswith('elif'):
		if Data.BranchStack[-1]:
			BranchReturnValue=Data.BranchStack[-1].pop(0)
		else: # Nothing in branch stack => return False for each branch
			BranchReturnValue=False
		# We must replace dummy elif TestedData by new one
		Dummy, Sel=Data.Dummies.pop(0)
		
		Switch.ReplaceSelector(Dummy, TestedData)
		TestGroup.ReplaceDummyTests(Dummy, TestedData)
		
		for M in Select.SelectOperation.Instances:
			if M.TestedData is Dummy:
				M.TestedData=TestedData
		return None # Do nothing
	else:
		logging.error("[SyntheSys.Analysis.GetConditionalBlocks] Test not supported. Aborted.")
		logging.error("Line:", TestLine.expandtabs().lstrip())
		sys.exit(1)
		
	RefIndentLevel=Misc.IndentationLevel(TestLine, TabSize=8)#len(TestLine)-len(TestLine.lstrip('\t'))
	EndifLineNb=TestLineNb
	for i, Line in enumerate(SourceLines[TestLineNb+1:]):
		if Line.expandtabs().lstrip().startswith('#'): continue
		IndentLevel=Misc.IndentationLevel(Line, TabSize=8)#len(TestLine)-len(TestLine.lstrip('\t'))
		if IndentLevel<=RefIndentLevel:
			EndifLineNb=i
			break
	
	# Elif and else source lines------------------------------
	ElseFound=ElifFound=False
	ElseLineNb=None
	EndElseLineNb=None
	ElifLineNb=TestLineNb
	ElifBlockLinesList = []
	for i, Line in enumerate(SourceLines[TestLineNb+1:]):
		if Line.lstrip().startswith('#'): continue
		IndentLevel=Misc.IndentationLevel(Line, TabSize=8)#len(TestLine)-len(TestLine.lstrip('\t'))
		# Seek else line # TODO : consider ';' 
		if ElseFound is False:
			if IndentLevel==RefIndentLevel and Line.expandtabs().lstrip().startswith('elif'):
#				print("Found ELIF")
				if ElifFound is True:
					ElifBlockLinesList.append(SourceLines[ElifLineNb+1:TestLineNb+i+1])
				ElifFound=True
				ElifLineNb=TestLineNb+i+1
				# Evaluate elif test condition (operations depend on previous if/elif condition)
				continue
			elif IndentLevel==RefIndentLevel and Line.expandtabs().lstrip().startswith('else'):
				if ElifFound is True:
					ElifBlockLinesList.append(SourceLines[ElifLineNb+1:TestLineNb+i+1])
				ElseFound=True
				ElifFound=False
				ElseLineNb=TestLineNb+i+1
				continue
			else:
				if IndentLevel<=RefIndentLevel:
					pass
				else:
					# inside a if or elif block
					continue
		# Check end of else or end of if/elif branches
		if IndentLevel<=RefIndentLevel:
			if ElifFound is True:
				ElifBlockLinesList.append(SourceLines[ElifLineNb+1:TestLineNb+i+1])
			EndElseLineNb=TestLineNb+i
			break
	if EndElseLineNb is None:
		# Last line of code
		EndElseLineNb=TestLineNb+i+1
	#---------------------------------------------------------
	# Save else's lines (will disable data production for these lines)
	AbsoluteTestLineNb=StartLineNb+TestLineNb
	if ElseLineNb is None: ElseSkip=None
	else: 
		ElseSkip = SkipLines(AbsoluteTestLineNb, RefIndentLevel, slice(StartLineNb+ElseLineNb+1, StartLineNb+EndElseLineNb+1), SourceLines[ElseLineNb+1:EndElseLineNb+1]) # SkipLines object
	
	# Trim left indent
	ReadyToExecutLines = [L.replace('\t'*(RefIndentLevel+1), '') for L in SourceLines[TestLineNb+1:TestLineNb+1+EndifLineNb] if not L.isspace()]
	ElifBlocks=[]
	for EL in ElifBlockLinesList:
		ElifBlocks.append([L.replace('\t'*(RefIndentLevel+1), '') for L in EL if not L.isspace()])
		
	SplitTLines=TestLine.split(';')
	if len(SplitTLines)>1: ReadyToExecutLines=SplitTLines[1:]+ReadyToExecutLines # TODO manage ';' in strings
	
	TestGroup.GatherSelectors()

	return ReadyToExecutLines, ElifBlocks, ElseSkip, CallingFrame.f_globals, CallingFrame.f_locals, CallingFrame, BranchReturnValue

#=========================================================
def StripReturnExpression(PythonLine):
	"""
	return the string with return statement if present.
	"""
	for Line in PythonLine.split(';'): # TODO: manage ';' in strings
		L=Line.expandtabs().lstrip()
		if L.startswith('return'):
			return L.replace('return', '')
	return None
	
#=========================================================
def MergeTracers(TestedData, Selection, TrueValue, FalseValue, SelectG):
	"""
	Given to 'locals' dictionaries, instanciate a Select (merge) node for two different data of same name.
	Return a new 'locals' dictionary.
		TestOp     : Test operation that causes True selection
		TrueValue  : 
		FalseValue : 
	"""
#	print("MergeTracers:\n\tTestedData=", TestedData, ",\n\tTrueValue=", TrueValue, ", \n\tFalseValue=", FalseValue, ",\n\tSelection", Selection)
	if not isinstance(TrueValue, Data):
		TrueValue=Data(
				Name=str(Data), 
				Operation=None, 
				PythonVar=TrueValue,
				Parents=[])
#	if FalseValue is None: # IF branch
#		return TrueValue.Merge(TestedData, SelectValue=Selection, Other=None)
#	else: # IF branch
	return TrueValue.Merge(TestedData, SelectValue=Selection, Other=FalseValue, SelectG=SelectG)
#	elif isinstance(FalseValue, Data): # An ELIF branch
#		return FalseValue.Merge(TestedData, SelectValue=Selection, Other=TrueValue)
#	else: # both are constants or None
#		if FalseValue is None:
#			FValue=None
#		else:
#			FValue=Data(
#				Name=str(Data), 
#				Operation=None, 
#				PythonVar=FalseValue,
#				Parents=[])
#		TValue=Data(
#			Name=str(Data), 
#			Operation=None, 
#			PythonVar=TrueValue,
#			Parents=[])
#		return TValue.Merge(TestedData, SelectValue=False, Other=FalseValue)
			
#================================================================
def DiffLocals(OldLocals, NewLocals):
	"""
	return dictionary of values that are different.
	"""
	DiffDict={}
	for k,v in NewLocals.items():
		if k in OldLocals:
			if not (OldLocals[k] is v): 
				DiffDict[k]=v
		else:
			DiffDict[k]=v
	return DiffDict

#================================================================
def GetMergeDict(TestedData, Selection, OldLocals, DiffDict, SelectG):
	"""
	return new dictionary of locals
	"""
	MergedDict={}
	for k,v in DiffDict.items():
		if k in OldLocals:
			OldData=OldLocals[k]
			if Selection is True: # IF or ELIF CONDITION
				O=MergeTracers(TestedData, Selection, v, None, SelectG=SelectG)
				NewData=OldData.Merge(TestedData, SelectValue=not Selection, Other=O, SelectG=SelectG)
				MergedDict[k]=NewData
			else: # ELSE condition
				if OldData.IsSelected(): # IF CONDITION
					NewData=OldData.Merge(TestedData, SelectValue=Selection, Other=v, SelectG=SelectG)
					MergedDict[k]=NewData
				else:
					NewData=OldData.Merge(TestedData, SelectValue=Selection, Other=v, SelectG=SelectG)
					MergedDict[k]=NewData
		else:
			MergedDict[k]=MergeTracers(TestedData, Selection, v, None, SelectG=SelectG)
	return MergedDict

#================================================================
def CondBranchAnalysis(TestedData):
	"""
	Execute each conditional sub-block, else included.
	Evaluate returned items and update eventually the current locals with merged values.
	"""
	Returned=[]
	TestOp=TestedData.GetProducer()
	ExecContext=GetConditionalBlocks(TestedData=TestedData)
	if ExecContext is None: return False
	TrueBlockLines, ElifBlockLinesList, ElseSkipLines, OriGlobals, OriLocals, CallingFrame, BranchReturnValue=ExecContext
	Locals, Globals=OriLocals.copy(), OriGlobals.copy()
	ReturnedExp=StripReturnExpression(TrueBlockLines[-1])
	SelectGs=SelectGroup.SelectGroup()
	Tests=TestGroup.TestGroup(TestChain=dict(), Selectors=dict(), SelectGroup=SelectGs)
	Op.Selector=(TestedData, True, None, Tests, 0)

	
	# Keep tracks of Select operators
	if ReturnedExp: 
		exec('\n'.join(TrueBlockLines[:-1]), Globals, Locals)
		RetData=eval(ReturnedExp, Globals, Locals)
	else:
		exec('\n'.join(TrueBlockLines), Globals, Locals)
		RetData=None
	
	DiffDict=DiffLocals(OriLocals, Locals)
	MergedDict=GetMergeDict(TestedData, True, OriLocals, DiffDict, SelectG=SelectGs)
	if not(RetData is None):	
		Returned.append( (TestedData,RetData) )
	# ELIF(s)
	Dummies=[]
	i=0
	for ElifBlockLines in ElifBlockLinesList:
		DummyTestData=Data("DUMMY", PythonVar=bool())
		Dummies.append( (DummyTestData, True) )
		i+=1
		TestedData=DummyTestData
		Op.Selector=(TestedData, True, TestedData, Tests, i)
		
		ReturnedExp=StripReturnExpression(ElifBlockLines[-1])
		Locals, Globals=OriLocals.copy(), OriGlobals.copy()
		if ReturnedExp: 
			exec('\n'.join(ElifBlockLines[:-1]), Globals, Locals)
			RetData=eval(ReturnedExp, Globals, Locals)
			Data.BranchStack[-1].append(False)
		else:
			exec('\n'.join(ElifBlockLines), Globals, Locals)
			RetData=None
			Data.BranchStack[-1].append(True)
			
		DiffDict=DiffLocals(OriLocals, Locals)
		MergedDict=GetMergeDict(DummyTestData, True, MergedDict, DiffDict, SelectG=SelectGs)

		if not(RetData is None):
			# Check if already merged
			AlreadyMerged=False
			for Children in RetData.SyntheSys__Children.values():
				for Child in Children:
					if Child.IsMerged():
						if Child._Producer.TestedData is TestedData:
							# Already merged
							AlreadyMerged=True
							break
			if AlreadyMerged is False:
				Returned.append( (TestedData,RetData) )
	
	# ELSE
	if ElseSkipLines:
		Op.Selector=(Op.Selector[0], False, None, None, i+1)
		Locals, Globals=OriLocals.copy(), OriGlobals.copy()
		ElseLines=ElseSkipLines.GetLines()
		ElseLines=RemoveComments([Line for Line in ElseLines if Misc.IndentationLevel(Line, TabSize=8)==0])
		ReturnedExp=StripReturnExpression(ElseLines[-1])
		if ReturnedExp is None: 
#			print("execute:", ElseLines)
			exec('\n'.join(ElseLines), Globals, Locals)
			RetData=None
			Data.BranchStack[-1]=[] # Clear list of returned values => default behavior
		else:
			exec('\n'.join(ElseLines[:-1]), Globals, Locals)
			RetData=eval(ReturnedExp, Globals, Locals)
	
		DiffDict=DiffLocals(OriLocals, Locals)

		MergedDict=GetMergeDict(TestedData, False, MergedDict, DiffDict, SelectG=SelectGs)

		if not(RetData is None):
			# Check if already merged
			AlreadyMerged=False
			for Children in RetData.SyntheSys__Children.values():
				for Child in Children:
					if Child.IsMerged():
						if Child._Producer.TestedData is TestedData:
							# Already merged
							AlreadyMerged=True
							break
			if AlreadyMerged is False:
				Returned.append( (None, RetData) )
				
		Tracer.SkipLines.append(ElseSkipLines)
	
	# Merge returned values
	MergedReturn=MergeReturnedValues(Returned, SelectG=SelectGs)
	
	# TODO : use O as value for skipped return statement
	ReturnInBranch_LineNb=None # TODO : FIX IT
	if not (ReturnInBranch_LineNb is None):
		SR=SkipReturn(LineNb=None, RefIndentLevel=None, Expression=None, MergedReturn=MergedReturn)
		
	CallingFrame.f_locals.update(MergedDict)
	
	Op.Selector=None # Deactivate selection
	Data.Dummies=Dummies
	TestGroup.GatherSelectors()
	return BranchReturnValue


#========================================================
def MergeReturnedValues(Returned, SelectG):
	"""
	return List of lines without lines that starts with #
	"""
	if not Returned: return None
	TestedData, RetData=Returned.pop(0)
	LastMerge=MergeTracers(TestedData, True, RetData, None, SelectG=SelectG)
	FinalMerge=LastMerge
	for TestedData, Value in Returned:
		if TestedData is None:
			LastMerge.Merge(None, SelectValue=False, Other=Value, SelectG=SelectG)
		else:
				NewMerge=MergeTracers(TestedData, True, Value, None, SelectG=SelectG)
				LastMerge.Merge(TestedData, SelectValue=False, Other=NewMerge, SelectG=SelectG)
				LastMerge=NewMerge
	return FinalMerge
		
		

#========================================================
def RemoveComments(Lines):
	"""
	return List of lines without lines that starts with #
	"""
	LinesWithoutComments=[]
	for Line in Lines:
		L=Line.expandtabs().lstrip()
		if L.startswith('#'): continue
		LinesWithoutComments.append(Line)
	return LinesWithoutComments

#========================================================


#TODO: 
# 	Implement signed/unsigned integer data types
# 	Implement signed/unsigned fixed/floating point data types
# 	Handle OVERFLOWS/SATURATIONS
# 	Operators : /, &, |, ^, %, *, -, +, >>, <<
# 	Choice: use divider or not (CORDIC algo) | use of shifts for constant power of 2 division
# 	Tests de signe de nombre par test du bit de signe
#
#
#

