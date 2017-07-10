#!/usr/bin/python


__all__ = ('DataFlow', 'Module', 'SyntheSys_Testbench', 'Synthesis')

from SyntheSys.Utilities.Timer import Timer, ProcessTimer, TimeStamp
from SyntheSys.Utilities import ConsoleInterface
from SyntheSys.Utilities.Misc import SyntheSysError
ConsoleInterface.ConfigLogging(Version="1.0", ModuleName="SyntheSys")

import logging
import os, sys, datetime
import shutil
import argparse
import networkx as nx
import struct
import pickle

import SyntheSys.SysGen
from SyntheSys.SysGen.HW import HwModel, HwResources
from SyntheSys.SysGen import Verify
from SyntheSys.SysGen import Constraints

from SyntheSys.Analysis import Module
from SyntheSys.Analysis import TBValues, Operation
from SyntheSys.Analysis import SyntheSys_Testbench as Testbench
from SyntheSys.Synthesis.Graphs import DataFlowGraph, TaskGraph
from SyntheSys.Synthesis.Optimizations import RscAlloc, ResourceSharing, ResourceEstimation, FpgaDesign
	
from SyntheSys.YANGO import Tools as YangoTools
from SyntheSys.YANGO import SoCConfig


#=============================================================
def SyntheSys_Synthesize(AlgoFunc, TestBenchFunc, OutputPath="./SyntheSys_output", *Args, **Kwargs):
	for Step, StepNb, Success in Synthesize(AlgoFunc, TestBenchFunc, OutputPath=OutputPath, *Args, **Kwargs):
		if Success is True:pass
#			logging.info("[SyntheSys] Step {0}/{1} Completed.".format(Step, StepNb))
		else:
			logging.error("[SyntheSys] Step {0}/{1} Failed.".format(Step, StepNb))
			return False
		
	logging.info("Success. Exiting.")
	return True
#import pkgutil
#__all__ = ["Generate",]
#for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
#    __all__.append(module_name)
#    module = loader.find_module(module_name).load_module(module_name)
#    exec('%s = module' % module_name)
	
#===========================================================================
def Synthesize(AlgoFunc, TestBenchFunc, OutputPath="./", *Args, **Kwargs):
	"""
	Generate HDL code in Output path according to constraints.
	"""
#	InputDataNumber=len(Kwargs['Tab'])
	CmdLineArgs = ParseOptions()
	#------------------------
	Cmd=CmdLineArgs.command.lower()
	#------------------------
	
	NbSteps=8 + (1 if True in map(lambda x: x.lower() in ["ava-soft", "ava-test", "simulate", "synthesis", "ResourceEstimation"], sys.argv[1:]) else 0)

	if not CmdLineArgs.output is None:
		OutputPath=CmdLineArgs.output
	
	PreviousConfigPath=CmdLineArgs.fpgadesign
	if PreviousConfigPath is None:
		TargetHW=HwModel.HwModel(CmdLineArgs.archi)
		if not TargetHW.IsSupported():
			logging.error("Target {0} not supported. Configuration must be provided in library.".format(TargetHW.Name))
			yield (0, NbSteps, False)
		HwConstraints=Constraints.Constraints(Throughput=None, HwModel=TargetHW, AddCommunication=(Cmd in ["synthesis", "synthesize"]))
		PreviousConfig=None
	else:
#		PreviousConfig = pickle.load(open(PreviousConfigPath, "rb"))
		PreviousConfig = FpgaDesign()
		PreviousConfig.SetupFrom(PreviousConfigPath)
		PreviousConfig.ResetScheduling()
		HwConstraints=PreviousConfig.Constraints
		TargetHW=HwConstraints.HwModel
	#------------------------
	
	AppPath=os.path.abspath(OutputPath)
	AppSrcPath=os.path.join(AppPath, "src")
	AppSynthesisPath=os.path.join(AppPath, "synthesis", TargetHW.Name)
	AppSimuPath=os.path.join(AppPath, "simulation")
	AppBinPath=os.path.join(AppPath, "bin")
	
	ResultFilePath=os.path.join(AppPath, "FpgaResourcesX.txt")#_{0}.format(TimeStamp())	
	
	for P in (AppPath, AppSrcPath, AppSynthesisPath, AppSimuPath, AppBinPath):
		if not os.path.isdir(P):
			os.makedirs(P)
	#------------------------
		
	logging.info("Target board: {0}".format(TargetHW))
