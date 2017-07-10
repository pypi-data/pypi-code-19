#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm


#======================================================================
@Synthesizable
class __BASICBLOCK__Green(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being consideGreen as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="Green")
		Inputs=collections.OrderedDict([
			('X', 1), 
			('Y', 1),
			('Z', 1),
			])
		Outputs=collections.OrderedDict([
			('Green', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def Green(self, X, Y, Z):
		"""
		return the sum of the inputs.
		"""
		g=1.42530*Y-0.900040*X-0.014695*Z
		return g
		
	
	
	
	

