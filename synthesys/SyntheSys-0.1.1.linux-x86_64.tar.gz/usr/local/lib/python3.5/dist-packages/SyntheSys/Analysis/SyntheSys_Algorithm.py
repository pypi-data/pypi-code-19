
import logging, sys
import inspect
from SyntheSys.Analysis.Data import Data
from SyntheSys.Analysis.Tracer import Tracer, ResetTracer
from SyntheSys.Analysis.Operation import ResetOperations, Operation
from SyntheSys.Analysis.Module import HighLevelModule
from SyntheSys.Analysis import SyntheSys_Testbench
from SyntheSys.Analysis import Select, Reduce

#========================================
def SyntheSys_Algorithm(*TypesList, **TypesDict):
	"""
	Expect to receive wanted types from decorator.
	Accepts undefinite number of parameters. Each of them must be checked.
	"""
	def Decorator(AlgoFunction):
		"""
		Decorator for input Data definition.
		usage:
			@Input(int, float, str)
			def Function(a, b, c):
				...
				return x
		Must return modified function.
		"""
		#------------------------------------------------
		def NewAlgoFunction(*args, **kwargs):
			"""
			Modified function.
			"""
			if HighLevelModule.NO_WRAPPING==True:
				return AlgoFunction(*args, **kwargs)
#			print("AlgoFunction:", AlgoFunction)
			#---------------------------------------------------------------------------
			if args:
				Mod=args[0]
				if not isinstance(Mod, HighLevelModule):
					if not "SyntheSys_HighLevelModule" in kwargs:
						if SyntheSys_Testbench.TestedModule is None:
#							logging.error("No HighLevelModule specified during algorithm call.")
#							sys.exit(1)
							logging.info("Normal call for algorithm function.")
							return AlgoFunction(*args, **kwargs)
						Mod=SyntheSys_Testbench.TestedModule
					else:
						Mod=kwargs.pop("SyntheSys_HighLevelModule")
			else:
				if not "SyntheSys_HighLevelModule" in kwargs:
					if SyntheSys_Testbench.TestedModule is None:
						logging.error("No HighLevelModule specified during algorithm call.")
						sys.exit(1)
#						logging.info("Normal call for algorithm function.")
#						return AlgoFunction(*args, **kwargs)
					Mod=SyntheSys_Testbench.TestedModule
				else:
					Mod=kwargs.pop("SyntheSys_HighLevelModule")
			
			#----------------Get TB values-----------------
			if HighLevelModule.RECORD_VALUES is True:
				ArgNames=inspect.getargspec(AlgoFunction)[0]
				ArgDict=GetArgDict(ArgNames=ArgNames, Args=args, Kwargs=kwargs)
				if Mod.IsBlackBox():
					for ArgName, ArgDefaultValue in Mod.Implementation.Inputs.items():
						if ArgName in ArgDict: continue
						ArgDict[ArgName]=ArgDefaultValue
#					print("ArgNames:", ArgNames)
#					print("ArgDict:", ArgDict)
#					print("Mod:", Mod)
#					print("Mod.Implementation.Inputs:", Mod.Implementation.Inputs)
#					input()
				if not Mod.SetTBValues(ArgDict):
					logging.error("[SyntheSys_Algorithm] Unable to set TB values for module '{0}'".format(Mod.GetName()))
					sys.exit(1)
#				print("Algo:", AlgoFunction.__name__)
#				print("args:", args)
#				print("kwargs:", kwargs)
				return AlgoFunction(*args, **kwargs)

			#----------------------------------------------
			if Mod.IsBlackBox(): 
#				print("===> BlackBox !")
				args=list(args)
				for i in range(len(args)):
					if i==0: continue
					Argument=args[i]
					if not isinstance(Argument, Tracer):
						if isinstance(Argument, list) or isinstance(Argument, tuple):
							args[i]=ReducedData(Argument)
				for k in kwargs:
					Argument=kwargs[k]
					if not isinstance(Argument, Tracer):
						if isinstance(Argument, list) or isinstance(Argument, tuple):
							kwargs[k]=ReducedData(Argument)
