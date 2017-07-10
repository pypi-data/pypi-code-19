#!/usr/bin/python

MODULE="SyntheSys.YANGO"
DESCRIPTION="SyntheSys.YANGO - Yet Another NoC Generator and Optimizer"
VERSION="python"
DATETIME="2013-09-19 at 17:00:47"

import logging
import os, sys
import zipfile
import tempfile

from SyntheSys.Utilities.Timer import TimeStamp
#from SyntheSys.Utilities import GenericGUI

from SyntheSys.YANGO import GUI
from SyntheSys.YANGO import Components


import SyntheSys.SysGen
from SyntheSys.SysGen import Simulation

#=======================================================================
def InitGUI(LibraryPath, Application):
	"""
	Initialize and launch GUI.
	"""
	logging.info("Fetch the folder where bundle is localised")	

	# Now test environnement variable ---------------------------------	
#	if(not ConsoleInterface.TestEnv(None)): 
#		GenericGUI.PopupDialog("Environment variable not set", "One or more environment variable 'ADACSYS_ROOT', 'ADACSYS_TOOL', 'ADACSYS_VERSION' is not set.\n\nPlease source the 'a_env' script, or set these variables manually.")
#		sys.exit(1)


	# Get the library path and launch the GUI
	if os.path.isdir(LibraryPath):
		LibPath  = os.path.abspath(LibraryPath)
		SyntheSys.YANGOGUI = GUI.GUI(
				Title=DESCRIPTION, 
				Version=VERSION, 
				LibPath=LibPath, 
				BundleDir=ExtractBundle(), 
				CloseFunctions=[], 
				ResourcesDirs=[]
				)
		if Application:
			SyntheSys.YANGOGUI.SetApplication(Application)
	else:
		logging.error("No SyntheSys.YANGO library '{0}' found. Please specify a correct path in the options (--lib or -l).".format(LibraryPath))
	return SyntheSys.YANGOGUI
	
#=======================================================================
def ExtractBundle():
	"""
	Extract zip bundle file.
	"""
	BundleDir = os.path.dirname(__file__)
	
	# Open extract resources archive-------------------------------------------
	logging.info("Extract bundle zip here")
	ZipFile   = os.path.join(BundleDir, 'Bundle.zip') 
	ThemeZip  = zipfile.ZipFile(ZipFile, 'r')
	BundleDir = os.path.abspath(os.path.join(BundleDir, "Bundle"))
	ThemeZip.extractall(BundleDir)
	ThemeZip.close()
	return BundleDir
	
#=======================================================================
def GetHDL(Options):
	"""
	Create a component object for given items and generate its sources files.
	"""
	logging.info("Generate HDL sources for module '{0}'.".format(Options.module))
	logging.info("Output file path: '{0}'.".format(Options.output))
	
	if os.path.isdir(Options.output):
		OutputPath=os.path.join(Options.output, Options.module)
	else:
		logging.error("Specified output path is not a directory.")
		return False
	
	Library=SyntheSys.SysGen.XmlLibManager.XmlLibManager(SyntheSys.SysGen.BBLIBRARYPATH)
	Mod=Library.Module(Options.module, [Library,])
	
	logging.info("Parameters: {0}".format(Options.parameter))
	for PAssignment in Options.parameter:
		if PAssignment=='': continue
		PName, Value=PAssignment.split('=')
		if PName in Mod.Params:
			logging.info("\t> Set '{0}' to {1}.".format(PName, Value))
			Mod.EditParam(PName, Value)
		else:
			logging.error("No such parameter '{0}' in module '{1}'.".format(PName, Options.module))
			
	Mod.Reload() # For loops regeneration
	Mod.IdentifyServices(Library.Services)
			
	TopInstance=SyntheSys.SysGen.Module.Instance(Name="DUT_"+Options.module, Mod=Mod)
	SourcesList = Mod.GenSrc(
				Synthesizable = True, 
				OutputDir     = OutputPath, 
				TestBench     = True, 
				IsTop         = True,
				ModInstance   = TopInstance,
				)
	return True
	

#==================================================================
def NewGUI(Application=None):
	"""
	Open GUI for SyntheSys.YANGO manager.
	"""
	SyntheSys.YANGOGUI=InitGUI(LibraryPath=SyntheSys.SysGen.BBLIBRARYPATH, Application=Application)
		
	return SyntheSys.YANGOGUI
	
