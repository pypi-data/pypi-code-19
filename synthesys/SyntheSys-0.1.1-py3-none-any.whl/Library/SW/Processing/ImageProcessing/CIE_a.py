#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

#======================================================================
@Synthesizable
class __BASICBLOCK__CIE_a(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being consideCIE_a as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="CIE_a")
		Inputs=collections.OrderedDict([
			('X', 1), 
			('Y', 1),
			])
		Outputs=collections.OrderedDict([
			('CIE_a', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def CIE_a(self, X, Y):
		"""
		return the sum of the inputs.
		"""
		var_X=X/95.047
		var_Y=Y/100.000
		if var_X > 0.008856:
			var_X = pow(var_X,1/3)
		else:
			var_X = (903.3*var_X + 16)/116
		if var_Y > 0.008856:
			var_Y = pow(var_Y,1/3)
		else:
			var_Y = (903.3*var_Y + 16)/116

		val_a=500*(var_X-var_Y)
		return val_a
		
	
	
	
	

