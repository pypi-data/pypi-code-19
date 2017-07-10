#! /usr/bin/python
"""
Select operations
"""
import logging, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import SyntheSys.SysGen
from SyntheSys.Analysis.Operation import Operation

#=========================================================
class SelectOperation(Operation):
	Instances=[]
	Dummies=[]
	""" 
	Abstraction of select Operations.
	Object for synchronous data flow representation/simulation.
	"""		
	#-------------------------------------------------
	def __init__(self, TestedData=None, InputList=[], ExtraArg={}, AlgoFunction=None, SelectG=None):
		"""
		Initialization of the Operation attributes.
		"""
		super().__init__(Name="SELECT", InputList=InputList, ExtraArg=ExtraArg, AlgoFunction=AlgoFunction)
		self.TestedData = TestedData
		self.Select={}
		self.SelectGroup=SelectG
		self.SelectGroup.AddSelect(self)
		SelectOperation.Instances.append(self)
	#-------------------------------------------------
	def IsSelect(self):
		return True
	#-------------------------------------------------
	def IsSwitch(self):
		return False
	#-------------------------------------------------
	def GetSelectOutput(self):
		"""
		Return first data output if present, else instantiate a new data from input data format.
		"""
		if self.Outputs:
			return self.Outputs[0]
		else:
			N=self.NodeID()
			SelectOutput=self.Inputs[0].GetCopy(NewName=N, Op=self, PythonVar=None)
			self.Outputs.append(SelectOutput)
			return SelectOutput
	#-------------------------------------------------
	def AddToSelect(self, OtherTracer, SelectValue):
		"""
		Add OtherTracer as operator input at SelectValue.
		OtherTracer must be a Data instance.
		"""
		for I in self.Inputs:
			if I is OtherTracer: 
				logging.error("{0} already in the select.".format(I))
				raise TypeError
				return False
				
		if SelectValue in self.Select:
#			print("[AddToSelect] OtherTracer:", OtherTracer)
#			print("[AddToSelect] SelectValue:", SelectValue, "in", self.Select, ":", SelectValue in self.Select)
#			print("[AddToSelect] self.Select[SelectValue].SyntheSys__Producer:", self.Select[SelectValue].SyntheSys__Producer)
#			input()
			if not self.Select[SelectValue].SyntheSys__Producer.IsSelect(): 
				# Add a new select operation With True input as OtherTracer
				SelectOp=SelectOperation(TestedData=self.TestedData, InputList=list(), SelectG=self.SelectGroup)
				SelectOp.AddToSelect(self.Select[SelectValue], True)#self.SyntheSys__Producer.GetSelectOutput().LastAssignment()
				SelectOp.AddToSelect(OtherTracer, False)#self.SyntheSys__Producer.GetSelectOutput().LastAssignment()
				O=SelectOp.GetSelectOutput().LastAssignment()
				self.Select[SelectValue]=O
				# TODO : Check non regression
			else:
#				raise TypeError("Operator producing of '{0}' is not a select operation".format(self.Select[SelectValue]))
				self.Select[SelectValue].SyntheSys__Producer.AddToSelect(OtherTracer, SelectValue)
		else:
			self.Inputs.append(OtherTracer)
			self.Select[SelectValue]=OtherTracer
			if self in OtherTracer.SyntheSys__Children:
				OtherTracer.SyntheSys__Children[self].append(self.GetSelectOutput())
			else:
				OtherTracer.SyntheSys__Children[self]=[self.GetSelectOutput(),]
	#		print("New select:", repr(self))
		return True
	#-------------------------------------------------
	def IsMerging(self, NodeID):
		"""
		return True if specified ID match one of its inputs.
		"""
#		print("[IsMerging] NodeID:", NodeID)
		for I in self.Inputs:
			if I.NodeID()==NodeID:
				return True
		return False
	#-------------------------------------------------
	def SubstituteBySelected(self):
		"""
		Remove selected link from output consumers's output parents
		"""
#		print("Select node:", self)
		for TestedData in self.Outputs.values():
#			print("Selected's output:",Selected)
#			print("Selected's output children:", Selected.SyntheSys__Children)
			for O in Selected.GetConsumers(OutputData=True):
#				print("    > Consumer's output:",O)
				Substitutes=[]
				for Parent in O._Parents:
					if Parent is self.InputData:
						Idx=O._Parents.index(Parent)
						Substitutes.append( (Parent, Idx) )
#				print("    >> :", Substitutes)
				for Parent, Idx in Substitutes:
					O._Parents.remove(Parent)
					O._Parents.insert(self.InputData, Idx)
#		input()
		return True
	#-------------------------------------------------
	def NodeID(self, ShowID=True):
		"""
		return string representation.
		"""
		return "SELECT_"+str(Operation.Instances.index(self))
	#-------------------------------------------------
	def Order(self):
		"""
		return higher index of input's producers.
		"""
		return max([Operation.Instances.index(I.SyntheSys__Producer) for I in self.Inputs])
		
			
		
		
		
		
		
		
		
		
		
		
