#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

#======================================================================
@Synthesizable
class __BASICBLOCK__BOPMUnit(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="BOPM_Unit")
		Inputs=collections.OrderedDict([
			('Stim1', 1), 
			('Stim2', 1),
			])
		Outputs=collections.OrderedDict([
			('Trace', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def GetPrice(self, Stim1, Stim2):
		"""
		return the sum of the inputs.
		"""
#		if a<b: return a+b
#		else: return a-b
		return Stim1+Stim2
		
##======================================================================
#def BOPMUnit(*Args, **ArgDict):
#	"""
#	Wrapper for transparent library usage.
#	"""
#	return BB_BOPMUnit(*Args, **ArgDict)
	
	
	
	