#							kwargs[k]=Data(
#								   Name="Reduced", 
#								   Operation=Reduce.Reduce(InputList=kwargs[k]), 
#								   PythonVar=[kwargs[k][j].SyntheSys__PythonVar for j in range(len(kwargs[k]))],
#								   Parents=kwargs[k])
							
#				for a in args[1:]+tuple(kwargs.values()):
#					if not isinstance(a, Tracer):
#						print("a:", a)
#						return AlgoFunction(*args, **kwargs)
				args=tuple(args)
				return Mod.BlackBoxFunction(*args, **kwargs) # TODO: set HW
				
			#---------------trace data flow----------------
			if HighLevelModule.DATAFLOW_TRACKING is True:
				#----------------------
				logging.debug("Clear lists of Tracer an Operations")
				ResetTracer()
				ResetOperations()
				#-------Arguments Tracer analysis------------
				logging.debug("Modifying algorithm function to take data tracker instead of expected arguments.")
				# Modifying algorithm function to take Datas instead of expected arguments.
				ArgNames=inspect.getargspec(AlgoFunction)[0]
				logging.debug("Arguments: {0}".format(ArgNames))
#				print("args:", args)
#				print("kwargs:", kwargs)
#				print("Mod.ArgDict:", Mod.ArgDict)
#				input()
				args, kwargs=GenDatas(Args=args[1:], ArgNames=ArgNames,  Kwargs=kwargs)
				Mod.ArgDict = kwargs.copy()
				for ArgName,Sig in zip(ArgNames, args):
					Mod.ArgDict[ArgName]=Sig
	#				Mod.ArgList = list(args)
				#----------------------
#				Mod.InternalDict = {}
#				for k,v in vars(Mod).iteritems():
#					if k not in vars(HighLevelModule()):
#						Mod.InternalDict[k]=v
#				for Name, Var in Mod.InternalDict.iteritems():
#					setattr(Mod, Name, Data(PythonVar=Var, Name=Name))
				#----------------------
#				args.insert(0, Mod)
				#------------------------------------------
				logging.debug("Execute '{0}' as HighLevelModule. Inputs are considered as Data objects.".format(AlgoFunction.__name__))
			else:
				logging.debug("Execute {0}'s '{1}' as python function (not HighLevelModule).".format(Mod, AlgoFunction.__name__))
			#----------------
			HighLevelModule.DATAFLOW_TRACKING=False # Used only for top instances
			#----------------
			
			# TODO: Restore internal attributes
			
			Mod.AlgoName=AlgoFunction.__name__
			RetVal = AlgoFunction(*args, **kwargs)
			# Substitute selected by select outputs
#			for S in Select.SelectOperation.Instances:
#				S.SubstituteBySelected()
			def GetRetList(RetVal):
				RetList=[]
				if isinstance(RetVal, tuple) or isinstance(RetVal, list):
					for R in RetVal:
						RetList+=GetRetList(R)
				elif isinstance(RetVal, Data):
					RetVal.SetAsInterface()
					RetList.append(RetVal)
				return RetList
				
			Mod.ReturnList=GetRetList(RetVal)
			
			return RetVal
		# First Add the AlgoFunction to class attribute with expected types
		NewAlgoFunction.IsAlgo=True
#		NewAlgoFunction.TypesList=TypesList
#		NewAlgoFunction.TypesDict=TypesDict
		return NewAlgoFunction 
	return Decorator

