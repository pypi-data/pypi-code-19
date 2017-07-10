
import sys, os, logging, re
import shutil

#==============================================================
from SyntheSys.Utilities.Timer import TimeStamp
from SyntheSys.Utilities import SafeRun

from SyntheSys.SysGen.Module import Instance

from SyntheSys.Utilities.RemoteOperations import RemoteOperations
from SyntheSys.Utilities.UserConfig import UserConfig
from SyntheSys.Utilities import Misc
from SyntheSys.Utilities.Misc import cd as Localcd



#==============================================================
class Simulation(RemoteOperations):
	"""
	Object that represent a simulation.
	It allows to configure/run simulation and fetch results.
	"""
	#------------------------------------------------------
	def __init__(self, Module, ModInstance, OutputPath="./Simulation", RemoteHost=None):
		"""
		Configure a new simulation environment.
		"""
		RemoteOperations.__init__(self, RemoteSubFolder="Simulation")
		if not os.path.isdir(str(OutputPath)):
			logging.error("Unable to generate files for application: no such output directory '{0}'.".format(str(OutputPath))) 
			return None # Thread, Event, FPGACmds
		self.LocalSimuPath=os.path.abspath(OutputPath)
		self.Module=Module
		
#		self.SrcList=Module.GenSrc(Synthesizable=True, OutputDir=OutputPath, TestBench=True, IsTop=True)
		DepDict=Module.GetDependencies()
		self.DUT=Module.TB_DUT
		self.Packages=DepDict["package"]
		self.Libraries=DepDict["library"]
		self.TBName, self.TBSource, self.DependencyFiles=Module.GetTestBenchInfo()
		
		self.ModuleInstance=Instance(Name=self.TBName, Mod=None)
		self.ModuleInstance.AddInstanceAsInstance(Inst=ModInstance)
		
		self.SrcList=Module.Sources["RTL"]+Module.Sources["Behavioral"]
		if len(self.SrcList)==0:
			logging.error("No sources found in module '{0}'".format(Module))

	#------------------------------------------------------------------------------
	def SetRemoteHost(self, RemoteHost, PromptID=False, Config=None):
		"""
		[OVERLOADED] Set Remote host.
		"""
		RemoteOperations.SetRemoteHost(self, RemoteHost, PromptID=PromptID, Config=Config)
#			ARCHI, OS, OS_CLASS, OS_FULL_NAME = Misc.GetSysInfo()
#	#------------------------------------------------------
#	def SetAvaFiles(self, *AvaFilesPaths):
#		"""
#		Set AvaFiles to be copied before simulation into working directory. 
#		"""
#		self.AvaFiles=[]
#		for FilePath in AvaFilesPaths:
#			if os.path.isfile(FilePath):
#				self.AvaFiles.append(FilePath)
#			else:
#				logging.error("[SetAvaFiles] No such path '{0}'.".format(AvaFilesPath))
#		return True
	#------------------------------------------------------
	def Run(self, Simulator="gHDL", ModuleList=[], InstanceList=[], SignalDepth=999999, NbCycles=1600, CycleLength=10):
		"""
		Launch simulation with specified simulator. 
		"""
		logging.info("----------------------------------")
		logging.info("Simulation path: '{0}'".format(self.LocalSimuPath))
		logging.info("Simulator      : '{0}'".format(Simulator))
		logging.info("----------------------------------")
		Simulator=Simulator.lower()
		#--------------------------------------------------------
		####################################################
		if Simulator=="myhdl":
			logging.error("myhdl simulation not supported yet. aborted.")
			return None
			Simulate_myHDL()
		####################################################
		elif Simulator=="ghdl":
			#As usual, you should analyze the design:
			#$ ghdl -a adder_tb.vhdl

			#And build an executable for the testbench:
			#$ ghdl -e adder_tb

			#You do not need to specify which object files are required: GHDL knows them and automatically adds them in the executable. Now, it is time to run the testbench:
			#$ ghdl -r adder_tb

			#If your design is rather complex, you'd like to inspect signals. Signals value can be dumped using the VCD file format. The resulting file can be read with a wave viewer such as GTKWave. First, you should simulate your design and dump a waveform file:
			#$ ghdl -r adder_tb --vcd=adder.vcd
			
			#Then, you may now view the waves:
			#$ gtkwave adder.vcd
			#--------------------------------------------------------
			SimuScriptPath=os.path.join(self.LocalSimuPath, "SimulationScript_{0}_{1}.txt".format(self.TBName, Simulator))
			with open(SimuScriptPath, "w+") as SimuScript:
				SimuScript.write("\n# Analyze, elaborate and build an exe from the top level entity")
				for FilePath in self.Libraries:
					AbsFilePath=os.path.abspath(FilePath)
					SimuScript.write("\nghdl -i {0}".format(AbsFilePath)) # Import our above example into the current 'work' cache
				for FilePath in self.Packages:
					AbsFilePath=os.path.abspath(FilePath)
					SimuScript.write("\nghdl -i {0}".format(AbsFilePath)) # Import our above example into the current 'work' cache
				for FilePath in self.SrcList:
					AbsFilePath=os.path.abspath(FilePath)
					SimuScript.write("\nghdl -i {0}".format(AbsFilePath)) # Import our above example into the current 'work' cache
				SimuScript.write("\nghdl -m --ieee=synopsys --ieee=mentor -fexplicit {0}".format(self.TBName.lower()))
				SimuScript.write("\n# Run the simulation and output a wave file")
				WaveformFilePath="{0}.vcd".format(self.TBName)
				SimuScript.write("\nghdl -r {0} --vcd={1}".format(self.TBName.lower(), WaveformFilePath))
