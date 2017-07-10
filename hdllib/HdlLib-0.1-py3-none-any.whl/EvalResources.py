#!/usr/bin/python


import sys, os, logging, re, math

from HdlLib.Utilities.ErrorHandlers import ToolError, ExecError
from HdlLib.SysGen.Module import Module
from HdlLib.SysGen.Signal import Signal

#======================================================================
class ResourceUsage:
	#------------------------------------------------------------------------------
	def __init__(self):
		"""
		Initialize resource dictionary
		"""
		self.ResourceDict={}
	#------------------------------------------------------------------------------
	def Eval(self, Mod): 
		"""
		Execute logic synthesis of a given module and return resource usage object.
		"""
		return self.ResourceDict























