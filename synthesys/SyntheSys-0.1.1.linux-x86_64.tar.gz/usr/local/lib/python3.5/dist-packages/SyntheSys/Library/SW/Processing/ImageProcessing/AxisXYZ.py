#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

Longueur=9

#======================================================================
@Synthesizable
class __BASICBLOCK__AxisXYZ(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="AxisXYZ")
		Inputs=collections.OrderedDict([
			('TabSp',[1 for i in range(9)]), 
			('TabRef',[1 for i in range(9)]),
			])
		Outputs=collections.OrderedDict([
			('AxisXYZ', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def AxisXYZ(self, TabSp, TabRef):
		"""
		return the sum of the inputs.
		"""
		sum_axis=0
		if len(TabSp)>len(TabRef):
			print("[AxisXYZ] Error: Reference values '{0}' < processing values '{1}'. Aborted.".format(len(TabSp), len(TabRef)))
			sys.exit(1)
		for i in range(len(TabSp)):
			sum_axis+=TabSp[i]*TabRef[i]
		return sum_axis
		
	
	
	
	