#		Module.HighLevelModule._TargetHW=TargetHW#Targets.pop(0)
	Step=0
	logging.info("Synthesizing algorithm '{0}'".format(AlgoFunc.__name__))

	with ProcessTimer() as T_ESL:
		#------------------------
		logging.info("Start algo analysis...")
		Step+=1	
		with ProcessTimer() as T:
			#################################################################
			SystemMod=Module.ExtractDataFlow(AlgoFunc, TestBenchFunc, *Args, **Kwargs)
			#################################################################
		logging.info('Duration of data flow analysis : {0}'.format(T.ExecTimeString()))
		yield (Step, NbSteps, True)
		#------------------------
		logging.info("Data flow extracted. Now build a Data Flow Graph...")
		Step+=1	
		with ProcessTimer() as T:
			#################################################################
			CDFG = SystemMod.UpdateCDFG()
			#################################################################
		logging.info('Duration of data flow graph building : {0}'.format(T.ExecTimeString()))
		logging.info("Generate '.png' file...")
		RetVal=(CDFG!=None)
		if len(CDFG)<1000:
			DataFlowGraph.ToPNG(CDFG, OutputPath=AppPath)
	
		yield (Step, NbSteps, RetVal)
		#------------------------
		logging.debug("Task Communication Graph building...")
		Step+=1	
		with ProcessTimer() as T:
			Operation.InitLibrary()
			#################################################################
			TG = TaskGraph.BuildTaskGraph(SystemMod)
			#################################################################
		logging.info('Duration of Task Communication Graph building : {0}'.format(T.ExecTimeString()))
		if len(TG)<1000:
			TaskGraph.ToPNG(TG, OutputPath=AppPath)
		RetVal=(TG!=None)
	#	sys.exit(1)
		yield (Step, NbSteps, RetVal)
	
		if not (PreviousConfigPath is None):
			PreviousConfig.ReloadModules(Operation.XMLLIB)
		#------------------------
		logging.info("Resources allocation and scheduling...")
		Step+=1	
		with ProcessTimer() as T:
			#################################################################
			try:
				APCG, Sched, TSMax=RscAlloc.AllocAndSchedule(
							TaskGraph=TG, 
							Constraints=HwConstraints,
							FpgaDesign=PreviousConfig
							)
			except SyntheSysError as E:
				logging.error("Unable allocate and schedule tasks.")
				yield (Step, NbSteps, False)
		if APCG is None:
			yield (Step, NbSteps, None)
		TotalRsc, NoCParams=ResourceEstimation.EstimateRscUsage(TargetHW, list(Sched.keys()), APCG)
		# TODO : use NoCParams for HDL generation
		ModDict={}
		for M in Sched.keys():
			if M.Name.startswith("AdOCNet"):NoCMod=M
			MName=str(M)
			if MName in ModDict:
				ModDict[MName]+=1
			else:
				ModDict[MName]=1
		NoCMod=Operation.LibServices["NoC"].GetModule()
		logging.info("Used modules: "+", ".join(["{0}({1})".format(N,Nb) for N,Nb in ModDict.items()]))
		logging.info("Total resources estimated: {0}".format(TotalRsc))
	#		logging.info("InputDataNumber={0}".format(InputDataNumber))
		with open(ResultFilePath, 'a+') as ResultRscFile:
			ResultRscFile.write("\n"+"-"*50)
	#			ResultRscFile.write("\nInputDataNumber={0}".format(InputDataNumber))
			ResultRscFile.write("\nNoC parameters: {NoCParameters}".format(NoCParameters=NoCParams))
			ResultRscFile.write("\nUsed modules: "+", ".join(["{0}({1})".format(N,Nb) for N,Nb in ModDict.items()]))
			ResultRscFile.write("\nPRE-SYNTHESIS ESTIMATION:")
			ResultRscFile.write("\n\tTotal resources estimated: {0}".format(TotalRsc))
		#################################################################
		
		if APCG:
			logging.debug("Number of APCG nodes: {0}".format(APCG.number_of_nodes()))
			if len(APCG)<1000:
				RscAlloc.ToPNG(APCG, OutputPath=AppPath)
		
		logging.debug("BEST SCHEDULING FOUND:\n"+"\n".join(["\t{0} => {1}".format(k,[str(Op).strip() for Op in v]) for k,v in Sched.items()]))
		logging.debug("TSMax: {0}".format(TSMax))

		logging.info('Duration of resources allocation and scheduling: {0}'.format(T.ExecTimeString()))
		RetVal=not (APCG is None)
	
		yield (Step, NbSteps, RetVal)
	
		#------------------------
		logging.info("Generate the application...")
		APP=YangoTools.NewApp(Name=SystemMod.AlgoName, Library=None)
	
		logging.debug("Extract CDFG and APCG graphs...")
		A=APP.GetAlgo()
		if A is None: 
			logging.error("Failed to add algorithm to application '{0}'".format(APP.Parameters["Common"]["Name"]))
			yield (Step, NbSteps, False)
		else: 
			A.SetCDFG(CDFG=CDFG)
	
		#------------------------	
		logging.info("Binding (APCG mapping).")
		APP.SetAPCG(APCG=APCG)
	
		with ProcessTimer() as T:
			MappingAlgo = None if len(APCG)>6 else "BranchAndBound"
			#################################################################
			try: NoCMapping, ECost, DimX, DimY, ARCG, NoCParams = APP.Binding(
										Algo=MappingAlgo, 
										FpgaDesign=PreviousConfig,
										NoCName=CmdLineArgs.noc #AdOCNet_2DMesh
										) 
			except SyntheSysError as E: 
				logging.error("Binding failure. {0}".format(E.Message))
				yield (Step, NbSteps, False)
			#################################################################
		logging.debug("NoC dimensions: {0}x{1}".format(DimX, DimY))
		logging.debug("Number of PE  : {0}".format(len(APCG)))
		logging.debug("PE mapped     : {0}".format(len(NoCMapping)))
		logging.debug("BEST MAPPING FOUND:\n"+"\n".join(["\t{0} => {1}".format(k,v) for k,v in NoCMapping.items()]))
		logging.debug("BEST COST: {0}".format(ECost))
		logging.debug('Duration of binding : {0}'.format(T.ExecTimeString()))
		Step+=1	
		if ECost==0:
			logging.error("No elements in Application characterization graph (APCG).")
		yield (Step, NbSteps, ECost!=0)
		
		if PreviousConfig is None:
			# SAVE DESIGN CONFIGURATIONS IN A FILE---------------------------------------------
