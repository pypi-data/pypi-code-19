#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

#======================================================================
@Synthesizable
class __BASICBLOCK__CIE_L(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="CIE_L")
		Inputs=collections.OrderedDict([
			('Y', 1),
			])
		Outputs=collections.OrderedDict([
			('CIE_L', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def CIE_L(self, Y):
		"""
		return the sum of the inputs.
		"""
		var_Y = Y/100.000
		if var_Y>0.008856:
			var_Y = pow(var_Y,1/3)
		else:
			var_Y = (7.787*var_Y) + (16/116)
		val_l = (116*var_Y) - 16
		return val_l
		
	
	
	
	

