#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

#======================================================================
@Synthesizable
class __BASICBLOCK__TestNode(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="TestNode") # TODO : utiliser des contraintes => Module.BlackBoxFunction
		Inputs=collections.OrderedDict([
			('I', 1), 
			])
		Outputs=collections.OrderedDict([
			('O', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def GetPrice(self, I):
		"""
		return the sum of the inputs.
		"""
#		if a<b: return a+b
#		else: return a-b
		return I
		
##======================================================================
#def TestNode(*Args, **ArgDict):
#	"""
#	Wrapper for transparent library usage.
#	"""
#	return BB_TestNode(*Args, **ArgDict)
	
	
	
	

