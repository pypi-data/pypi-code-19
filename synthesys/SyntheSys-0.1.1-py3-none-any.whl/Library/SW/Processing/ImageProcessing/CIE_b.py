#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

#======================================================================
@Synthesizable
class __BASICBLOCK__CIE_b(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being consideCIE_b as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="CIE_b")
		Inputs=collections.OrderedDict([
			('X', 1), 
			('Y', 1),
			])
		Outputs=collections.OrderedDict([
			('CIE_b', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def CIE_b(self, Y, Z):
		"""
		return the sum of the inputs.
		"""
		var_Y=Y/100.000
		var_Z=Z/108.883
		if var_Y > 0.008856:
			var_Y = pow(var_Y,1/3)
		else:
			var_Y = (903.3 * var_Y + 16)/116
		if var_Z>0.008856:
			var_Z= pow(var_Z,1/3)
		else:
			var_Z = (903.3 * var_Z + 16)/116
		val_b=200*(var_Y-var_Z)
		return val_b
		
	
	
	
	

