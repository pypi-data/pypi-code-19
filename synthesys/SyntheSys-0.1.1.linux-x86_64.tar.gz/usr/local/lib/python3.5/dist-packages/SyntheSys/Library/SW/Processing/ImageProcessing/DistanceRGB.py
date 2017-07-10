#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

import math


Longueur=9
#======================================================================
@Synthesizable
class __BASICBLOCK__DistanceRGB(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="DistanceRGB")
		Inputs=collections.OrderedDict([
			('R1', 1), 
			('G1', 1),
			('B1', 1),
			('R2', 1), 
			('G2', 1),
			('B2', 1),
			])
		Outputs=collections.OrderedDict([
			('DistanceRGB', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def DistanceRGB(self, R1, G1, B1, R2, G2, B2):
		"""
		return the sum of the inputs.
		"""
		deta_E= math.sqrt((R1-R2)*(R1-R2)+(G1-G2)*(G1-G2)+(B1-B2)*(B1-B2))
		return deta_E
		
	
	
	
	

