
import sys, os, re
import logging

#======================================================
# Generic HdlLib error handlers
class HdlLibError(Exception):
	def __init__(self, Message="HdlLib error"):
		self.Message = Message
	def __str__(self):
		return repr(self.Message)
		
#======================================================
# HdlLib Parse error handlers
class ParseError(HdlLibError):
	def __init__(self, Message="HdlLib error"):
		self.Message = Message
		logging.error(Message)
	def __str__(self):
		return repr(self.Message)

				
				