#			sys.setrecursionlimit(3000)
			FD = FpgaDesign.FpgaDesign(BaseApp=SystemMod.AlgoName, DimX=DimX, DimY=DimY, NoCMapping=NoCMapping, ARCG=ARCG, NoCParams=NoCParams, Constraints=HwConstraints)
			FD.WriteFile(AppBinPath)
#			pickle.dump(FD, open(os.path.join(AppBinPath, SystemMod.AlgoName+'.soc'), "wb+"))
		else:
#			------------------------
#			 POST MAPPING SCHEDULING
			with ProcessTimer() as T:
				APCG, Sched, TSMax=RscAlloc.TaskMappingSchedule(
								TaskGraph=TG, 
								NoCMapping=NoCMapping,
								Constraints=HwConstraints, 
								)
			yield (Step, NbSteps, True)
	
	logging.info('Duration of ESL : {0}'.format(T_ESL.ExecTimeString()))
#	sys.exit(1)
	#------------------------
	###################################################################################
	# GENERATE TESTBENCH STIMULI VALUES
	###################################################################################
	
	###################################################################################
	# GENERATE SOC CONFIGURATION VALUES
	###################################################################################
	logging.info("Generation of the SoC data values and configurations.")
	
	AppStimValues, ComAddress, CommunicationService=GenerateConfData(
	                                                           APP, 
	                                                           SystemMod, 
	                                                           NoCMapping, 
	                                                           Sched, 
	                                                           SrcOutputPath=AppPath, 
	                                                           BinOutputPath=AppBinPath
	                                                           )
	
	Step+=1
	if len(AppStimValues)==0:
		logging.error("No stimuli values generation: aborted.")
		yield (Step, NbSteps, False)
	else:
		yield (Step, NbSteps, True)
	
	###################################################################################
	# Generate VHDL sources
	###################################################################################
	logging.info("Generation of HDL sources.")
	
	try:
		Success=APP.GenerateHDL(
			        AppSrcPath, 
			        TBValues=AppStimValues, 
			        TBClkCycles=CmdLineArgs.clockcycles, 
			        CommunicationService=CommunicationService, 
			        ComAddress=ComAddress,
			        HwConstraints=HwConstraints
			        )
	except SyntheSysError as E:
		logging.error("Unable to generate HDL code for specified application.")
		yield (Step, NbSteps, False)
	
#	input("HDL GENERATION FINISHED")
	Step+=1	
	yield (Step, NbSteps, Success)
	#------------------------
	AppMod=APP.GetModule()

	#------------------------
	if not APP.AddChild("Architecture", Model=TargetHW, ExtraParameters={}):
		logging.error("Unable to add hardware '{0}'.".format(TargetHW))
		yield (Step, NbSteps, False)
	
	
	############################################################################
	# OPTIONNAL COMMANDS
	############################################################################

	Step+=1	
	if Cmd=="yango" or Cmd=='gui' or Cmd=="manual":
		logging.info("========================================")
		logging.info("          Selected mode: GUI") 
		logging.info("========================================")
		YangoToolsGUI = YangoTools.NewGUI()
		YangoToolsGUI.SetApplication(APP)
		yield (Step, NbSteps, YangoToolsGUI.Start())
		
	#------------------------
	elif Cmd=="simulate" or Cmd=="simulation": 
		logging.info("========================================")
		logging.info("      Selected mode: SIMULATION") 
		logging.info("========================================")
		
		if AppStimValues is not None:
			RetVal=YangoTools.Simulate(
					APP, 
					Simulator=CmdLineArgs.simulator, 
					RemoteHost=CmdLineArgs.host, 
					ModuleList=CmdLineArgs.module, 
					InstanceList=CmdLineArgs.instance, 
					SignalDepth=CmdLineArgs.signaldepth, 
					NbCycles=CmdLineArgs.clockcycles, 
					CycleLength=CmdLineArgs.cyclelength,
					OutputPath=AppSimuPath, 
					DisplayWaveForm=True
					)
			yield (Step, NbSteps, not (RetVal is None)) 
		else:
			yield (Step, NbSteps, False) 
	#------------------------
	elif Cmd in ["synthesis", "synthesize"]:
		logging.info("========================================")
		logging.info("       Selected mode: SYNTHESIS")
		logging.info("========================================")
		# Generate binary for design 
		try: 
			
			with ProcessTimer() as T:
				ResultFilesDict=APP.Synthesize(SrcDirectory=AppSrcPath, OutputPath=AppSynthesisPath, ControlHW=None, RemoteHost=CmdLineArgs.host)
			logging.info('Duration of logic synthesis : {0}'.format(T.ExecTimeString()))
		
		except SyntheSysError as E:
			logging.error("Unable to synthesize application.")
			yield (Step, NbSteps, False)
			
		if len(ResultFilesDict)==0:
			logging.error("Synthesis failed. No bitstream generated.")
			yield (Step, NbSteps, False)
		
		if 'RouteReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['RouteReport']
		elif 'PlaceReport' in ResultFilesDict:
			RscFilePath=ResultFilesDict['PlaceReport']
		else:
			logging.error("[ModuleResources] No resources report generated. Unable to extract resources consumption.")
			yield (Step, NbSteps, False)

		ArchPath=GeneratePackageFile(Name=SystemMod.AlgoName, BinaryPath=ResultFilesDict['Binary'], AppBinPath=AppBinPath, AppPath=AppPath)
		logging.info("Package file: {0}".format(ArchPath))
		
		HWRsc=TargetHW.GetUsedResourcesDict(RscFilePath)