#				SimuScript.write("\n./{0} --vcd={1}".format(self.TBName.lower(), WaveformFilePath))
				SimuScript.write("\n# Display VCD thanks to Gtkwave application.")
				SimuScript.write("\ngtkwave ./{0}".format(WaveformFilePath))
			#--------------------------------------------------------
			if self.RemoteHost: 
				logging.error("Remote simulation with gHDL not supported yet.")
			else:
				for FilePath in self.DependencyFiles:
					AbsFilePath=os.path.abspath(FilePath)
					shutil.copy(AbsFilePath, self.LocalSimuPath)
				#----------------------------------------------------
				logging.debug("SimuScriptPath: '{0}'".format(SimuScriptPath))
				with Localcd(self.LocalSimuPath):
					if not SafeRun.SafeRun(not sys.platform.startswith('win'), [SimuScriptPath,]):
						logging.info("Simulation script execution success.")
						return WaveformFilePath, WaveformFilePath
					else:
						return None
			return None
		####################################################
		elif Simulator in ["modelsim", "questasim"]:
			#--------------------------------------------------------
			Conf=UserConfig()
			SetupScriptPath=Conf.GetValue(Sec="Simulation", Opt="SourceScript_Modelsim", Host=self.RemoteHost)

			if self.RemoteHost is None:
				if not os.path.isfile(SetupScriptPath):
					logging.error("No such source script '{0}'. Simulation aborted.".format(SetupScriptPath))
					return None
				elif not os.access(SetupScriptPath, os.R_OK):
					logging.error("You do not have the execution right access on script '{0}'. Simulation aborted.".format(SetupScriptPath))
					return None
				
			SimuScriptPath=os.path.join(self.LocalSimuPath, "SimulationScript_{0}_{1}.run".format(self.TBName, Simulator))
			#--------------------------------------------------------
			with open(SimuScriptPath, "w+") as SimuScript:
				SimuScript.write("\n# MODULES COMPILATION")
				SimuScript.write('\nsource "{SETUP_SCRIPT}" && vlib ./work'.format(SETUP_SCRIPT=SetupScriptPath))
				SimuScript.write('\nsource "{SETUP_SCRIPT}" && vmap work ./work'.format(SETUP_SCRIPT=SetupScriptPath))
				for FilePath in self.SrcList:
					AbsFilePath=os.path.abspath(FilePath)
					if self.RemoteHost is None:
						SrcPath=AbsFilePath
					else:
						SrcPath='/'.join(["./src", os.path.basename(FilePath)])
					if FilePath.endswith(".vhd"):
						SimuScript.write('\nsource "{SETUP_SCRIPT}" && vcom -work work "{SRC_PATH}"'.format(SRC_PATH=SrcPath, SETUP_SCRIPT=SetupScriptPath))
					elif FilePath.endswith(".v"):
						SimuScript.write('\nsource "{SETUP_SCRIPT}" && vlog -work work "{SRC_PATH}"'.format(SRC_PATH=SrcPath, SETUP_SCRIPT=SetupScriptPath))
					else:
						logging.error("Source format not recognized ('{0}')".format(AbsFilePath)) 
						
				SimuScript.write("\n\n# COMPILE THE PROJECT TESTBENCH")
				SimuScript.write("""\nsource '{SETUP_SCRIPT}' && vsim -gui work.{TB}""".format(TB=self.TBName, SETUP_SCRIPT=SetupScriptPath)) # /bin/bash -l -c 'cd "{PATH}" && source "{ENV}" && 
			
			#----------------------------------------------------
			logging.debug("SimuScriptPath: '{0}'".format(SimuScriptPath))
