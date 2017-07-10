#! /usr/bin/python

"""

"""
import logging

#=========================================================
class BranchNode:
	""" 
	Abstraction of CDFG branch node.
	"""		
	#-------------------------------------------------
	def __init__(self, Name, Input):
		"""
		Initialization of the Data attributes.
		"""
		self.__name__    = Name
		
		self.Input       = Input
		self.OutputTrue  = None
		self.OutputFalse = None
		
	#-------------------------------------------------
	def SetOutput(self, DataItem, CondTrue=True):
		"""
		Return label for True condition.
		"""
		if CondTrue is True: OutputTrue=DataItem
		else: OutputFalse=DataItem
		
	#-------------------------------------------------
	def Label(self, TargetData):
		"""
		Return label for True/False condition.
		"""
		if TargetData is self.OutputTrue:
			return "{0}==0".format(self.Input.LastAssignment())
		else:
			return "{0}!=0".format(self.Input.LastAssignment())
		
	#-------------------------------------------------
	def __str__(self):
		"""
		Return branch name.
		"""
		return "{0}({1})".format(self.__name__, self.Input.LastAssignment())
		
		
		
		
		
		
		