#		HWRsc={"LUT":(15, -1, -1), "RAM":(12, -1, -1), "REGISTER":(10, -1, -1)}
		UsedResources=HwResources.HwResources(HWRsc)
	
		AppMod=APP.GetModule()
		AppMod.UpdateResources(TargetHW.GetFPGA(FullId=False), UsedResources)
	
#		FinalRsc = AppMod.GetUsedResources(TargetHW.GetFPGA(FullId=False))
		logging.info("Total resources used: {0}".format(UsedResources))
#		logging.info("InputDataNumber={0}".format(InputDataNumber))
		logging.debug("[Recovered] Total resources used: {0}".format(UsedResources))
		with open(ResultFilePath, 'a+') as ResultRscFile:
			ResultRscFile.write("\nPOST SYNTHESIS:")
			ResultRscFile.write("\n\tTotal resources used: {0}".format(UsedResources))
		
		yield (Step, NbSteps, True)
	#------------------------
	elif Cmd in ["rsc", "resources"]:
		logging.info("========================================")
		logging.info("   Selected mode: Resource Estimation")
		logging.info("========================================")
		# TODO
		# Synthesize PE, NoC and Task managers individually
		RscResults={}
		PEs = APP.GetPEs()
		#------------------------------------------
		if "NoC" in Operation.LibServices:
			AdOCNet=Operation.LibServices["AdOCNet"].GetModule()
		else: 
			logging.error("No such service 'NoC' in library. Aborted.")
			yield (Step, NbSteps, False)
		# Setup NoC parameters
		if "NetworkAdapter" in Operation.LibServices:
			NetworkAdapter=Operation.LibServices["NetworkAdapter"].GetModule()
		else: 
			logging.error("No such service 'NetworkAdapter' in library. Aborted.")
			yield (Step, NbSteps, False)
		# Setup NetworkInterface parameters
		if "TaskManager" in Operation.LibServices:
			TaskManager=Operation.LibServices["TaskManager"].GetModule()
		else: 
			logging.error("No such service 'TaskManager' in library. Aborted.")
			yield (Step, NbSteps, False)
		#------------------------------------------
		# Setup TaskManager parameters
		for Mod in PEs+[AdOCNet, TaskManager, NetworkAdapter]:
			HWRsc=TargetHW.ModuleResources(Mod=Mod, Library=APP.Library, RemoteHost=CmdLineArgs.host)
			if HWRsc is None:
				logging.error("Failed to evaluate resources.")
				yield (Step, NbSteps, False)
			else:
				logging.info("Used resources : {0}".format(HWRsc))
				# Update XML
#				AppMod.UpdateResources(FpgaId=TargetHW.GetFPGA(FullId=False), HWRsc=HWRsc)
#				AppMod.DumpToLibrary() 
			RscResults[Mod.Name]=HWRsc
		# Collect resource consumption statistics into a .ini file
		GenStatFile(RscResults)
		yield (Step, NbSteps, True)
	#------------------------
	elif Cmd=="ava-soft": 
		logging.info("========================================")
		logging.info("        Selected mode: AVA-Soft") 
		logging.info("========================================")
		RetVal=YangoTools.AVASoft(
				APP, 
				"ML605", 
				RemoteHost=CmdLineArgs.host
				)

		yield (Step, NbSteps, RetVal)
	#------------------------
	elif Cmd.lower()=="verify":
		logging.info("========================================")
		logging.info("         Selected mode: Verify")
		logging.info("========================================")
		#-----------------------------------------------------------
		if CmdLineArgs.loopback is False:
			if CmdLineArgs.RefVCD is None:
				Results=YangoTools.Simulate(
						APP, 
						Simulator    = "isim", 
						RemoteHost   = CmdLineArgs.host, 
						ModuleList   = CmdLineArgs.module, 
						InstanceList = CmdLineArgs.instance, 
						SignalDepth  = CmdLineArgs.signaldepth, 
						NbCycles     = CmdLineArgs.clockcycles, 
						CycleLength  = CmdLineArgs.cyclelength,
						OutputPath   = AppSimuPath, 
						DisplayWaveForm=False
						)
				if Results is None:
					logging.error("Simulation failed unable to generate reference VCD file. Verification Aborted.")
					yield (Step, NbSteps, False)
				WaveformFilePath, VCDPath = Results
			else:
				if CmdLineArgs.BinaryPath is None:
					logging.error("BinaryPath must be provided when using RefVCD. Verification aborted.")
					yield (Step, NbSteps, False)
		#-----------------------------------------------------------

		VerifyPath=os.path.join(AppPath, "Verification")

		HwArchi=HwModel(CmdLineArgs.archi)
		# Generate binary for Target
		
		#----------
		if CmdLineArgs.loopback is True:
			#---------------------------------
			if "ControlVerif_Loopback" in Operation.LibServices:
				ControlVerifServ=Operation.LibServices["ControlVerif_Loopback"] 
			else:
				logging.error("No such service '{0}' in library. exiting.".format("ControlVerif_Loopback"))
				sys.exit(1)
			ControlVerifServ.Alias="LOOPBACK"
			#---------------------------------
			LoopbackMod = ControlVerifServ.GetModule(Constraints=None)
			VerifModule=LoopbackMod
		else:
			VerifModule=AppMod
		
		DUTMod, StimuliList, TracesList, ClockList = Verify.WrapForTest(Module=VerifModule)
		
		VerifTopMod = Verify.GetTopVerif(HwArchi=HwArchi)
		if VerifTopMod is None:
			logging.error("No verification module found for hardware {0}".format(HwArchi))
			yield (Step, NbSteps, False)

		PadConstraints=HwArchi.GetBaseCtrlConstraints()
		if PadConstraints is None:
			logging.error("[Implement] No FPGA pad constraints generated: implementation aborted.")
			yield (Step, NbSteps, False)
			
		# Copy constraint file to implement directory
		ImplementPath=os.path.join(AppSynthesisPath, "Verification-"+HwArchi.Name)
		if not os.path.isdir(ImplementPath): os.makedirs(ImplementPath)
		shutil.copyfile(PadConstraints, os.path.join(ImplementPath, os.path.basename(PadConstraints)))

		#---------------------
		DUTInstance=SyntheSys.SysGen.Module.Instance(Name=DUTMod.Name, Mod=DUTMod)
		TopInstance=SyntheSys.SysGen.Module.Instance(Name=VerifTopMod.Name, Mod=VerifTopMod)
		