#				os.environ["PATH"]=os.environ["PATH"]+':'+self.ise_path
#				with sh.Command(self.ise_env):
			
			if self.RemoteHost is None:
				for FilePath in self.DependencyFiles:
					AbsFilePath=os.path.abspath(FilePath)
					shutil.copy(AbsFilePath, self.LocalSimuPath)
					
				with Localcd(self.LocalSimuPath):
					if not SafeRun.SafeRun(not sys.platform.startswith('win'), [SimuScriptPath,]):
						logging.info("Simulation script execution success.")
						return "", ""
					else:
						return None
			else:
				SimulationPath="Simulation/{0}_Simulation_{1}".format(self.TBName, TimeStamp())
				TargetSrcDirectory='/'.join([SimulationPath, 'src'])
				#----------------------------------------------------
				# Copy scripts to remote host
				#----------------------------------------------------
				DirList=[TargetSrcDirectory,] 
				SetupFileDict={ # Files to be moved
					SimuScriptPath  : os.path.basename(SimuScriptPath),
					}
				SrcDict={}
				for S in self.SrcList:
					SrcDict[S]=os.path.basename(S)
				for FilePath in self.DependencyFiles:
					SetupFileDict[os.path.abspath(FilePath)]=os.path.basename(FilePath)
				
				#----------------------------------------------------
	#			if self.SendPaths(DirList, SetupFileDict) is False: return None
				if self.CreateHostDir(DirList=DirList) is False: return None
				if self.SendPathsRelative(FileDict=SetupFileDict, HostAbsPath=SimulationPath) is False: return None
				if self.SendPathsRelative(FileDict=SrcDict, HostAbsPath=TargetSrcDirectory) is False: return None
				#----------------------------------------------------
			
#				RemoteSetupSafeRun    = '/'.join([SynthesisPath, os.path.basename(SetupSafeRun)])
				RemoteSimuScriptPath = '/'.join([SimulationPath, os.path.basename(SimuScriptPath)])
			
				Success=self.RemoteRun(
					Command='chmod 777 {SimuScript}'.format(SimuScript=RemoteSimuScriptPath),
					ScriptsToSource=[], 
					abort_on_prompts='True', warn_only=True
					)
	#			SetupEnvScript=HwModel.GetSetupEnvScript()
				Success=self.RemoteRun(
					Command='./{SynthesisScript}'.format(SynthesisScript=os.path.basename(RemoteSimuScriptPath)),
					ScriptsToSource=[SetupScriptPath,],
					FromDirectory=SimulationPath,
					abort_on_prompts='True', warn_only=True, XForwarding=True
					)
				if Success:
					# Fetch result files (bitstream, MAP report and PAR report)
#					MapReportPath="/".join([SynthesisPath, "{0}{1}".format(TopName, MapReportExt)])
#				
#					if not self.DownloadFromHost(HostPath=ResultFilePath, LocalPath=LocalSynthesisPath):
#						return None
					logging.info("Simulation success.")
					# Now remove remote directory
					self.RemoteRun(Command='rm -rf {SimulationPath}'.format(SimulationPath=SimulationPath), abort_on_prompts='True', warn_only=True)
					return []
				else:
					# Now remove remote directory
					self.RemoteRun(Command='rm -rf {SimulationPath}'.format(SimulationPath=SimulationPath), abort_on_prompts='True', warn_only=True)
				
					logging.info("Simulation failure.")
					return None
