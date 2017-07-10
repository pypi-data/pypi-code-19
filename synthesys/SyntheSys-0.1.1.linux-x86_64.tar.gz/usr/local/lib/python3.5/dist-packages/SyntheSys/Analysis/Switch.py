#! /usr/bin/python
"""
Merge operations
"""
import logging, os, sys

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import SyntheSys.SysGen
from SyntheSys.Analysis.Operation import Operation

#=========================================================
class SwitchOperation(Operation):
	Instances=[]
	""" 
	Abstraction of SWITCH Operations.
	Object for synchronous data flow representation/simulation.
	"""		
	#-------------------------------------------------
	def __init__(self, InputData, Selector, TestGroup=None):
		"""
		Initialization of the Operation attributes.
		"""
		self._Name="SWITCH"
		super().__init__(Name=self._Name, InputList=[InputData,])
		self.InputData=InputData
#		self.Inputs=[InputData,]
		self.TestGroup=TestGroup
		self.Selector=Selector
		self.Outputs={}
		SwitchOperation.Instances.append(self)
	#-------------------------------------------------
	def IsSwitch(self):
		return True
	#-------------------------------------------------
	def SubstituteBySelected(self):
		"""
		Remove selected link from output consumers's output parents
		"""
		raise TypeError
#		print("Select node:", self)
		for Selected in self.Outputs.values():
#			print("Selected's output:",Selected)
#			print("Selected's output children:", Selected._Children)
			for SelData, ConsumerList in Selected.GetConsumers(OutputData=True):
				for ConsumerOp in ConsumerList:
#					print("# ConsumerOp:",ConsumerOp)
					for ConsOut in ConsumerOp.GetOutputs():
#						print("    > Consumer's output:",ConsOut)
						Substitutes=[]
						for Parent in ConsOut._Parents:
							if Parent is self.InputData:
								Idx=ConsOut._Parents.index(Parent)
								Substitutes.append( (Parent, Idx) )
		#				print("    >> :", Substitutes)
						for Parent, Idx in Substitutes:
							ConsOut._Parents.remove(Parent)
							ConsOut._Parents.insert(self.InputData, Idx)
#		input()
		return True
	#-------------------------------------------------
	def GetSwitched(self, Selection=True):
		"""
		Return switched data output if present, else instantiate a new data from input data format.
		"""
#		print("self.Outputs.items():", self.Outputs.items())
		if not Selection in self.Outputs: 
			N=self.NodeID()
			SwitchOutput=self.InputData.GetCopy(NewName=N+"[{0}]".format(Selection), Op=self, PythonVar=None)
			self.Outputs[Selection]=SwitchOutput
			self.InputData.AddChildren(self, SwitchOutput)
#			print("Selection:", Selection)
#			print("SwitchOutput:", SwitchOutput.__name__)
#			print("Select input", self.InputData)
#			print(">> children:", self.InputData._Children)
#			input()
			return SwitchOutput
		else: return self.Outputs[Selection]
	#-------------------------------------------------
	def GetOutputs(self):
		"""
		Return list of output data
		"""
		return self.Outputs.values()
	#-------------------------------------------------
	def GetOutputName(self, ShowID):
		"""
		Return None so the output data ID is taken from data itself (not SWITCH(DataName)).
		"""
		return None
	#-------------------------------------------------
	def NodeID(self, ShowID=True):
		"""
		return string representation.
		"""
		return "SEL"+str(Operation.Instances.index(self))
	#--------------------------------------------------------------------
#	def GetNextTasks(self):
#		"""
#		Add a list of Operations consuming output data.
#		"""
#		FollowingList = []
##		print("self.Outputs:", self.Outputs)
#		for Selection, O in self.Outputs.items():
#			if O is None: continue
##			if len(T._Children)==0: FollowingList.append(None); continue
#			for Task, CList in O._Children.items():
#				if Task.GetName()=="__setitem__":
#					FollowingList+=Task.GetNextTasks()
#				else:
#					FollowingList.append(Task)
#		return sorted(list(set(FollowingList)))
#=========================================================
def ReplaceSelector(Dummy, TestedData):
	"""
	Replace every occurence of Dummy as a selector by TestedData.
	"""
#	print("[SwitchOperation.Replace] Replace {0} by {1}".format(Dummy, TestedData))
	for S in SwitchOperation.Instances:
#		print("Selector:", S)
		if S.Selector is Dummy:
#			print("Found => replace it !")
			S.Selector=TestedData
	return
	#-------------------------------------------------
#	def Order(self):
#		"""
#		return higher index of input's producers.
#		"""
#		return max([Operation.Instances.index(I._Producer) for I in self.Inputs])
		
			
		
		
		
		
		
		
		
		
		
		
