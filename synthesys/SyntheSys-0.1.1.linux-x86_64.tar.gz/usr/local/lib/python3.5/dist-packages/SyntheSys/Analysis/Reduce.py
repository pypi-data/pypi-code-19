#! /usr/bin/python
"""
Merge operations
"""
import logging, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import SyntheSys.SysGen
from SyntheSys.Analysis.Operation import Operation

#=========================================================
class Reduce(Operation):
	Instances     = []
	ReducedInputs = []
	ReducedList   = []
	""" 
	Abstraction of Reducing operations.
	Object for synchronous data flow representation/simulation.
	"""		
	#-------------------------------------------------
	def __init__(self, InputList):
		"""
		Initialization of the Operation attributes.
		"""
		self._Name="Reduce"
		super().__init__(Name=self._Name, InputList=InputList)
		Reduce.Instances.append(self)
	#-------------------------------------------------
	def IsSwitch(self):
		return False
	#-------------------------------------------------
	def IsReduce(self):
		return True
	#-------------------------------------------------
#	def SubstituteBy(self, NewReduce):
#		"""
#		Remove selected link from output consumers's output parents
#		"""
#		for O in self.Outputs:
#			NewReduce.Outputs.append(O)
#			O.SyntheSys__Producer=NewReduce
#		
#		for I in self.Inputs:
#			I.SyntheSys__Children[NewReduce]=NewReduce.Outputs+self.Outputs
#			I.SyntheSys__Children.pop(self)
#		
#		return True
	#-------------------------------------------------
#	def Remove(self):
#		Reduce.Instances.remove(self)
#		Operation.Instances.remove(self)
#		return 
	#-------------------------------------------------
	def GetReduced(self):
		"""
		Return Reduced data output.
		"""
		if len(self.Output):
			return self.Output[0]
		else:
			return None
	#-------------------------------------------------
#	def GetOutputName(self, ShowID):
#		"""
#		Return None so the output data ID is taken from data itself (not SWITCH(DataName)).
#		"""
#		return None
	#-------------------------------------------------
	def NodeID(self, ShowID=True):
		"""
		return string representation.
		"""
		return "Reduce"+str(Operation.Instances.index(self))


#=========================================================
#def ReplaceReduce(P1, P2):
#	"""
#	Replace P1 by P2.
#	"""
#	P1.SubstituteBy(P2)
#	Reduce.Instances.remove(P1)
#		
#	return
		
			
		
		
		
		
		
		
		
		
		
		