#=======================================================================
def NewApp(Name, Library=None):
	"""
	return App component instance.
	"""
	if Library is None: Library=SyntheSys.SysGen.XmlLibManager.XmlLibManager(SyntheSys.SysGen.BBLIBRARYPATH)
	HTree=Components.App(Library=Library, Name=Name, Bundle=None)
	HTree.AddChild("Algorithm", Name=Name+"_Algo", FromLib=False, ExtraParameters={})
	return HTree
	
#=======================================================================
def Simulate(App, Simulator="isim", RemoteHost=None, ModuleList=[], InstanceList=[], SignalDepth=999999, NbCycles=1600, CycleLength=10, OutputPath=None, DisplayWaveForm=False):
	"""
	Launch simulation on application with specified AVAFiles.
	"""
	if not isinstance(App, Components.TreeMember):
		logging.error("Component to simulate must be a treemember instance, not {0}.".format(type(App)))
		return None
	#-----------------------------------
	if OutputPath is None:
		SimuPath=tempfile.mkdtemp(suffix='', prefix='{0}_Simulation'.format(App.Parameters["Common"]["Name"]))
	else:
		SimuPath=os.path.join(OutputPath, App.Parameters["Common"]["Module"].Name, "Simulation", TimeStamp())
		
	if not os.path.isdir(SimuPath):
		os.makedirs(SimuPath)
		
	if not "Module" in App.Parameters["Common"]:
		logging.error("No top module generated from selected item. Please generate module first.")
		return None
	Sim = Simulation.Simulation(
				Module=App.Parameters["Common"]["Module"], 
				ModInstance=App.Parameters["Common"]["Instance"],
				OutputPath=SimuPath
				)
	Sim.SetRemoteHost(RemoteHost=RemoteHost, PromptID=False, Config=None)
	ResultFiles=Sim.Run(
			Simulator=Simulator, 
			NbCycles=NbCycles, 
			CycleLength=CycleLength, 
			ModuleList=ModuleList, 
			InstanceList=InstanceList, 
			SignalDepth=SignalDepth
			)
#	if ResultFiles is None:
#		return None
#	WaveformFilePath, VCDPath=Results
#	if DisplayWaveForm is True:
#		os.system("""/bin/bash -l -c 'source "{0}" && isimgui -view "{1}"'""".format(Sim.ise_env, WaveformFilePath))
	#-----------------------------------
	return ResultFiles#WaveformFilePath, VCDPath
	
#=======================================================================
def AVASoft(Application, Architecture):
	"""
	Run AVA-Soft Flow to verify specified application on specified architecture.
	"""
	#---------	
	Project=AVAProject.NewTempProjectWithTB(Architecture) # LOCAL PROJECT
	if Project is None:
		logging.error("Unable to create temporary project.") 
		return False
	if Project.LoadSyntheSys.YANGOApp(Application) is False:
		logging.error("Unable to load application data to AVA project.") 
		return False
	#---------	
	if Remote is True:
		return AVASoftCmd.RemoteFlow(Project, Architecture)
	else:
		return AVASoftCmd.LocalFlow(Project, Architecture)
	
#=======================================================================
def AVATest(Application, Ctrl, Target, BinaryPath, Values, ClockValue="10", Diff=False, Configuration=None, OutputPath="./AVA-Test", Remote=True):
	"""
	Run AVA-Test Flow to verify specified application on specified Ctrl and target.
	"""
	os.environ["TOOL"]="AVA-Soft"
	#---------	
#	CmdFile=os.path.join(os.environ["ADACSYS_ROOT"], os.environ["ADACSYS_TOOL"], os.environ["ADACSYS_VERSION"], "etc", "AVACmd.ini")
#	Project=AVAProject.NewTempProjectWithTB(Ctrl, TBName="TB0", CmdFile=CmdFile) # LOCAL PROJECT
	#---------	
#	if Project is None:
#		logging.error("[SyntheSys.YANGO.Tools.Flow] Unable to create temporary project.") 
#		return False
	if Configuration is None:
		logging.error("[SyntheSys.YANGO.Tools.Flow] No configuration specified. Aborted.")
		return False