#			# 'module_simu.do'---------------------------------------
#			DO_FilePath = os.path.join(self.LocalSimuPath, '{0}_simu.do'.format(self.Name))
#			with open(DO_FilePath, 'w+') as DO_File:
#				DO_File.write("vlib work\n")
#				DO_File.write("vmap work\n")
#				DO_File.write("vcom -work work -f FileList.txt\n")
#				DO_File.write('vsim -voptargs="+acc" +notimingchecks -L work -t "1ps" work.{0}_tb\n'.format(self.Name))
#				DO_File.write("do wave.do\n")
#				DO_File.write("vcd file myvcd1.vcd")
#				DO_File.write("vcd add -r /sim_minimips/*")
#				DO_File.write("run -all\n\n")
#				
#			# 'FileList.txt'-----------------------------------------
#			LIST_FilePath = os.path.join(self.LocalSimuPath, "FileList.txt")
#			AlreadyWritten=[]
#			with open(LIST_FilePath, 'w+') as LIST_File:
#				for FilePath in self.Sources["RTL"]+self.Sources["Behavioral"]:
#					FileName=os.path.basename(FilePath)	
#					if not AlreadyWritten.count(FileName):
#						LIST_File.write(FileName+'\n')
#						AlreadyWritten.append(FileName)
		####################################################
		elif Simulator=="isim":
			Conf=UserConfig()
			SetupScriptPath=Conf.GetValue(Sec="Simulation", Opt="SourceScript_Isim", Host=self.RemoteHost)
		
			if self.RemoteHost is None:
				if not os.path.isfile(SetupScriptPath):
					logging.error("No such source script '{0}'. Simulation aborted.".format(SetupScriptPath))
					return None
				elif not os.access(SetupScriptPath, os.R_OK):
					logging.error("You do not have the execution right access on script '{0}'. Simulation aborted.".format(SetupScriptPath))
					return None
				#--------------------------------------------------------
			TCLFilePath=os.path.join(self.LocalSimuPath, "TCLScript_{0}".format(self.TBName))
			#--------------------------------------------------------
			CombinedMod  = "(" + ")|(".join(ModuleList) + ")"
			CombinedInst = "(" + ")|(".join(InstanceList) + ")"
			with open(TCLFilePath, "w+") as TCLScript:
				TCLScript.write("\n# TCL Script for TB '{0}'".format(self.TBName))
				TCLScript.write("\n# Shows current scope in design hierarchy.")
				TCLScript.write("\nscope")
#				ROOT="/{0}/{1}".format(self.TBName, self.DUT)
#				TCLScript.write("\nwave add {0}".format(ROOT))
				#-----------------------
				Instances=[]
#				ModuleList.append(self.Module.Name)
				for Inst, Path in self.ModuleInstance.WalkInstances(Depth=SignalDepth):
					if len(InstanceList)>0:
						if Inst.Mod is None: pass
#						elif re.match(CombinedInst, Inst.Name):
##						elif Inst.Name in InstanceList:
#							Instances.append( (Inst, Path) )
#							continue
						else:
							for I in InstanceList:
								ReqPath=I.split('/')
#								print("Test:", ReqPath, "==", Path+[Inst.Name,])
								if ReqPath == Path+[Inst.Name,]:
									if not ((Inst, Path) in Instances):
										Instances.append( (Inst, Path) )
									continue
							
					if len(ModuleList)>0:
						if Inst.Mod is None: pass
						elif re.match(CombinedMod, Inst.Mod.Name):
#						elif Inst.Mod.Name in ModuleList:
							Instances.append( (Inst, Path) )
							continue
#					if len(ModuleList)==0 and len(InstanceList)==0:
						# Display all instances
#						Instances.append( (Inst, Path) )	
				#-----------------------
				if (len(InstanceList)!=0 or len(ModuleList)!=0) and len(Instances)==0: 
					ErrorMsg="No instance or entity {0} found for chronogram display.".format(InstanceList+ModuleList)
					logging.error(ErrorMsg)
					logging.error("Available:")
					for Inst, Path in self.ModuleInstance.WalkInstances(Depth=SignalDepth):
						logging.error("/".join(Path+[str(Inst),]))
					AskAgain=True
					while(AskAgain):
						Answer=input("Force visualisation ? (Y/N)")
						if Answer.lower() in ['y', 'yes']:
							for Path in InstanceList:
								TCLScript.write("\nwave add /{0}/".format(Path))
