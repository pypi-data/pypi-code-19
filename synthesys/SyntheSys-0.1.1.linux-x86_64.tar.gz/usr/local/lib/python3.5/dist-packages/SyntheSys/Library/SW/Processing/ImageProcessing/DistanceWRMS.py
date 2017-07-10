#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm


import math


Longueur=9
#======================================================================
@Synthesizable
class __BASICBLOCK__DistanceWRMS(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="DistanceWRMS")
		Inputs=collections.OrderedDict([
			('Tab1',[1 for i in range(9)]), 
			('Tab2',[1 for i in range(9)]),
			])
		Outputs=collections.OrderedDict([
			('DistanceWRMS', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def DistanceWRMS(self, Tab1, Tab2):
		"""
		return the sum of the inputs.
		"""
		global Longueur
		Sum=0
		for i in range(len(Tab1)):
			Sum=math.fabs(Tab1[i]-Tab2[i])*math.fabs(Tab1[i]-Tab2[i])/(math.sqrt(Tab1[i])*math.sqrt(Tab2[i]))+Sum
		dis_wrms=math.sqrt(Sum/Longueur)
		return dis_wrms
		
	
	
	
	

