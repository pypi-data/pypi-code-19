
#import myhdl
import logging, os, sys, inspect
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from Utilities import Misc

#=========================================================
class SkipLines():
	#------------------------------------------------
	def __init__(self, TestLineNb, RefIndentLevel, SkipSlice, SourceLines):
		"""
		Return an SkipLines object for the else block of current frame test.
		This function must be called from a if/elif test 
		"""
		self.TestLineNb=TestLineNb
#		print("SkipSlice:",SkipSlice)
#		print("TestLineNb:", self.TestLineNb)
		self.RefIndentLevel=RefIndentLevel
		self.SkipSlice=SkipSlice
		self.SourceLines = SourceLines
#		print("self.SourceLines:", self.SourceLines)
	#------------------------------------------------
	def ShowLines(self):
		"""
		Print skipping lines to stdout.
		"""
		print("-------------------")
		print("Lines to skip:")
		for L in self.SourceLines:
			print(L)
		print("-------------------")
		return None
	#------------------------------------------------
	def SkipCurrent(self):
		"""
		Test if current calling line has to be skipped.
		"""
		CurFrame = inspect.currentframe()
		CallingFrames = inspect.getouterframes(CurFrame, 2)
		LineNb  = CallingFrames[2][2]
#		print(CallingFrames[2])
#		self.ShowLines()
#		print("self.TestLineNb:", self.TestLineNb)
#		print("self.SkipSlice", self.SkipSlice)
#		print("Skipping lines: [{0}:{1}[".format(self.TestLineNb+self.SkipSlice.start, self.TestLineNb+self.SkipSlice.stop))
		if LineNb>=self.SkipSlice.start and LineNb<(self.SkipSlice.stop):
#			print("Skip line", LineNb)
			return True
#		print("Do not skip line", LineNb)
		return False
	#------------------------------------------------
	def GetLines(self):
		"""
		return Lines ready to be executed.
		"""
		return [L.replace('\t'*(self.RefIndentLevel+1), '') for L in self.SourceLines if not L.isspace()] # TODO : manage space instead of tabulations
	#------------------------------------------------
	def __repr__(self):
		"""
		return self representing string
		"""
		return "SkipLines(FuncStatLineNb={0}, TestLineNb={1}, RefIndentLevel={2}, SourceLines={3})".format(repr(self.FuncStatLineNb), repr(self.SkipSlice.start), repr(self.RefIndentLevel), repr(self.SourceLines))
	
#=========================================================
class SkipReturn():
	#------------------------------------------------
	def __init__(self, LineNb, RefIndentLevel, Expression, MergedReturn):
		"""
		Return an SkipLines object for the else block of current frame test.
		This function must be called from a if/elif test 
		"""
		self.LineNb=LineNb
#		print("LineNb:",LineNb)
		self.RefIndentLevel=RefIndentLevel
		self.Expression = Expression
		self.MergedReturn=MergedReturn
	#------------------------------------------------
	def ShowExpression(self):
		"""
		Print skipping returned expression to stdout.
		"""
		print("Return expression:", self.Expression)
		return None
	#------------------------------------------------
	def SkipCurrent(self):
		"""
		Test if current calling line is a return statement to be skipped.
		"""
		CurFrame = inspect.currentframe()
		CallingFrames = inspect.getouterframes(CurFrame, 2)
		LineNb  = CallingFrames[2][2]
#		print(CallingFrames[2])
#		self.ShowLines()
#		print("self.TestLineNb:", self.TestLineNb)
#		print("self.SkipSlice", self.SkipSlice)
#		print("Skipping lines: [{0}:{1}[".format(self.TestLineNb+self.SkipSlice.start, self.TestLineNb+self.SkipSlice.stop))
		if LineNb==self.LineNb:
#			print("Skip line", LineNb)
			return True
#		print("Do not skip line", LineNb)
		return False
	#------------------------------------------------
	def __repr__(self):
		"""
		return self representing string
		"""
		return "SkipReturn(LineNb={0}, RefIndentLevel={1}, Expression={2}, MergedReturn={3})".format(repr(self.LineNb), repr(self.RefIndentLevel), repr(self.Expression), repr(self.MergedReturn))
	
	
	
	
	
	
	