#================================================
def ReducedData(Argument):
	"""
	return reduced tracer from argument list.
	"""
	for i,A in enumerate(Reduce.Reduce.ReducedInputs):
		if A is Argument:
			return Reduce.Reduce.ReducedList[i]
			
	if len(Argument)>0:
		ReduceInputs=[]
		Constants=[]
		for item in Argument:
			if isinstance(item, Tracer):
				if len(Constants)>0:
					ReduceInputs.append(
						Data(
						   Name="ReducedConst", 
						   Operation=None, 
						   PythonVar=Constants,
						   Parents=[]))
					Constants=[]
				ReduceInputs.append(item)
			else:
				Constants.append(item)
				
		if len(Constants)>0:
			ReduceInputs.append(
				Data(
				   Name="ReducedConst", 
				   Operation=None, 
				   PythonVar=Constants,
				   Parents=[]))
		
		if len(ReduceInputs)==1:
			return ReduceInputs[0]
		else:
			ReducedData=Data(
				   Name="Reduced", 
				   Operation=Reduce.Reduce(InputList=ReduceInputs), 
				   PythonVar=[ReduceInputs[j].SyntheSys__PythonVar for j in range(len(ReduceInputs))],
				   Parents=ReduceInputs)
			Reduce.Reduce.ReducedInputs.append(Argument)
			Reduce.Reduce.ReducedList.append(ReducedData)
			return ReducedData
	else:
		logging.error("Empty list given to module '{0}'".format(Mod))
		raise SyntheSysError
		
		
#================================================
def CheckType(Param, Type, Pos, FunctionName):
	"""
	Check if type of param is Type.
	Raise an error if not.
	"""
	if isinstance(Param, Sig.Data):
		return True
	elif isinstance(Type, list):
		# First check if Param is a list	
		if not isinstance(Param, list):
			raise TypeError("Argument #{0}({1}) of function '{2}' has wrong type '{3}', expected a list.".format(Pos, repr(Param), FunctionName, type(Param)))
		for i, SubType in enumerate(Type):
			CheckType(Param[i], SubType, '{0}:{1}'.format(Pos, i), FunctionName)
	else:
		if Type != type(Param):
			raise TypeError("Argument #{0}({1}) of function '{2}' has wrong type '{3}', expected {4}".format(Pos, repr(Param), FunctionName, type(Param), Type))

	return True
	
#===========================================================================
def GenDatas(Args=[], ArgNames=[], Kwargs={}):
	"""
	Convert class arguments to Data instances arguments.
	"""		
	logging.debug("Change variables to Datas.")
#	if len(ArgNames)!=len(Args):
#		logging.error("Arguments number ({0}) is no the same as the number of argument names ({1}).".format(len(ArgNames), len(Args)))
#		return [], {}
	# If arguments are Datas : copy them
	args = [Data(PythonVar=Arg, Name=ArgNames[i+1], IsInterface=True) for i, Arg in enumerate(Args)]
	kwargs = {}
	for Name, Arg in list(Kwargs.items()):
		kwargs[Name]=Data(PythonVar=Arg, Name=Name, IsInterface=True) 
	return args, kwargs
	
#===========================================================================
def GetArgDict(ArgNames, Args, Kwargs):
	"""
	Associate each object to argument name.
	"""
	ArgDict={}
	
	for i, Arg in enumerate(Args):
		ArgDict[ArgNames[i]]=Arg
		
	for Name, Arg in list(Kwargs.items()):
		ArgDict[Name]=Arg
	
	return ArgDict
#===========================================================================
#def GenArgsFromTypes(TypesList=[], ArgNames=[], TypesDict={}):
#	"""
#	Convert class arguments to instances arguments.
#	"""
#	logging.debug("Generate {0} arguments from argument types".format(len(TypesList)+len(TypesDict)))
#	ObjectList=[]
#	for Type in TypesList:
#		if isinstance(Type, dict):
#			logging.error("Dict type as argument not supported yet.")
#		elif isinstance(Type, list):
#			ObjectList.append(GenArgsFromTypes(TypesList=Type)[0])
#		else:
#			ObjectList.append(Type())
#	ObjectDict={}
#	for Name, Type in TypesDict.iteritems():
#		if isinstance(Type, dict):
#			logging.error("Dict type as argument not supported yet.")
#		elif isinstance(Type, list):
#			ObjectDict[Name]=GenArgsFromTypes(TypesDict=Type)[1]
#		else:
#			ObjectDict[Name]=Type()
#			
#	return ObjectList, ObjectDict


	
    
    
    
    
    
    
