
import logging, os, sys
import networkx as nx

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))
from SyntheSys.Analysis import Operation
from SyntheSys.Synthesis.Graphs import AppCharGraph
from SysGen.HW.HwResources import HwResources
from SyntheSys.YANGO import NoCMapping
from Utilities.Misc import SyntheSysError


	
#====================================================================
def AllocExceedRsc(FPGAModel, Task, Module, CurrentSched, TaskGraph):
	"""
	return True if the allocation of module for task make the global 
	resources higher than FPGA available ones.
	"""
#	UsedRsc=EstimateRscUsage(FPGAModel, list(CurrentSched.keys()))
	
	NewSched=CurrentSched.copy() # Potential New Scheduling
#	print("NewSched:", '\n'.join([str(k)+":"+str([str(i) for i in v]) for k,v in NewSched.items()]))
	NewSched[Module]=[Task,]
	APCG=AppCharGraph.ScheduleToAPCG(NewSched, TaskGraph=TaskGraph) # Potential APCG
	NewRscUsage, NoCParams=EstimateRscUsage(FPGAModel, list(NewSched.keys()), APCG)#UsedRsc+EstimateRscUsage(FPGAModel, [Module,])
	return not (NewRscUsage < FPGAModel.AvailableResources()), NewRscUsage

#====================================================================
def EstimateRscUsage(FPGAModel, ModList, APCG):
	"""
	return Rsc object for total used resources.
	"""
	FPGAName = FPGAModel.GetFPGA(FullId=False)
	UsedRsc  = HwResources(FPGAModel=FPGAModel)
	
	TaskManager=Operation.LibServices["TaskManager"].GetModule()
	NetworkAdapter=Operation.LibServices["NetworkAdapter"].GetModule()
	FIFO=Operation.LibServices["FIFO"].GetModule()
	for Mod in ModList:
		R=Mod.GetUsedResources(FPGAName)
		if R is None: logging.error("Unable to estimate resources on '{0}' for module '{1}'.".format(FPGAName, Mod.Name));sys.exit(1)
		UsedRsc+=R
		# Consider Adapters's resources
		R=TaskManager.GetUsedResources(FPGAName)
		if R is None: logging.error("Unable to estimate resources on '{0}' for TaskManager.".format(FPGAName));sys.exit(1)
		UsedRsc+=R
		R=NetworkAdapter.GetUsedResources(FPGAName)
		if R is None: logging.error("Unable to estimate resources on '{0}' for NetworkAdapter.".format(FPGAName));sys.exit(1)
		UsedRsc+=R
		R=FIFO.GetUsedResources(FPGAName)
		if R is None: logging.error("Unable to estimate resources on '{0}' for NetworkAdapter.".format(FPGAName));sys.exit(1)
		UsedRsc+=R
	# Add NoC ressources (Use NoC model)
	if len(ModList)>1:
		NoC=Operation.LibServices["NoC"].GetModule()
#		UsedRsc+=NoC.GetUsedResources(FPGAName)
		try: NoCRsc, NoCParams = GetResourcesFromModel(NoC, FPGAModel, APCG) 
		except SyntheSysError as E: 
			logging.error("Unable to estimate resources on '{0}' for the NoC. {1}".format(FPGAName, E.Message));sys.exit(1)
		UsedRsc+=NoCRsc
	else:
		NoCParams={}
	return UsedRsc, NoCParams
	
#====================================================================
def GetResourcesFromModel(NoCMod, FPGAModel, APCG):
	"""
	Estimate resource usage from mathematical models.
	"""
	import string

	OtherParameters, M=NoCMapping.SetNoCParam(APCG)
	ModList=[N.GetModule() for N in APCG.nodes() if not (N is None)]
	FlitWidth=NoCMapping.SetupFlitWidth(ModuleList=ModList) # TODO : Use it
	DimX, DimY = M.Size()
	NoCParameters={"DimX":DimX,"DimY":DimY, "FlitWidth":FlitWidth}

	Models={"LUT":"2003.916*DimX*DimY+2913.355", "REGISTER":"802.626*DimX*DimY+1026.595", "RAM":"5.000*DimX*DimY-20.000"}

	RscDict={}
	for Type, Expression in Models.items():
		RscDict[Type]=(int(eval(Expression, NoCParameters.copy())), -1, -1)
	
	NoCResources = HwResources(RscDict=RscDict, FPGAModel=FPGAModel)
#	logging.debug("NoC resources usage: {0}".format(NoCResources))
#	input()
	return NoCResources, NoCParameters
	