#		from lxml import etree
#		print(etree.tostring(VerifTopMod.XMLElmt, encoding="UTF-8", pretty_print=True))
		
		DUTSourcesList = DUTMod.GenSrc( 
					Synthesizable = True, 
					OutputDir     = os.path.join(VerifyPath, "src"), 
					TestBench     = False, 
					IsTop         = False,
					ModInstance   = DUTInstance,
#					TBValues      = TBValues,
#					TBClkCycles   = TBClkCycles,
#					CommunicationService=CommunicationService
					Recursive=False,
					)
		SourcesList = VerifTopMod.GenSrc( 
					Synthesizable = True, 
					OutputDir     = os.path.join(VerifyPath, "src"), 
					TestBench     = False, 
					IsTop         = True,
					ModInstance   = TopInstance,
#					TBValues      = TBValues,
#					TBClkCycles   = TBClkCycles,
#					CommunicationService=CommunicationService
					)
		# Change required service SimuCom to become simple instead of orthogonal ???
		VerifTopMod.Sources["RTL"]+=DUTSourcesList[:1]
		if CmdLineArgs.loopback:
			VerifModule.GenSrc( 
					Synthesizable = True, 
					OutputDir     = os.path.join(VerifyPath, "src"), 
					TestBench     = False, 
					IsTop         = False,
					ModInstance   = DUTInstance,
#					TBValues      = TBValues,
#					TBClkCycles   = TBClkCycles,
#					CommunicationService=CommunicationService
					Recursive=False,
					)
			VerifTopMod.Sources["RTL"]+=VerifModule.Sources["RTL"]
		else:
			VerifTopMod.Sources["RTL"]+=APP.Parameters["Common"]["Sources"]
		
		if CmdLineArgs.BinaryPath is None:
			BinaryPath=HwArchi.Implement(
						Module         = VerifTopMod, 
						PadConstraints = PadConstraints, 
						OutputPath     = ImplementPath, 
						RemoteHost     = CmdLineArgs.host
						)
		else:
			BinaryPath=CmdLineArgs.BinaryPath
			
		#-----------------------------------------
		# UPLOAD TO FPGA
		#-----------------------------------------
		HwArchi.Upload(BinaryPath=BinaryPath, ScanChainPos=5, Remote=True)
		#-----------------------------------------
		
		
		if BinaryPath is None or not os.path.isfile(str(BinaryPath)):
			logging.error("No binary generated for the target board.")
			Step+=1
			yield (Step, NbSteps, False)
		
		logging.info("Generated binary: '{0}'".format(BinaryPath))
		logging.debug("Now process AVA-Test Mono-FPGA Verification...")
		
		if CmdLineArgs.RefVCD is None:
			if CmdLineArgs.loopback is True:
				RefVCD = '/media/matthieu/DATA_EXT4/TRAVAIL/GIT-MP/Python/HDLSynthesis/Library/HDL/Management/Emulation/ControlVerif/Loopback/src/LOOPBACK.vcd'
			else:
				RefVCD = VCDPath
		else:
			RefVCD = CmdLineArgs.RefVCD
		
		# Launch verifying flow
		OutputVCD=YangoTools.Verify(
				Module     = AppMod, 
				BinaryPath = BinaryPath, 
				Clocks     = ClockList,
				Stimuli    = StimuliList, 
				Traces     = TracesList, 
				RefVCD     = RefVCD,
				ClockValue = "10", 
				Diff       = True,
				OutputPath = VerifyPath,
				RemoteHost = CmdLineArgs.host
				)
		
		if OutputVCD:
			os.system("gtkwave {0}".format(OutputVCD))
		
		yield (Step, NbSteps, RetVal)
		
