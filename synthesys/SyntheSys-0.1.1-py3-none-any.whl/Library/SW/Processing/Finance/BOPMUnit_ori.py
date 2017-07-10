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
			('d',1),
			('spots_p',1),
			('rinv',1),
			('Stim2', 1), #Stim1__call[k]
			('Stim1', 1), #Stim2__call[k-1]

			('Stim2_2', 1), #Stim1__put[k]
			('Stim1_1', 1), #Stim2__put[k-1]
			('strike',1),
			('p',1),
			('q',1),
			])
		Outputs=collections.OrderedDict([
			#('Trace', 1), 
			('values_call_new',1),
			('values_put_new',1),
			('spots_p',1),
			])
		Imp.SetInterface(Inputs=Inputs, Outputs=Outputs)
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def GetPrice(self, d,spots_p,rinv,Stim2,Stim1,Stim2_2,Stim1_1,strike,p,q):
		spots_p = d * spots_p
		a= rinv * (p * Stim2 + q * Stim1)
		b= spots_p-strike
		if b>0: c = b
		else: c = 0.0
		if a>c: temp_call_new = a
		else: temp_call_new = c
	
		d= rinv * (p * Stim2_2 + q * Stim1_1)
		e= strike-spots_p
		if e>0: f = e
		else: f = 0.0
		if d>f: temp_put_new = d
		else: temp_put_new = f
	
		if temp_call_new > 0.0: values_call_new = temp_call_new
		else: values_call_new = 0.0
	
		if temp_put_new > 0.0: values_put_new = temp_put_new
		else: values_put_new = 0.0
	
		return values_call_new, values_put_new, spots_p		
		
##======================================================================
#def BOPMUnit(*Args, **ArgDict):
#	"""
#	Wrapper for transparent library usage.
#	"""
#	return BB_BOPMUnit(*Args, **ArgDict)
	
	
	
	

