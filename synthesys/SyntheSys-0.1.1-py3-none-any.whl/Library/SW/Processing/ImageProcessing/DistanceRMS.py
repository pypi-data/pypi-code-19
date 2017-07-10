#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

import math

Longueur=9
#======================================================================
@Synthesizable
class __BASICBLOCK__DistanceRMS(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="DistanceRMS")
		Inputs=collections.OrderedDict([
			('Tab1',[1 for i in range(9)]), 
			('Tab2',[1 for i in range(9)]),
			])
		Outputs=collections.OrderedDict([
			('DistanceRMS', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def DistanceRMS(self, Tab1, Tab2):
		"""
		return the sum of the inputs.
		"""
		global Longueur
		Sum=0
		for i in range(len(Tab1)):
			Sum+=pow(Tab1[i]-Tab2[i], 2)
		dis_rms=math.sqrt(Sum)/Longueur
		return dis_rms
		
	
	
	
	