#	#------------------------
#	elif Cmd=="ava-test":
#		logging.info("========================================")
#		logging.info("        Selected mode: AVA-Test")
#		logging.info("========================================")
#		if CmdLineArgs.ctrl is None:
#			logging.error("Please specify a controller for AVA-Test.")
#			sys.exit(1)
#		ControlHW=HwModel(CmdLineArgs.ctrl)
#		# Generate binary for Target
##			TargetBinaryPath=APP.Implement(os.path.join(AppSynthesisPath, "AVA-Test_Ctrl-"+ControlHW.Name+"_Target-"+TargetName), ControlHW=ControlHW, RemoteMode=CmdLineArgs.remote)
#			
#		# Give a name prefixed by "Target_" 
##			NewTargetBinaryPath=os.path.join(os.path.dirname(TargetBinaryPath), ControlHW.Name+"_"+TargetName+"_"+os.path.basename(TargetBinaryPath))
##			os.rename(TargetBinaryPath, NewTargetBinaryPath)
##			logging.debug("Generated binary: '{0}'".format(NewTargetBinaryPath))
#		# Launch AVA-Test flow
##			NewTargetBinaryPath="/media/matthieu/DATA_EXT4/TRAVAIL/GIT-MP/Python/HDLSynthesis/Examples/BinomialTree/BOPM/implement/MiniX/AVA-Test_Ctrl-ML605_Target-MiniX/MiniX_2015-04-15_07h52m27s/ML605_MiniX_BOPM.bit"
#		NewTargetBinaryPath="/media/payet/DATA/TRAVAIL/GIT-MP/Python/HDLSynthesis/Examples/BinomialTree/BOPM/implement/MiniX/AVA-Test_Ctrl-ML605_Target-MiniX/MiniX_2015-06-02_10h52m03s/ML605_MiniX_BOPM.bit"
#		if NewTargetBinaryPath is None or not os.path.isfile(str(NewTargetBinaryPath)):
#			logging.error("No binary generated for the target board.")
#			yield (Step, NbSteps, False)
#		if not os.path.isfile(NewTargetBinaryPath):
#			logging.error("No such file '{0}'. Aborted.".format(NewTargetBinaryPath))
#			yield (Step, NbSteps, False)
#		Configurations=ControlHW.GetCtrlConfig(TargetHW=TargetHW, Module=AppMod)
#		RetVal=YangoTools.AVATest(
#				APP, 
#				Ctrl=CmdLineArgs.ctrl, 
#				Target=CmdLineArgs.archi,
#				BinaryPath=NewTargetBinaryPath, 
#				Values=WellNamedAppStimValues, 
#				ClockValue="10", 
#				Diff=False,
#				Configuration=Configurations[0], 
#				OutputPath=os.path.join(AppPath, "AVA-Test"),
#				Remote=CmdLineArgs.remote
#				)
#		if RetVal:
#			os.system("cat {0}".format(os.path.join(AppPath, "AVA-Test", "traceValues.txt")))
#		yield (Step, NbSteps, RetVal)

#====================================================================	
def GeneratePackageFile(Name, BinaryPath, AppBinPath, AppPath):
	"""
	Pack .bit and *.bin files into a tar.gz.
	"""
	shutil.copy(BinaryPath, AppBinPath)
	CurDir=os.path.abspath('.')
	os.chdir(AppBinPath)
	ArchPath=os.path.abspath(os.path.join(AppPath,"{0}.tar.gz".format(Name)))
	shutil.make_archive(ArchPath, 'gztar', '.', verbose=True)
	os.chdir(CurDir)
	return ArchPath
	
#====================================================================	
def GenerateConfData(APP, SystemMod, NoCMapping, Sched, SrcOutputPath, BinOutputPath):
	"""
	Generate binary files for configuration and testbench data stimuli.
	"""
	#------------------------------------------------
	# First find the communication node
	ComNode=None
	for Node, Coordinates in NoCMapping.items():
		if Node.GetType()=="Communication":
			ComNode        = Node
			ComCoordinates = Coordinates
			ComService     = Node.GetService()
			break

	if ComNode is None:
		logging.error("[GenerateConfData] No communication operator found: aborted.")
		return {}, None, None
	
	#------------------------------------------------
	# Generate high level stimuli from testbench function
	TaskStimDict, TaskConstStimDict=Testbench.GenStimDict(Mod=SystemMod) # Return dict with Operation:ArgValuesDict pairs

	#------------------------
	# Optimize NoC parameters for a given number of stimuli (prevent from saturating the communication port buffer)
	NbReduceTask=0
	for Task, v in Sched.items():
#		print("Task.Name:", Task.Name)
		if Task.Name=="Reduce":
			NbReduceTask+=1
#	print("NbReduceTask:",NbReduceTask)
#	input()
	NbConfigPathValues   = len(NoCMapping)*8
	NbStimValues         = len(list(TaskStimDict.values())[0])
	NbConfigReduceValues = NbReduceTask*3
	SoCParams=APP.OptimizeParameters(NbInput=3*(NbConfigPathValues+NbStimValues+NbConfigReduceValues) if TaskStimDict else 16, ComCoordinates=ComCoordinates) # 16 by default : TODO change it !
	# Setup parameters of Communication module
	ComService.UpdateAllValues(SoCParams)

	# Generate Network stimuli from high level stimuli (TaskStimDict)
	logging.debug("[SyntheSys] Generate stimuli")
	StimValues, Values=SoCConfig.GenStim(
	                                 TaskStimDict = TaskStimDict, 
	                                 NoCMapping   = NoCMapping,
	                                 Schedule     = Sched, 
	                                 ComServ      = ComService,
	                                 ConstConfig  = False)

	# ConstantValues
	logging.debug("[SyntheSys] Generate constant stimuli")
	ConstantStimValues, ConstantValues=SoCConfig.GenStim(
	                                                TaskStimDict = TaskConstStimDict, 
	                                                NoCMapping   = NoCMapping,
	                                                Schedule     = Sched, 
	                                                ComServ      = ComService,
	                                                ConstConfig  = True)

	
	# ConstantValues
	logging.debug("[SyntheSys] Generate reduces configurations")
	ReduceStimValues, ReduceValues = SoCConfig.GenMapReduceConfig(
	                                               NoCMapping = NoCMapping, 
	                                               Schedule   = Sched, 
	                                               ComServ    = ComService,
	                                               OutputPath = SrcOutputPath)

	# Data paths ------------------------------------------------------------
	logging.debug("[SyntheSys] Generate data paths")
	DataPath, DataPathFilePath=SoCConfig.GenerateDataPath(
	                                            NoCMapping = NoCMapping, 
	                                            Schedule   = Sched, 
	                                            ComNode    = Node,
	                                            ComCoordinates = Coordinates,
	                                            ComServ    = ComService,
	                                            OutputPath = SrcOutputPath)
	DataPathStimValues, DataPathValues=SoCConfig.DataPathToValues(
	                                                     DataPath, 
	                                                     NoCMapping, 
	                                                     ComServ = ComService,
	                                                     IncludeComNode=False, 
	                                                     Multicast=True)
