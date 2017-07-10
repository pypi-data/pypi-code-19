#!/usr/bin/python3

import os, sys, logging

#======================================================================
class Constraints:
	#----------
	def __init__(self, Throughput, HwModel, AddCommunication=False):
		"""
		Setup parameters Throughput and HwModel.
		"""
		self.Throughput=Throughput
		self.HwModel=HwModel
		self.AddCommunication=AddCommunication
	#----------
	def GetCommunicationService(self, ServDict):
		"""
		Return a communication service that is supported by the Hw model.
		"""
		if self.AddCommunication is True:
			for SName, S in ServDict.items():
				if S.IsCommunication is True:
#					input("Found communication module '{0}'".format(S))
					return S
			logging.error("Cannot find any communication module that satisfies these constraints '{0}'.".format(self))
			return None
		else:
			ServName="SimuCom"
			for SName, S in ServDict.items():
				if SName==ServName:
					return S
			logging.error("Cannot find the 'SimuCom' service in library.")
			return None
	#----------
	def SatisfiedFor(self, Module):
		"""
		return True if Module satisfy Hw and throughput constraints.
		"""
		if self.HwModel is None:
			logging.error("[pyInterCo.Constraints.Constraints.Satisfy] No HwModel specified for constraint checking.")
			return False
			
#		print("Module:", Module)
#		print("self.HwModel.GetFPGA():", self.HwModel.GetFPGA(FullId=False))
#		print("Resources:", Module.Resources)
#		print("CompatibleFPGAs:", Module.CompatibleFPGAs())
#		print("HwModel's FPGA in CompatibleFPGAs:", self.HwModel.GetFPGA(FullId=False) in Module.CompatibleFPGAs())
#		input()
		FPGA=self.HwModel.GetFPGA(FullId=False)
		if not (FPGA in Module.CompatibleFPGAs()):
			if "ALL" in Module.CompatibleFPGAs(): 
				FPGA="ALL"
			else:
				return False
		if self.Throughput is None:
			return True
		else:
			print("MaxFreq of module:", Module.MaxFreq)
			F=Module.GetMaxFreq(FPGA=FPGA)
			DII=Module.GetDataIntroductionInterval()
			print("Freq is", F)
			print("DII is", DII)
			print("Throughput is", F*DII)
			input()
			if F*DII < self.Throughput:
				return False
			
			return True
	#---------------------------------------------------------------
	def Copy(self):
		"""
		Return object with same attributes.
		"""
		Copy=Constraints(
				Throughput=self.Throughput, 
				HwModel=self.HwModel
				)
		return Copy
	#----------------------------------------------------------------------
	def __repr__(self):
		"""
		Return string representation.
		"""
		return "pyInterCo.Constraints(Throughput={Throughput}, HwModel={HwModel}, AddCommunication={AddCommunication})".format(Throughput=repr(self.Throughput), HwModel=repr(self.HwModel), AddCommunication=repr(self.AddCommunication) )
	#----------------------------------------------------------------------
	def __str__(self):
		"""
		Return string representation.
		"""
		return str(self.HwModel)

















		
