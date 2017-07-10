#!/usr/bin/python

import sys, os
import collections

from SyntheSys.Analysis.Module import HighLevelModule, Synthesizable
from SyntheSys.Analysis.SyntheSys_Algorithm import SyntheSys_Algorithm as Algorithm

import math

#Longueur=9
#======================================================================
@Synthesizable
class __BASICBLOCK__RegionMean(HighLevelModule):
	"""
	Option pricing tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		self.NbData=9
		Imp=self.SetService(ServiceName="RegionMean")
		Inputs=collections.OrderedDict([
			('DataList', [1.0 for i in range(self.NbData)]), 
			('NbElement', self.NbData), 
			])
		Outputs=collections.OrderedDict([
			('RegionMean', 1), 
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def RegionMean(self, DataList, NbElement=9):
		"""
		return the sum of the inputs.
		"""
		Sum=sum(DataList)
	#	EcritureData(Results=Moyenne, FilePath="tab1.dat")
	#	EcritureData(Results=Moyenne2, FilePath="tab2.dat")
		return float(Sum)/len(DataList)
		
	
	
	
	