#	if Project.LoadSyntheSys.YANGOApp(Application) is False:
#		logging.error("[SyntheSys.YANGO.Tools.Flow] Unable to load application data to AVA project.") 
#		return False
	#---------	
	Module       = Application.GetModule()
	ClockNames   = Module.GetClockNames()
	StimuliNames = Module.GetStimuliNames()
	TraceNames   = Module.GetTraceNames()
	#---------	
	if AVAProject.GenAvaFiles(ClockNames=ClockNames, Stimuli=StimuliNames, Traces=TraceNames, ModuleName=Module.Name, Values=Values, OutputPath=OutputPath) is False:
		logging.error("Unable to generate AVA files from application '{0}'".format(Application))
		return None
		
	return AVATestCmd.Flow(
			Ctrl          = Ctrl, 
			Target        = Target, 
			BinaryPath    = BinaryPath, 
			ClockValue    = ClockValue, 
			Diff          = Diff, 
			Configuration = Configuration, 
			OutputPath    = OutputPath, 
			Remote        = Remote
			)
	
#=======================================================================
def Implement(Lib, OutputPath="./", Application=None):
	"""
	Create a App component object for each application specified.
	From it, execute the Generate method to get all output files.
	"""
	if Application is None:
		logging.error("Please specify an application name.")
	else:
		Application=Components.App(Library=Lib, Name=Application)
		if Application.IsInLibrary(Application):
			#------------------------------------------------
			def CmdSuccess():
				"""
				Current command execution succeeded: pass.
				"""
				pass
			#------------------------------------------------
			def CmdFailed():
				"""
				Current command execution failed: pass.
				"""
				logging.info("An error occured during implementation process: aborted.")
				logging.error("> An error occured during implementation process: aborted.")
			#------------------------------------------------
			logging.info("SyntheSys.YANGO: Implementation start for application '{0}'.".format(Application))
			Application.SetFromLib(Application)
			for ImplementFlow in Application.Implement():
				if ImplementFlow!=None:
					ImplementFlow.Start(CmdSuccess, CmdFailed, StopAfterFailure=True)
			#------------------------------------------------
			HWRsc=TargetHW.ModuleResources(Mod=Mod, Remote=False)
			if HWRsc is None:
				logging.error("Failed to evaluate resources.")
				return None
			else:
				logging.info("Used resources : {0}".format(HWRsc))
				# Update XML
				Mod.UpdateResources(FpgaId=TargetHW.GetFPGA(FullId=False), HWRsc=HWRsc)
				Mod.DumpToLibrary() 
				return HWRsc
		else:
			logging.error("No application named '{0}' available in library.".format(Application))
	sys.exit(0)
	
#=======================================================================
def Verify(Module, BinaryPath, Clocks, Stimuli, Traces, RefVCD, ClockValue="10", Diff=False, OutputPath="./AVA-Test", Remote=True):
	"""
	Run AVA-Test Flow to verify specified application on specified architecture.
	"""
	os.environ["TOOL"]="AVA-Soft"
	
	#---------
	ClockNames   = [x.GetName() for x in Clocks]
	StimuliNames = [x.GetName() for x in Stimuli]
	TraceNames   = [x.GetName() for x in Traces]
#	logging.info("ClockNames: {0}".format(ClockNames))
#	logging.info("StimuliNames: {0}".format(StimuliNames))
#	logging.info("TraceNames: {0}".format(TraceNames))
	StimuliSizes = [x.GetSize() for x in Stimuli]
	TraceSizes   = [x.GetSize() for x in Traces]
	
	#---------
	if AVAProject.GenAvaFiles(ClockNames=ClockNames, StimuliNames=StimuliNames, StimuliSizes=StimuliSizes, TraceNames=TraceNames, TraceSizes=TraceSizes, ModuleName=Module.Name, Values=None, OutputPath=OutputPath) is False:
		logging.error("Unable to generate AVA files from module '{0}'".format(Module))
		return None
		
	#---------
	return AVATestCmd.Verify(
			HwArchi="ML605", 
			RefVCD=RefVCD, 
			ClockValue=ClockValue, 
			Diff=Diff, 
			Configuration="MiniX_Mono", 
			OutputPath=OutputPath, 
			Remote=Remote
			)
	
#	AVATestCmd.Flow(
#			Ctrl          = Ctrl, 
#			Target        = Target, 
#			BinaryPath    = BinaryPath, 
#			ClockValue    = ClockValue, 
#			Diff          = Diff, 
#			Configuration = Configuration, 
#			OutputPath    = OutputPath, 
#			Remote        = Remote
#			)
	
	

