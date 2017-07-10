#!/usr/bin/python

import sys, os
from AccelLibrary import PYHLS_PATH

sys.path.append(PYHLS_PATH)

from pyhls.Design.Module import HighLevelModule, Synthesizable
from pyhls.Design.Algorithm import Algorithm
#from pyhls.Design.Testbench import Testbench

#======================================================================
@Synthesizable
class __BASICBLOCK____sub__(HighLevelModule):
	"""
	Basic subtactor tile.
	"""
	#--------------------------------------------------------------------
	def __init__(self): # HighLevelModule Parameters
		"""
		Initialization of the DoubleLoop HighLevelModule.
		"""
		HighLevelModule.__init__(self) # essential for being considered as HighLevelModule and inherit of basic HighLevelModule functions/attributes
		Imp=self.SetService(ServiceName="Subtractor")
		Imp.SetInterface(Inputs={'A':1, 'B':1}, Outputs={'R':1}, InOuts={})
		self._TargetHW='All'
	#--------------------------------------------------------------------
	@Algorithm() # Mean that this method will be HighLevelModule algorithm to be synthesized.
	def Sum(self, A, B):
		"""
		return A-B.
		"""
		return A-B
		
	
	
	
	