#								input("\nwave add /{0}/{1}/".format("/".join(Path), Inst.Name))
							AskAgain=False
						elif Answer.lower() in ['n', 'no']:
							AskAgain=False
							return None
						else:
							AskAgain=True
				elif Instances:
					for Inst, Path in Instances:
						TCLScript.write('\ndivider add "{0}"'.format(Inst.Name))
						if len(Path): TCLScript.write("\nwave add /{0}/{1}/".format("/".join(Path), Inst.Name))
						else: TCLScript.write("\nwave add /{0}/".format(Inst.Name))
				else:
					TCLScript.write("\nwave add /{0}/{1}/".format(self.TBName, self.DUT))
				#-----------------------
#				TCLScript.write("\n# Shows you current value of signals in current scope.")
#				TCLScript.write("\nshow value clk")
#				TCLScript.write("\n# Shows the value of a signal named clk.")
#				TCLScript.write("\ndump")
				SimulationLength=int(NbCycles*CycleLength)
#				TCLScript.write("\n# Runs simulation for {0} ns.".format(SimulationLength))
#				TCLScript.write("\nrun {0} ns".format(SimulationLength))
#				TCLScript.write("\n# Resets simulation to time 0.")
#				TCLScript.write("\nrestart")
#				TCLScript.write("\n# Log simulation output of all VHDL signal, Verilog wire and Verilog reg at top level to the waveform database (wdb) file.")
#				TCLScript.write("\nwave log /")
#				TCLScript.write("\n# Runs simulation for 1000 ns.")
#				TCLScript.write("\nrun 1000 ns")
#				TCLScript.write("\n# Log simulation output of /tb/UUT/clk to waveform database (wdb) file starting at current simulation time (i.e. 1000 ns).")
#				TCLScript.write("\nwave log /tb/UUT/clk")
				TCLScript.write("\nvcd dumpfile {0}.vcd".format(self.TBName))
				TCLScript.write("\nvcd dumpvars -m {0} -l 2".format(self.DUT))
#				TCLScript.write("\n# Runs simulation for an additional {0} ns.".format(SimulationLength))
#				TCLScript.write("\nrun {0} ns".format(SimulationLength))
				TCLScript.write("\nrun 3000 ns")
				TCLScript.write("\nrun all") 
				TCLScript.write("\nvcd dumpflush")
				TCLScript.write("\n# Quits simulation.")
				TCLScript.write("\nexit 0\n\n")
			
			#--------------------------------------------------------
			SimuScriptPath=os.path.join(self.LocalSimuPath, "SimulationScript_{0}_{1}.run".format(self.TBName, Simulator))
			with open(SimuScriptPath, "w+") as SimuScript:
				SimuScript.write("\n# MODULES COMPILATION")
				for FilePath in self.SrcList:
					AbsFilePath=os.path.abspath(FilePath)
					if self.RemoteHost is None:
						SrcPath=AbsFilePath
					else:
						SrcPath='/'.join(["./src", os.path.basename(FilePath)])
					if FilePath.endswith(".vhd"):
						SimuScript.write('\nsource "{SETUP_SCRIPT}" && vhpcomp -work work "{0}"'.format(SrcPath, SETUP_SCRIPT=SetupScriptPath))
					elif FilePath.endswith(".v"):
						SimuScript.write('\nsource "{SETUP_SCRIPT}" && vlogcomp -work work "{0}"'.format(SrcPath, SETUP_SCRIPT=SetupScriptPath))
					else:
						logging.error("Source format not recognized ('{0}')".format(SrcPath)) 
						
				SimuScript.write("\n\n# COMPILE THE PROJECT TESTBENCH")
				SimuScript.write("""\nsource "{SETUP_SCRIPT}" && fuse work.{TB} -L unisim -o {PATH}_with_isim.exe""".format(TB=self.TBName, PATH=os.path.join("./", self.TBName), SETUP_SCRIPT=SetupScriptPath)) # /bin/bash -l -c 'cd "{PATH}" && source "{ENV}" && 
				SimuScript.write("\n\n# Run the simulation script previously generated")
				SimuScript.write("""\nsource "{SETUP_SCRIPT}" && {PATH}_with_isim.exe -intstyle xflow -wdb Results_{TB} -tclbatch {TCL}\n\n""".format(TB=self.TBName, PATH=os.path.join("./", self.TBName), TCL=TCLFilePath if not self.RemoteHost else os.path.basename(TCLFilePath), SETUP_SCRIPT=SetupScriptPath))
				WaveformFilePath="Results_{0}.wdb".format(self.TBName)
				SimuScript.write("""\n\nsource "{SETUP_SCRIPT}" && isimgui -view "{WAVE}" """.format(SETUP_SCRIPT=SetupScriptPath, WAVE=WaveformFilePath))
				# Possible options :
					# -sdfnowarn    Do not display SDF warnings.  
					# -sdfnoerror   Treat errors found in SDF file as warnings.  
					# -vcdfile <vcd_file>   Specifies the VCD output file for Verilog projects. Default file name is dump.vcd.
					# -vcdunit <unit>       Specifies the VCD output time unit. Possible values are fs, ps, ns, us, ms and sec. Default is ps.
					# -view <waveform_file.wcfg>   Used in combination with the -gui switch to open the specified waveform file in the ISim graphic user interface.
					# -wdb <waveform_database_file.wdb>   Simulation data is saved to the specified file. For example: x.exe –wdb my.wdb saves the simulation data to my.wdb instead of the default isimgui.wdb.
				
			#--------------------------------------------------------
			if self.RemoteHost:
				#----------------------------------------------------
				SimulationPath="Simulation/{0}_Simulation_{1}".format(self.TBName, TimeStamp())
				TargetSrcDirectory='/'.join([SimulationPath, 'src'])
				#----------------------------------------------------
				# Copy scripts to remote host
				#----------------------------------------------------
				DirList=[TargetSrcDirectory,] 
				SetupFileDict={ # Files to be moved
					SimuScriptPath  : os.path.basename(SimuScriptPath),
					}
				SrcDict={}
				for S in self.SrcList:
					SrcDict[S]=os.path.basename(S)
				for FilePath in self.DependencyFiles:
					SetupFileDict[os.path.abspath(FilePath)]=os.path.basename(FilePath)
			
				#----------------------------------------------------
	#			if self.SendPaths(DirList, SetupFileDict) is False: return None
				if self.CreateHostDir(DirList=DirList) is False: return None
				if self.SendPathsRelative(FileDict=SetupFileDict, HostAbsPath=SimulationPath) is False: return None
				if self.SendPathsRelative(FileDict=SrcDict, HostAbsPath=TargetSrcDirectory) is False: return None
				#----------------------------------------------------
		