#	print("DataPath:", '\n'.join([str(k)+':'+str([str(i) for i in v]) for k,v in DataPath.items()]))
#	print("DataPathValues:", DataPathValues)
#	input()
#	print("DataPathValues : ",DataPathValues)
#	print("Values         : ",Values)

	# Ctrl paths ------------------------------------------------------------
	logging.debug("[SyntheSys] Generate control paths")
	CtrlPath, CtrlPathFilePath=SoCConfig.GenerateCtrlPath(
	                                            NoCMapping = NoCMapping, 
	                                            Schedule   = Sched, 
	                                            ComNode    = Node,
	                                            ComCoordinates = Coordinates,
	                                            ComServ    = ComService,
	                                            OutputPath = SrcOutputPath)
	CtrlPathStimValues, CtrlPathValues, Parameters=SoCConfig.CtrlPathToValues(
	                                                                CtrlPath, 
	                                                                NoCMapping, 
	                                                                Schedule=Sched, 
	                                                                ComServ=ComService)
	
	# Memory read back
	X,Y=(0,0)
	N=GetNode(NoCMapping,X,Y)
	if N.GetService()==ComService:
#		logging.error("Node ({0},{1}) is the communication node.".format(X,Y))
#		sys.exit(1)
		X,Y=(1,0)
		N=GetNode(NoCMapping,X,Y)
		
	ComHeader=int("00000000{0:04b}{1:04b}".format(*ComCoordinates),2)
	# Read back internal Configuration memories
#	DATA_ID1=N.GetDataID(Type="HEADER_CONFIG", MemoryRead=False, FlitWidth=ComService.Params["FlitWidth"].GetValue(), StartIndex=0, TaskAddress=0)
#	MemoryFillStimValues, MemoryFillValues=ComService.GenInputStim(TaskValues=list(range(10, 5, -1)), DataID=DATA_ID1, X=X, Y=Y, PayloadReceived=5)
#	DATA_ID2=N.GetDataID(Type="HEADER_CONFIG", MemoryRead=True, FlitWidth=ComService.Params["FlitWidth"].GetValue(), StartIndex=0, TaskAddress=0)
##	input("ComHeader: {0}".format("00000000{0:04b}{1:04b}".format(*ComCoordinates)))
##	input("in integer: {0}".format(ComHeader))
#	MemoryReadStimValues, MemoryReadValues=ComService.GenInputStim(TaskValues=[ComHeader,], DataID=DATA_ID2, X=X, Y=Y, PayloadReceived=1) 
	
	#----------------
	GenerateBinary(Values, os.path.join(BinOutputPath, "DataValues.bin"), ("DataIn", 8))
	GenerateBinary(ConstantValues, os.path.join(BinOutputPath, "ConstValues.bin"), ("DataIn", 8))
	GenerateBinary(ReduceValues, os.path.join(BinOutputPath, "ReduceValues.bin"), ("DataIn", 8))
	GenerateBinary(DataPathValues, os.path.join(BinOutputPath, "DataPath.bin"), ("DataIn", 8))
	GenerateBinary(CtrlPathValues, os.path.join(BinOutputPath, "CtrlPath.bin"), ("DataIn", 8))
	
#	GenerateBinary(MemoryFillValues, os.path.join(BinOutputPath, "MemoryFill.bin"), ("DataIn", 8))
#	GenerateBinary(MemoryReadValues, os.path.join(BinOutputPath, "MemoryRead.bin"), ("DataIn", 8))
	
	# TODO : Use 'Parameters' to configurate HDL
	# Concatenate configuration and stimuli values in AppStimValues 
	# and keep them for simulation runtime
	ExtensionTime=1000 # TODO : set as parameters ?
	
	# Concatenate all stimuli values : running and configuration
	AppStimValues=DataPathStimValues.copy()
	for Name in AppStimValues:
		ValueList=AppStimValues[Name]
		if len(CtrlPathStimValues)>0: # Add control configuration
			ValueList.extend(CtrlPathStimValues[Name])
		if len(ReduceStimValues)>0: # Add constants configuration
			ValueList.extend(ReduceStimValues[Name])
		if len(ConstantStimValues)>0: # Add constants configuration
			ValueList.extend(ConstantStimValues[Name])
#			AppStimValues[Name]+=CtrlPathStimValues[Name]+Values[Name]+[Values[Name][-1] for i in range(KeepValuesLength)]
		
		ValueList.extend(StimValues[Name])
		ValueList.extend([StimValues[Name][-1] for i in range(ExtensionTime)])
#		for i in range(5):
#		ValueList.extend(MemoryFillStimValues[Name])
#		ValueList.extend(MemoryReadStimValues[Name])
#			ValueList.extend([StimValues[Name][-1] for i in range(50)])
	
	return AppStimValues, ComCoordinates, ComService

