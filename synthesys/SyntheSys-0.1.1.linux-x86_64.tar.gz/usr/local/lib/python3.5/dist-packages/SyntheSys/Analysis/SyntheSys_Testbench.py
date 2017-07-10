import logging


from SyntheSys.Analysis.Module import HighLevelModule
from SyntheSys.Analysis.Tracer import Tracer
from SyntheSys.Analysis.Data import Data

TestedModule=None
#========================================
def SyntheSys_Testbench():
	"""
	Used for generation of Stimuli and Golden traces.
	Expect to receive nothing.
	"""
	def Decorator(TBFunction):
		"""
		Decorator for testbench definition.
		usage:
			@Testbench
			def Function():
				...
				return x
		Must return modified function.
		"""
		def NewTBFunction(*args, **kwargs):
			"""
			Modified function.
			"""
			if len(args)>0: 
				Mod=args[0]
				if isinstance(Mod, HighLevelModule):
					logging.debug("Execute '{0}' as testbench. Record data values.".format(TBFunction.__name__))
				
					HighLevelModule.DATAFLOW_TRACKING=True
		#			Data.BRANCH_BROWSING=False
					global TestedModule
					TestedModule=Mod
					Result = TBFunction(*args[1:], **kwargs)
					return Result
					
#			logging.error("[NewTBFunction] No arguments given.")
			return TBFunction()
			
		# First Add the AlgoFunction to class attribute with expected types
		NewTBFunction.IsTB=True
		return NewTBFunction 
	return Decorator
    

#===========================================================================
def GenStimDict(Mod):
	"""
	Return dict with Module:ArgValuesDict pairs
	"""
	#-----------------------------
	# Generate stim
	HighLevelModule.DATAFLOW_TRACKING=True
#	Mod.BRANCH_BROWSING=False
	HighLevelModule.RECORD_VALUES=True
	HighLevelModule.NO_WRAPPING=False
#	raw_input("[ExtractDataValues] Mod.RECORD_VALUES is {0}".format(Mod.RECORD_VALUES))
#	RetSig = Mod._Algorithm(*Args, **Kwargs) # Resets Mod._Algorithm.DATAFLOW_TRACKING
#	print("Mod:", Mod)
#	print("Mod._Testbench:", Mod._Testbench)
	Mod._Testbench(Mod)
	#-----------------------------
	
	TaskStimDict={}
	for ArgName, ArgData in Mod.ArgDict.items():
#		print("ArgName:", ArgName)
#		print("ArgData:", ArgData)
		for D, OpList in ArgData.GetConsumers(IncludeControl=True):
#			print("D:", D)
			for Op in OpList:
#				print("   Op:", Op)
				for Idx, I in enumerate(Op.GetInputs(TestedData=False)):
#					print("   I:", I)
#					print(I.NodeID(), "=> Index:",Idx)
#					print("I.GetTBValues():", I.GetTBValues())
					if not Op in TaskStimDict: TaskStimDict[Op]={}
					TaskStimDict[Op][Idx]=(I.Name, I.GetTBValues()[:])
#					print("      Values:",TaskStimDict[Op][Idx])
#	input()
	TaskConstStimDict={}
	for ConstData in Tracer.Constants:
#		print("ConstData:", ConstData)
		if ConstData.NodeID() in Mod.ArgDict: continue
		elif ConstData.NodeID() == "DUMMY": continue
#		print("ConstName:", ConstData.NodeID())
#		print("ConstData:", repr(ConstData))
		for D, OpList in ConstData.GetConsumers():
#			print("D:", D)
#			print("OpList:", OpList)
			for Op in OpList:
#				print("   Op:", Op)
#				print("Op:", Op._Name)
				for Index, I in enumerate(Op.GetInputs()):
#					print("I:", I.NodeID())
#					print("Index:", Index)
					if I is ConstData:
#						print(ConstData.NodeID(), "=> Index:",Index)
						try: TaskConstStimDict[Op][Index]=(ConstData.NodeID(),[ConstData.SyntheSys__PythonVar,])
						except: TaskConstStimDict[Op]={Index:(ConstData.NodeID(),[ConstData.SyntheSys__PythonVar,])}
#				print("Operation:", repr(Op))
#				print(">>>inputs:", Op.GetInputs())
#				for I in Op.GetInputs():
#					print("  > Input:", I)
#					if not Op in TaskConstStimDict: TaskConstStimDict[Op]={}
#					TaskConstStimDict[Op][I.Name]=I.GetTBValues()[:]
#		input()
#	print("TaskConstStimDict:", TaskConstStimDict)
#	input()
	HighLevelModule.NO_WRAPPING=True
	
	return TaskStimDict, TaskConstStimDict
	
	
	
	
	
	
	
	
	