#				RemoteSetupSafeRun    = '/'.join([SynthesisPath, os.path.basename(SetupSafeRun)])
				RemoteSimuScriptPath = '/'.join([SimulationPath, os.path.basename(SimuScriptPath)])
		
				Success=self.RemoteRun(
					Command='chmod 777 {SimuScript}'.format(SimuScript=RemoteSimuScriptPath),
					ScriptsToSource=[], 
					abort_on_prompts='True', warn_only=True
					)
	#			SetupEnvScript=HwModel.GetSetupEnvScript()
				Success=self.RemoteRun(
					Command='./{SynthesisScript}'.format(SynthesisScript=os.path.basename(RemoteSimuScriptPath)),
					ScriptsToSource=[SetupScriptPath,],
					FromDirectory=SimulationPath,
					abort_on_prompts='True', warn_only=True, XForwarding=True
					)
				ResultFiles=[os.path.join(self.LocalSimuPath, WaveformFilePath), os.path.join(self.LocalSimuPath, "{0}.vcd".format(self.TBName)),]
				if Success:
					logging.info("Simulation success.")
					# Fetch result files (VCD, Waveforms)
					if not self.DownloadFromHost(
							HostPath=WaveformFilePath, 
							LocalPath=self.LocalSimuPath
							):
						Misc.CleanTempFiles(Path=SimulationPath, Host=self.RemoteHost)
						return None
					# Now remove remote directory
					Misc.CleanTempFiles(Path=SimulationPath, Host=self.RemoteHost)
					return ResultFiles
				else:
					# Now remove remote directory
					Misc.CleanTempFiles(Path=SimulationPath, Host=self.RemoteHost)
			
					logging.info("Simulation failure.")
					return None
				#----------------------------------------------------
			else:
				SimulationPath=self.LocalSimuPath
				for FilePath in self.DependencyFiles:
					AbsFilePath=os.path.abspath(FilePath)
					shutil.copy(AbsFilePath, SimulationPath)
				#----------------------------------------------------
				logging.debug("SimuScriptPath: '{0}'".format(SimuScriptPath))
				with Localcd(SimulationPath):
					if not SafeRun.SafeRun(not sys.platform.startswith('win'), [SimuScriptPath,]):
						logging.info("Simulation script execution success.")
						logging.info("Now open waveform file.")
						WaveformFilePath="Results_{0}.wdb".format(self.TBName)
						WaveformFilePath=os.path.join(SimulationPath, WaveformFilePath)
						return WaveformFilePath, os.path.join(SimulationPath, "{0}.vcd".format(self.TBName))
					else:
						Misc.CleanTempFiles(Path=SimulationPath, Host=self.RemoteHost)
						return None
					
				#----------------------------------------------------
		####################################################
		else:
			logging.error("No such simulator supported '{0}'.".format(Simulator))
			return None
			
