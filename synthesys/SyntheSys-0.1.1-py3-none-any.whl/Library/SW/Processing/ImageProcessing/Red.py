#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm


#======================================================================
@Synthesizable
class __BASICBLOCK__Red(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="Red")
		Inputs=collections.OrderedDict([
			('X', 1), 
			('Y', 1),
			('Z', 1),
			])
		Outputs=collections.OrderedDict([
			('Red', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def Red(self, X, Y, Z):
		"""
		return the sum of the inputs.
		"""
		r=2.37067*X-0.513885*Y+0.005298*Z
		return r
		
	
	
	
	

