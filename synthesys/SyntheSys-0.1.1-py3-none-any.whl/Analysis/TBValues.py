
#import myhdl
import logging, os, sys
#from Operator import Operator as Op

import SyntheSys.Utilities.Misc
	
#=========================================================
class TBValues:
	"""Object that store testbench values of a module"""
	#-------------------------------------------------
	def __init__(self):
		"""
		Initialization of the TBValues attributes.
		"""
		self._CallValues=[]
	#-------------------------------------------------
	def NewCallValues(self, Args):
		"""
		Add values to call list.
		"""
		self._CallValues.append(Args)
		return True
	#-------------------------------------------------
	def __str__(self):
		"""
		Display Call values.
		"""
		return "<TBValues: "+"\n".join(map(str, self._CallValues))+">"
	#-------------------------------------------------
	def __repr__(self):
		"""
		Display Call values.
		"""
		return "<TBValues: >"+"\n".join(map(str, self._CallValues))

		
		
		
		
		
		
		
		
		
		
		
		
		
