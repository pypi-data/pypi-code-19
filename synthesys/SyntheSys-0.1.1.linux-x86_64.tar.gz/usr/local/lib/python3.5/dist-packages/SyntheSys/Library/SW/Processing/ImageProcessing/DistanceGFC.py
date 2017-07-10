#!/usr/bin/python

import sys, os, logging
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

import math


Longueur=9
#======================================================================
@Synthesizable
class __BASICBLOCK__DistanceGFC(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="DistanceGFC")
		Inputs=collections.OrderedDict([
			('TabEs',[1 for i in range(9)]), 
			('TabMe',[1 for i in range(9)]),
			])
		Outputs=collections.OrderedDict([
			('DistanceGFC', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def DistanceGFC(self, TabEs, TabMe):
		"""
		return the sum of the inputs.
		"""
		if len(TabMe)+len(TabEs)==0:
			logging.error("[ImageProcessing.DistanceGFC] TabEs and TabMe inputs are empty. Exiting.")
			sys.exit(1)
		SumEs=0
		SumMe=0
		SumEM=0
		for i in range(len(TabEs)):
			SumEs+=TabEs[i]*TabEs[i]
			SumMe+=TabMe[i]*TabMe[i]
			SumEM+=TabEs[i]*TabMe[i]
		GFC=math.fabs(SumEM)/(math.sqrt(SumEs)*math.sqrt(SumMe))
		return GFC
		
	
	
	
	