#==============================================================
class TrafficSimulation(Simulation):
	"""
	Sub class of simulation dedicated to NoC Traffic simulation.
	"""
	#------------------------------------------------------
	def __init__(self, TopModule, TrafficMatrix={}, OutputPath="./"):
		"""
		Configure traffic parameters.
		"""
		Simulation.__init__(self, Module=TopModule, OutputPath=OutputPath)
		self.TrafficMatrix=TrafficMatrix
		
	#------------------------------------------------------
	def GetLatences(self):
		"""
		Return dictionary of results for traffic sent by each router.
		"""
		Latencies={}
		return Latencies

#=================================================================
#=================================================================
class NoCTrafficModule():
	"""
	myHDL top module.
	"""
	#----------------------------------------------------------
	def __init__(self,Duration=500, TopModule=None):
		"""
		Initialize testbench duration and list of instances.
		"""
		self.InstancesList=InstancesList
		self.Duration=Duration
		
		self.NoCModule = TopModule.Get()
		
		self.Inputs  = [HDL.Signal(HDL.intbv(0, min=0, max=DataWidth)) for k in range(0, NbInputs)]
		self.Outputs = [HDL.Signal(HDL.intbv(0, min=0, max=DataWidth)) for k in range(0, NbOutputs)]
		
	#----------------------------------------------------------
	def nulls(self):
		"""
		support method code
		"""
		pass
	#----------------------------------------------------------
	def Top(self):
		"""
		myhdl module code
		"""
		cmd = "iverilog -o bin2gray -Dwidth=%s bin2gray.v dut_bin2gray.v"

		def NoC(B, G, width):
		    os.system(cmd % width)
		    return HDL.Cosimulation("vvp -m ./myhdl.vpi {0}".format(self.NoCModule.Name), B=B, G=G)
			
		return 

#=================================================================
def Simulate_myHDL():
	"""
	myHDL testbench
	"""
	reset = HDL.ResetSignal(0,active=0,async=True)
	Clk   = HDL.Signal(bool(0))
	#-ClockGenerator-------------------
	@HDL.always(HalfPeriod)
	def ClkDriver():
		Clk.next = not Clk
	
	#-StimuliGenerator-----------------
	@HDL.instance
	def Stimuli():
		#-INIT---------------------
		Rst.next = 1
		yield Clk.negedge
		Rst.next = 0
		#-START--------------------
		for i in range(Duration):
			for Index in range(len(Inputs)):
				Inputs[Index].next = RDM.randrange(len(Inputs))
			yield Clk.negedge
		raise HDL.StopSimulation

	#-Monitor--------------------------
	@HDL.instance
	def monitor():
		#-ClockGenerator-------------------
		@HDL.always_seq(Clk.posedge, reset=reset)
		def TestNewLatency():
			for S in self.Outputs:
				if S.edge():
					print("[{0}] Received packet, latency={1}".format(HDL.now(), S))
			
	#-LaunchSimulation-----------------
	TestedModule = NoCTrafficModule(Duration=500, TopModule=None)
	x = HDL.Signal(intbv(0, min=-8, max=8))
	y = HDL.Signal(intbv(0, min=-64, max=64))

	toVerilog(TestedModule.Top,clock,reset,x,y)
	toVHDL(TestedModule.Top,clock,reset,x,y)

	return HDL.instances()

	
#--------------------------
class NullDevice():
	def write(self, s):
		pass
	def isatty(self):
		return False
#--------------------------