#====================================================================	
def DirectoryPath(Path):
	"""
	raise error if path is no a directory
	"""
	if os.path.isdir(Path):
		return os.path.abspath(Path)
	else:
		try: os.makedirs(Path)
		except: raise TypeError

#====================================================================	
def FilePath(Path):
	"""
	raise error if path is no a directory
	"""
	if os.path.isfile(Path):
		return os.path.abspath(Path)
	else:
		raise TypeError
#====================================================================	
def GenerateBinary(ValuesDict, NewBinaryPath, *DumpList):
	"""
	Create a binary file and dump values for each data of the DumpList Tuple (DataName, Size) given in ValuesDict.
	Size is the number of bytes to be writen for each value (can be only 1, 2, 4 or 8).
	"""
	TypeDict={1:'B', 2:'H', 4:'I', 8:'Q'}
	with open(NewBinaryPath, "wb+") as BinFile:
		for Dat, Size in DumpList:
			if Dat in ValuesDict:
#				print("Data:", Dat)
#				print("Data:", Size)
#				print("ValuesDict:", ValuesDict[Dat])
#				print("len(ValuesDict[Dat]):", len(ValuesDict[Dat]))
				ValueList=[]
				for v in ValuesDict[Dat]:
					if isinstance(v, float):
						ValueList.append(IntegerEquivalentToFloat(v, TypeDict[Size]))
					elif isinstance(v, int):
						ValueList.append(v)
					else:
						logging.error("[GenerateBinary] Cannot generate binary representation of value '{0}' of type '{1}'.".format(v, type(v)))
						sys.exit(1)
				for V in ValueList:
#					print("V:", V, "hex:", hex(V))
#					print("Size:", Size)
#					print("TypeDict[Size]:", TypeDict[Size])
					BinFile.write(struct.pack(TypeDict[Size], V)) 
	

#====================================================================
def IntegerEquivalentToFloat(FloatNum, Type):
	FloatFormat='d' if Type=='q' else 'f'
	FloatRep = struct.pack(FloatFormat, FloatNum)
#	print("FloatNum:", FloatNum)
#	print("struct.pack(",FloatFormat,", FloatNum):", FloatRep, '=>', len(FloatRep))
	return struct.unpack(Type, FloatRep)[0]
#	StringRep=''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', FloatNum).decode("utf-8"))
#	if len(StringRep)>SizeMax:
#		logging.error("Cannot convert value '{0}' to integer equivalent. Integer size required is '{1}', given is '{2}'".format(StringRep, SizeMax, SizeMax))
#	return int(StringRep, 2)
	
#====================================================================
def GetNode(Mapping, X, Y):
	"""
	Return Node mapped at given coordinates.
	"""
	for Node, Coord in Mapping.items():
		if Coord==(X,Y):
			return Node
	return None
	
	
#====================================================================
def ParseOptions():
	"""
	Parse argument options and do corresponding actions.
	"""
	Parser = argparse.ArgumentParser(description="SyntheSys analysis, simulation and implement tools", epilog="")
	
	#------------------General command arguments-----------------
	# ARGUMENT: Server name
	Parser.add_argument('command', action='store', help='Name of command to execute ("Simulation", "AVA-Soft", "AVA-Test", "Implement", "Verify", "YANGO" - GUI for customization).', type=str, default=None)
	Parser.add_argument('--host', action='store', help='Execute commands remotely on given host.', default=None)
	Parser.add_argument('-o', '--output', action='store', help='Output folder path.', type=DirectoryPath, default=None)
	Parser.add_argument('--signaldepth', action='store', type=int, help='Define the depth at which the signals of the design are added to waveforms.', default=999999)
	Parser.add_argument('-m', '--module', action='append', help='Module to display signals.', default=[])
	Parser.add_argument('-i', '--instance', action='append', help='Instance to display signals.', default=[])
	Parser.add_argument('-c', '--clockcycles', action='store', type=int, help='Number of clock cycles to trace (in testbench). Default is 800 cycles.', default=2000)
	Parser.add_argument('--cyclelength', action='store', type=int, help='Length of a clock cycle in ns. Default is 10 ns.', default=10)
	Parser.add_argument('-a', '--archi', required=False, action='store', help='Every architecture to target.', default="TooBigFpga")
#	Parser.add_argument('--ctrl', action='store', help='Control architecture for AVA-Test.', default=None)
#	Parser.add_argument('--BinaryPath', action='store', type=FilePath, help='Specify the verification binary path to be loaded onto the FPGA.', default=None)
#	Parser.add_argument('--RefVCD', action='store', type=FilePath, help='Specify the reference VCD path to be loaded for FPGA verification.', default=None)
#	Parser.add_argument('--loopback', action='store_true', help='Execute commands remotely.', default=False)
#	Parser.add_argument('--setupsimu', action='store', type=FilePath, help='Script that setup simulator environment.', default=None)
	Parser.add_argument('--simulator', action='store', help='Name of the simulator to use. Supported simulators are "gHDL", "modelsim", "questasim", "isim", ""', type=str, default="isim")
	Parser.add_argument('--fpgadesign', action='store', type=FilePath, help='Specify file path to a previous design (FpgaDesign file : *.soc) to be used as constraints for the application generation.', default=None)
	
	Parser.add_argument('-n', '--noc', required=False, action='store', help='Name of the NoC to use.', default="AdOCNet")
	#------------------
#	Parser.set_defaults(func=LaunchFunc)
	Args = Parser.parse_args()
		
	return Args	
	
	
	
	
	
	
	
	
