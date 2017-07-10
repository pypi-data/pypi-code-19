#!/usr/bin/python

import os, sys, datetime, logging
import HdlLib.SysGen.HDLEditor as HDL

#==================================================================
class Condition:
	"""
	Object that contains representation of condition on signals.
	"""
	#----------------------------------------------------------------------
	def __init__(self, StringCondition=None):
		"""
		Initialize AND and OR dictionary of conditions.
		"""
		self.StringCondition = StringCondition
		self._Conditions     = {"__and__":[], "__or__":[]}
		self._Signals        = []
		self.ComplementFlag  = False
		self.SyncAssignments = []
		
	#----------------------------------------------------------------------
	def Copy(self):
		"""
		Create a new Condition object with copy of all attributes
		"""
		C=Condition()
		C.StringCondition = self.StringCondition
		C._Conditions=self._Conditions.copy()
		C._Signals        = self._Signals[:]
		C.ComplementFlag  = self.ComplementFlag
		return C
	#----------------------------------------------------------------------
	def AddSyncAssignments(self, CondAssignmentsPairs):
		"""
		Add signals to be assigned when condition is verified
		"""
		self.SyncAssignments+=CondAssignmentsPairs
		return 
	#----------------------------------------------------------------------
	def AddANDCond(self, *Signals):
		"""
		Update the dictionary of condition concatenated with AND operator.
		"""
		HDLSigs=[x.HDLFormat() for x in Signals if not isinstance(x, HDL.Signal)]
		HDLSigs+=[x for x in Signals if isinstance(x, HDL.Signal)]
		for S in HDLSigs:
			self._Conditions["__and__"].append(S.Test())
		self._Signals+=Signals
		return
	#----------------------------------------------------------------------
	def AddORCond(self, Operator="__or__", *Signals):
		"""
		Update the dictionary of condition concatenated with OR operator.
		"""
		HDLSigs=[x.HDLFormat() for x in Signals if not isinstance(x, HDL.Signal)]
		HDLSigs+=[x for x in Signals if isinstance(x, HDL.Signal)]
		for S in Sigs:
			self._Conditions["__or__"].append(S.Test())
		self._Signals+=Signals
		return
	#----------------------------------------------------------------------
	def GetSignals(self):
		"""
		Return list of signal that take place in condition.
		"""
		return self._Signals
	#----------------------------------------------------------------------
	def Evaluate(self, Vars={}):
		"""
		return True if eval(StringCondition) return True
		"""
		return bool(eval(str(self.StringCondition), Vars))
	#----------------------------------------------------------------------
	def Complement(self):
		"""
		return complementary condition string representation.
		"""
		C=self.Copy()
		C.ComplementFlag=True
		return C 
		
	#----------------------------------------------------------------------
	def __bool__(self):
		"""
		return complementary condition string representation.
		"""
		if len(self._Signals)==0: return False
		else: return True
		
	#----------------------------------------------------------------------
	def __add__(self, Other):
		"""
		Concatenate conditions
		"""
		C=self.Copy()
		if C.StringCondition and Other.StringCondition:
			C.StringCondition+= Other.StringCondition
		C._Conditions.update(Other._Conditions) 
		C._Signals        += Other._Signals
		C.ComplementFlag = False
		return C
		
	#----------------------------------------------------------------------
	def __str__(self):
		"""
		Return string representation.
		"""
		if len(self._Signals)==0: return ""
		AndCode = HDL.OPSYMBOL_DICT["__and__"].join(self._Conditions["__and__"])
		ORCode  = HDL.OPSYMBOL_DICT["__or__"].join(self._Conditions["__or__"])
#		if len(ANDCondList)>0:
#			AndCode+='('+" and ".join(ANDCondList)+')'			
#		if len(ORCondList)>0:
#			ORCode+='('+" or ".join(ORCondList)
		if ORCode=="":
			if AndCode=="":
				Code=""
			else:
				Code=AndCode
		else:
			if AndCode=="":
				Code=ORCode
			else:
				Code=" and ".join([ORCode, AndCode])
			
			
		if self.ComplementFlag==True:
			return "not {0}".format(Code)
		else:
			return Code
		
#=======================================================================
def SigName(Code, OrderedIndexes=[], Vars={}, LocalParams={}):
	"""
	Parse signal name and return normalized name format.
	"""
	if Code.startswith('{') and Code.endswith('}'):
		ToConcatList = [S.strip('{').strip('}') for S in Code.split(',')]
	else:
		ToConcatList = [Code,]
	IndexedSigList = []
	#logging.debug("Code={0}".format(Code))
	for ToConcatSig in ToConcatList:
		try: Inst, Sig = ToConcatSig.split('.') # Separate signal name from instance name
		except: Inst, Sig = "", ToConcatSig
		# split instance name and indexes (when in loop)
		InstID = Inst.split(':')
		if InstID[0]=='': InstID[0]=Inst 
		#logging.debug("InstID={0}".format(InstID))
		
		for i in range(1, len(InstID)):
			try: InstID[i] = OrderedIndexes[i-1]+str(eval(InstID[i], Vars))
			except: logging.critical('Failed to get instance name for "{0}" in a loop. Make sur your indexed it (name="instance:var")'.format(InstID))
			
		if len(InstID)>1: InstName = "_".join([InstID[0], "".join(InstID[1:])])
		else: InstName = InstID[0]
		
		# Fetch local constants
		if list(LocalParams.keys()).count(Sig): Sig=LocalParams[Sig]
		# split signal name and indexes
		SigID = Sig.split(':')
		SigName = SigID[0]
		Index=None
		if len(SigID)>1:
			Range = SigID[1].split('~') # TODO: comment please !!!!
			Min=eval(Range[0], Vars)
			if len(Range)>1: 
				Max=eval(Range[1], Vars)
				Index=[Min, Max]
			else:
				Index=Min
		else:
			Index=None
		for i in range(1, len(SigID)):
			SigID[i] = eval(SigID[i], Vars)
		
		IndexedSigList.append([InstName, SigName, Index])
		if SigName=='': sys.exit(1)
	return IndexedSigList
			
#============================================================================
def GetActualName(ActualList, Vars={}):
	"""
	Return a value (string format) of actual signal described by a list.
	"""
	ConcatList, Cond, LocalVars = ActualList
	Variables=Vars.copy()
	Variables.update(Vars)
	if eval(str(Cond), Variables):
		for Inst, SigVal, Index in ConcatList:
			if len(Inst)<1:
				if Index==None:
					return str(SigVal)
				else:
					S=Signal(SigVal)
					S.SetIndex(Index)
					return S.Name
			else:
				if Index==None:
					return str(Inst)+'_'+str(SigVal)
				else:
					S=Signal(str(Inst)+'_'+str(SigVal))
					S.SetIndex(Index)
					return S.Name
					
	else:
		return None



#============================================================================
def ParseType(Type):
	"""
	Return subsize and subtype of type according to XML syntaxe.
	Size returned is None when it's not a subtype.
	"""
	Index = Type.rfind('*')
	if Index!=-1: # If type is complex (has subtype)
		SubType=Type[Index+1:].lower()
		if SubType in ["logic", "numeric"]:
			# Find subtype size			
			SubSize = Type[:Index].strip('(').strip(')')
	#		# Create new type from size * subtype
	#		NewType="{0}_{1}".format(SubSize.upper(), Type[Index+1:].upper())
			return SubType, SubSize, Type[Index+1:]
		# Else it's not a array type, it's a custom type.
		else: return None, None, Type
	else:
		return None, None, Type
	

