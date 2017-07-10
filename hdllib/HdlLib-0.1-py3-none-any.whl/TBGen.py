#!/usr/bin/python

VERSION=0.1

import os, sys, logging
import shutil, math
if os.name == 'nt':
	from win32 import win32api
	USER_NAME=win32api.GetUserNameEx(3)
else:
	import pwd
	USER_NAME=pwd.getpwuid(os.getuid())[4]
import datetime, argparse
import collections
#======================LOGGING CONFIGURATION===========================
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from HdlLib.Utilities import ConsoleInterface
ConsoleInterface.ConfigLogging(Version="0.1", ModuleName="SetupTBGen")
from HdlLib.Utilities import ColoredLogging
#======================================================================

from HdlLib.Utilities.ErrorHandlers import HdlLibError
from HdlLib import VHDLParser, Graphics
from HdlLib.SysGen import HDLEditor

from HdlLib.Utilities.ErrorHandlers import ParseError

HDLEditor.INDENT_VALUE='  '

#=======================================================================
def SetupParseOptions(SubParsers):
	"""
	Parse argument options and do corresponding actions.
	"""
	TBGenParser = SubParsers.add_parser('tbgen', help='Generate TBGen files and scenarii automatically from a VHDL source code. TBGen is a VHDL testbench with a scenario description with Alstom syntax.')
	
	#------------------General command arguments-------------------------------------
	# ARGUMENT: VHDL file path
	TBGenParser.add_argument('file', action='store', type=FilePath, help='VHDL source file to be parsed as DUT (Design Under Test).')
	# ARGUMENT: Output directory
	TBGenParser.add_argument('-o', '--outputdir', action='store', type=DirectoryPath , help="Output directory (recursively create the folder when it does not exist. Default is current directory.", default=os.getcwd())
	# ARGUMENT: Display version
	# TBGenParser.add_argument('-v', '--version', action='version', version="SetupTBGen version='{0}'".format(VERSION), help="Displays SetupTBGen version.")
	
	TBGenParser.set_defaults(func=SetupTBGen_Opt)
	return TBGenParser
	
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
		return os.path.abspath(os.path.normpath(os.path.expanduser(Path)))
	else:
		raise TypeError
		
#====================================================================	
def GetExtraParameters(ParamDict):
	"""
	Prompt user for providing extra parameters.
	Input dictionary is a pair {Name : Tuple(type, Description),}.
	"""
	Params={}
	for k,(Type,Desc) in ParamDict.items():
		while(1):
			Answer=input("\tCould you provide a {0} for this signal ? ".format(Desc))
			try: Answer=Type(Answer);break
			except: continue
		Params[k]=Answer
	return Params
	
#================================================================
def SetupTBGen_Opt(Options):
	"""wrapper for SetupTBGen function"""
	return SetupTBGen(VHDLFilePath=Options.file, OutputPath=Options.outputdir)

#================================================================
def SetupTBGen(VHDLFilePath, OutputPath):
	"""
	Generate a whole TBGen testebench files environment from a given VHDL File Path and return True when succeeded.
	"""
	if (OutputPath is None): OutputPath=os.getcwd()
	if not os.path.isdir(OutputPath): 
		try: os.makedirs(OutputPath)
		except: 
			raise NameError("Cannot create given output directory '{0}'.".format(OutputPath))
			return False
	if (VHDLFilePath is None) or VHDLFilePath=="":
		raise HdlLibError("VHDLFilePath argument must not be empty (None or empty string). Given : '{0}'.".format(VHDLFilePath))
		return False
	try: 
		ModuleList=VHDLParser.ParseVHDL(FilePath=VHDLFilePath)
	except ParseError:
		logging.error("The VHDL file couldn't be parsed. Please correct the detected errors and try again.")
		return False
	
	Declarations = ""
	Content      = ""
	for Mod in ModuleList:
		# Create a folder for each module found-----------------------------------------------
		TBGenDir = os.path.join(OutputPath, Mod.Name)
		if not os.path.isdir(TBGenDir): 
			try: os.makedirs(TBGenDir)
			except: 
				logging.error("Unable to make directory '{0}'".format(TBGenDir));return False
		else: 
			while(1): 
				A=input("Directory '{0}' already exist. Remove it (y/n) ? ".format(TBGenDir));
				if A=='y': break; 
				elif A=='n': sys.exit(1)
				else: continue
			shutil.rmtree(TBGenDir)
			try: os.makedirs(TBGenDir)
			except: 
				logging.error("Unable to make directory '{0}'".format(TBGenDir));return False
				
		# Generate a SYNOPTIC PNG:----------------------------------------------------------------
		Graphics.Synoptic(Mod, TBGenDir)
		# Classify ports found:----------------------------------------------------------------
		ClockInputs=[]
		ClockEnables=[]
		ResetInputs=[]
		GPIO=[]
		AcqInputs=[]
		RAMInterface=False
		
		# Declare generics as constant in the testbench----------------------------------------
		Content+=HDLEditor.CommentSeparator(Length=50)
		Declarations+=HDLEditor.Comment("Declare generics as constant in the testbench")
		Content+=HDLEditor.CommentSeparator(Length=50)
		for PName, P in Mod.Params.items():
			Declarations+=P.HDLFormat().Declare(Constant=True, UnConstrained=False)
		
		# Get port information and declare signals for the testbench---------------------------
		Content+=HDLEditor.CommentSeparator(Length=50)
		Declarations+=HDLEditor.Comment("Declare '{0}' signals for the testbench".format(Mod.Name))
		Content+=HDLEditor.CommentSeparator(Length=50)
		ModulePorts=Mod.Ports.copy()
		print("------------------------------------------------")
		
		FuncDict={'Reset': ResetInputs, 'Clock' : ClockInputs, "Clock enable":ClockEnables, "GPIO": GPIO, "Acquisition":AcqInputs, "RAM interface" : GPIO, 'Rewritable parameter': GPIO}
		for PName, P in ModulePorts.items():
			# Ask user to define the function of each port-----------------------------------------------
			if P.GetFuncFromStdInput()=="RAM interface": RAMInterface=True
			if not P.Func in FuncDict: logging.error("Function '{0}' not in ['Reset', 'Clock', 'Clock enable', 'GPIO', 'Acquisition', 'RAM interface', 'Rewritable parameter']."); raise TypeError()
			FuncDict[P.Func].append(P)
			Declarations+=P.HDLFormat().Declare()

		print("------------------------------------------------")
			
		# List emulators--------------------------------------------------------------------
		EmuDict={'GPIO':[], 'GenericPattern':[],}
		ArraySizes={}
		Vars=VHDLParser.AlstomFunctionsMapping.copy()
		Vars.update(Mod.GetConstants())
		MainClockPeriod=ClockInputs[0].SpecialParameters['Period_ns']
		#-------------------
		for P in ResetInputs+ClockInputs+ClockEnables+GPIO:
			if P.Type=="logic": 
				if P.GetSize(Vars)==1:
					EmuDict['GPIO'].append(P.Name)
				else: 
					for i in range(P.GetSize(Vars=Vars)):
						EmuDict['GPIO'].append("{0}_{1}".format(P.Name, i))
			else: 
				if not (P.Type in ArraySizes):
					while(1):
						Answer=input("\tCould you provide the size of the array for type '{0}' ? ".format(P.Type))
						try: Answer=int(Answer);ArraySizes[P.Type]=Answer;break
						except: continue
				for i in range(P.GetSize(Vars)):
					for j in range(ArraySizes[P.Type]):
						EmuDict['GPIO'].append("{0}_{1}_{2}".format(P.Name, i, j))
		#-------------------
		for P in AcqInputs:
			if P.Type=="logic": 
				for i in range(P.GetSize(Vars=Vars)):
					EmuDict['GenericPattern'].append("{0}_{1}".format(P.Name, i))
			else: 
				if not (P.Type in ArraySizes):
					while(1):
						Answer=input("Could you provide the size of the array for type '{0}' ? ".format(P.Type))
						try: Answer=int(Answer);ArraySizes[P.Type]=Answer;break
						except: continue
				for i in range(P.GetSize(Vars)):
					for j in range(ArraySizes[P.Type]):
						EmuDict['GenericPattern'].append("{0}_{1}_{2}".format(P.Name, i, j))
		
		logging.info("Generate a TBGen files for entity '{0}'...".format(Mod.Name))
		# Add clock enable generators------------------------------------------------------
#		for i, Cke in enumerate(ClockEnables):
#			Content += HDLEditor.Process("ClockEnable_Proc{0}".format(i), SensitivList=[], Declarations="", Content=
#"""------------------------------------
#-- Clock generator for '{CkeName}'
#------------------------------------
#{CkeName} <= '0';
#wait for {ResetTime}; 
#loop 
#  wait for {Period1} ns; -- {CkePeriod} ns - {ClkPeriod} ns
#  wait until {ClkName}='1';
#  {CkeName} <= '1';
#  wait until {ClkName}='1';
#  {CkeName} <= '0';
#end loop;
#""".format(
#			           CkeName=Cke.Name, 
#			           ClkName=ClockInputs[0].Name, 
#			           ResetTime="2 us", 
#			           Period1=Cke.SpecialParameters['Period_ns']-ClockInputs[0].SpecialParameters['Period_ns'], 
#			           CkePeriod=Cke.SpecialParameters['Period_ns'],
#			           ClkPeriod=MainClockPeriod))
		
		# Generate the VHDL for emulator instanciation--------------------------------------
		# First instantiate the TBGen Scheduler
		Content+=HDLEditor.Instantiate("EmuScheduler_Inst", "Scheduler", Architecture=None, SignalDict={"semaphores":"ArraySemaphore","contSigs":"ArraycontSigs"}, GenericDict={"G_EmuName":'"emuCTRL   "',"G_CmdFileName":"STIMULI_CTRL","NbEmu":"NBEMU"}, Comment="TBGen controller", FromLib=None)
		
		if len(EmuDict['GPIO'])>0: 
			Content+= HDLEditor.Instantiate("emuGPIO_inst", "emuGPIO_TSA", Architecture=None, SignalDict={"semaphore": "ArraySemaphore(EMU_GPIO_IND)", "contSigs":"ArraycontSigs(EMU_GPIO_IND)", "gpio":"gpio1"}, GenericDict={"G_EmuName":'"emuGPIO   "', "G_CmdFileName":"STIMULI_GPIO", "nb_GPIO":"NB_GPIO"}, Comment="PATTERN_GENERATOR Emulator GPIO", FromLib='tb_gen')
		if len(EmuDict['GenericPattern'])>0: 
			ActualSigs=['Real{0}'.format(i) for i in range(16)]
			for A in ActualSigs: 
				ASig=HDLEditor.Signal(A)
				ASig.Type='real'
				Declarations+=ASig.Declare()
			SigDict=collections.OrderedDict(( ("semaphore","ArraySemaphore(EMU_PATTERN_GENERATOR_IND)"),("contSigs","ArraycontSigs(EMU_PATTERN_GENERATOR_IND)") ))
			for i in range(16) : SigDict['Pattern_{0}'.format(i)]='Real{0}'.format(i)
			Content+= HDLEditor.Instantiate("EmuPatternGenerator", "emuPattern_Generator", Architecture=None, SignalDict=SigDict, GenericDict={"G_EmuName":'"emuPatGen "',"G_CmdFileName":"STIMULI_PATTERN_GENERATOR"}, Comment="DUT instanciation", FromLib='')

			Content+=HDLEditor.CommentSeparator(Length=50)
			Content+=HDLEditor.Comment("Connect DUT ports with PATTERN_GENERATOR emulator signals")
			Content+=HDLEditor.CommentSeparator(Length=50)
			i=0
			for P in AcqInputs:
				if P.Type=='logic':
					Content+=HDLEditor.Assign(HDLEditor.Signal(P.Name, Direction="OUT"), HDLEditor.Signal("CONV_STD_LOGIC_VECTOR(integer(Real{0}), {1})".format(i, P.Size), Direction="IN"))
					i+=1
				else: 
					for j in range(P.GetSize(Vars=Vars)):
						Content+=HDLEditor.Assign(HDLEditor.Signal("{0}({1})".format(P.Name, j), Direction="OUT"), HDLEditor.Signal("CONV_STD_LOGIC_VECTOR(integer(Real{0}), {1})".format(j, ArraySizes[P.Type]), Direction="IN"))
						i+=1
		
		# Setup connexion of DUT ports with GPIO signals------------------------------------
		Content+=HDLEditor.CommentSeparator(Length=50)
		Content+=HDLEditor.Comment("Connect DUT ports with GPIO emulator signals")
		Content+=HDLEditor.CommentSeparator(Length=50)
		for P in ResetInputs+ClockInputs+ClockEnables+GPIO:
			if P.Type=='logic' or P.Type=='numeric':
				if P.GetSize(Vars)==1:
					if P.Direction=='IN':
						Content+=HDLEditor.Assign(HDLEditor.Signal("{0}".format(P.Name), Direction="OUT"), HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}")))""".format(P.Name), Direction="IN"))
					else:
						Content+=HDLEditor.Assign(HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}")))""".format(P.Name), Direction="IN"), HDLEditor.Signal("{0}".format(P.Name), Direction="OUT"))
				else: 
					for i in range(P.GetSize(Vars=Vars)):
						if P.Direction=='IN':
							Content+=HDLEditor.Assign(HDLEditor.Signal("{0}({1})".format(P.Name,i), Direction="OUT"), HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}_{1}")))""".format(P.Name,i), Direction="IN"))
						else:
							Content+=HDLEditor.Assign(HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}_{1}")))""".format(P.Name,i), Direction="IN"), HDLEditor.Signal("{0}({1})".format(P.Name,i), Direction="OUT"))
			else: 
				for i in range(P.GetSize(Vars=Vars)):
					for j in range(ArraySizes[P.Type]):
						if P.Direction=='IN':
							Content+=HDLEditor.Assign(HDLEditor.Signal("{0}({1})({2})".format(P.Name,i,j), Direction="OUT"), HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}_{1}_{2}")))""".format(P.Name,i,j), Direction="IN"))
						else:
							Content+=HDLEditor.Assign(HDLEditor.Signal("""gpio1(t_gpio'pos(t_gpio'value("{0}_{1}_{2}")))""".format(P.Name,i,j), Direction="IN"), HDLEditor.Signal("{0}({1})({2})".format(P.Name,i,j), Direction="OUT"))
		
		# Generate the VHDL for DUT instanciation/déclaration--------------------------------
		Declarations+=HDLEditor.Component(Mod.Name, Generics=[G.HDLFormat() for N,G in Mod.Params.items()], Ports=[P.HDLFormat() for N,P in Mod.Ports.items()], Comments="DUT")
		Content+=HDLEditor.Instantiate("UUT_"+Mod.Name, Mod.Name, Architecture=None, SignalDict={N:P.HDLFormat() for N,P in Mod.Ports.items()}, GenericDict={N:P.HDLFormat() for N,P in Mod.Params.items()}, Comment="DUT instanciation", FromLib='')
		
		# Generate the template for results checking-----------------------------------------
		for Pname, P in Mod.Ports.items():
			if P.Direction=="OUT":
				Content+="\n-- Here results check statements... not available yet."
				
		# Specific declarations--------------------------------------------------------------
		Declarations+=TBGenDeclarations()
		Content="""
  -----------------------------------
  ----- Testbench title display -----
  -----------------------------------
  p_mess("          ", MSG_NULL, string'(" "));
  p_mess("          ", MSG_NULL, string'("------------------------------------"));
  p_mess("          ", MSG_NULL, string'("  " & title));
  p_mess("          ", MSG_NULL, string'("------------------------------------"));
  p_mess("          ", MSG_NULL, string'(" "));
"""+Content
		
		
		# Finally generate the VHDL testbench-----------------------------------------------
		Generics=[
			HDLEditor.Signal("title", Type="string", InitVal='"Unitary test - {0}.vhd"'.format(Mod.Name), CurValue='"Unitary test - {0}.vhd"'.format(Mod.Name)),
			HDLEditor.Signal("scenario", Type="string", InitVal='"{0}.tbu_{0}"'.format(Mod.Name), CurValue='"{0}.tbu_{0}"'.format(Mod.Name)),
			HDLEditor.Signal("mode", Type="string", InitVal='"ut"', CurValue='"ut"'),
			HDLEditor.Signal("clkperiod", Type="time", InitVal='10.000 ns', CurValue='10.000 ns'),
			]
		with open(os.path.join(TBGenDir, "tbu_{0}.vhd".format(Mod.Name)), 'w') as VhdlFile:
			# First add the DUT (mod) to an empty entity----------------------------------------
			VhdlFile.write("""
---------------------------------------------------------------------------------------------------
-- Company       : Alstom ADM
-- Site          : Villeurbanne
----------------------------------------------------------------------------------------------------
-- Title         : TSA
-- Project       : AGATE4C
----------------------------------------------------------------------------------------------------
-- File          : tbu_{Module}.vhd
-- Author        : {Author}
-- Created       : {Date}
-- Last modified : {Date}  
-- Standard      : VHDL'93
----------------------------------------------------------------------------------------------------
-- Description: Unitary testbench of module {Module}.vhd
--
----------------------------------------------------------------------------------------------------
-- Copyright (c) {Year} ALSTOM-TRANSPORT
----------------------------------------------------------------------------------------------------
-- Modification History    :
----------------------------------------------------------------------------------------------------
-- Date        | Author         | Changes made
----------------------------------------------------------------------------------------------------
-- {Date}  | {Author} | Created
----------------------------------------------------------------------------------------------------
""".format(Author=USER_NAME, Module=Mod.Name, Date=datetime.datetime.now().strftime("%d/%m/%Y"), Year=datetime.datetime.now().strftime("%Y")))# Commented Header 
			VhdlFile.write(HDLEditor.Libraries(LibList=["ieee",]))
			VhdlFile.write(HDLEditor.Packages(Library="ieee", PackageList=["std_logic_1164", "std_logic_arith", "std_logic_unsigned", "math_real"]))
			VhdlFile.write(HDLEditor.Libraries(LibList=["std",]))
			VhdlFile.write(HDLEditor.Packages(Library="std", PackageList=["textio",]))
			VhdlFile.write(HDLEditor.Libraries(LibList=["ees",]))
			VhdlFile.write(HDLEditor.Packages(Library="ees", PackageList=["text_util",]))
			VhdlFile.write(HDLEditor.Libraries(LibList=["tb_gen",]))
			VhdlFile.write(HDLEditor.Packages(Library="tb_gen", PackageList=["conversions", "pack_emu_gen", "emuGPIO_TSA_pkg", "emulators_pkg"]))
			VhdlFile.write(HDLEditor.Libraries(LibList=["lib_work",]))
			VhdlFile.write(HDLEditor.Packages(Library="lib_work", PackageList=["pkg_util","pkg_type"]))
			VhdlFile.write(HDLEditor.Entity(Name="tbu_{0}".format(Mod.Name), Generics=Generics, Ports=[], Comments="Empty entity"))
			VhdlFile.write(HDLEditor.Architecture("testbench", "tbu_{0}".format(Mod.Name), Declarations=Declarations, Content=Content, Comments="Automatically generated by SetupTBGen.py (see Matthieu Payet)"))
			
	
		#------------------------------------------------------------------------------------
		# Generate the scenario
		#------------------------------------------------------------------------------------
		with open(os.path.join(TBGenDir, "{0}.tbu_{0}.scru".format(Mod.Name)), 'w') as ScenarioFile:
			ScenarioFile.write("""
##--------------------------------------------------------------------------------
##-- Company       : ALSTOM ADM
##-- Site          : Villeurbanne
##--------------------------------------------------------------------------------
##-- Title         : TSA
##-- Project       : AGATE4C
##--------------------------------------------------------------------------------
##-- File          : {Module}.tbu_{Module}.scru
##-- Author        : {Author}
##-- Created       : {Date} 
##-- Last modified : {Date} 
##-- Standard      : VHDL'93
##--------------------------------------------------------------------------------
##-- Description   : UNITARY TEST for module {Module}.vhd
##--  
##--------------------------------------------------------------------------------
##-- Copyright (c) {Year} ALSTOM-TRANSPORT
##-------------------------------------------------------------------------------
##-- Modification History :
##-- ----------------------------------------------------------------------------
##-- Date        | Author         | Changes made
##-- ----------------------------------------------------------------------------
##-- {Date}  | {Author} | Created
##-- ----------------------------------------------------------------------------

################################
#Define Emulators declaration
################################
define EMULATOR_SPEC Scheduler Scheduler
define EMULATOR_SPEC GPIO emuGPIO_TSA
define EMULATOR_SPEC PATTERN_GENERATOR emuPattern_Generator

########################################################################################################################
# Display configuration
########################################################################################################################
define FILE FILE_REPORT ./files_reports/{Module}.txt
define REPORT File_Report 
Scheduler SET_AFF NOTE FALSE FALSE
Scheduler SET_AFF WARNING TRUE TRUE
ALL WAIT ALL
GPIO INIT_GPIO

GPIO COMMENT  "##########################################################################################"
GPIO COMMENT  "##################### TEST CASE MODULE {Module}.vhd  ########################"
GPIO COMMENT  "##########################################################################################"
GPIO COMMENT  " " """.format(Author=USER_NAME, Module=Mod.Name, Date=datetime.datetime.now().strftime("%d/%m/%Y"), Year=datetime.datetime.now().strftime("%Y")))
			Stage=1
			Step=1
			#-Setup acquisition signals---------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Setup acquisition signals:") );Stage+=1;Step=1
			ScenarioFile.write(ScenarioComment("Generate sinus waveforms from the 'pattern generator' emulator"))
			ScenarioFile.write("\n# SINUS    SELECT_OUTPUT FREQ_ECH OFFSET FREQUENCY AMPLITUDE DELAY_NS")
			
			i=0
			for P in AcqInputs:
				if P.Type=='logic':
					ScenarioFile.write("\nPATTERN_GENERATOR SINUS {Index} {SamplingFreq} {Offset} {Freq} {Amplitude} {Delay}".format(Index=i, SamplingFreq=1000000, Offset=0, Freq=i*1000+1000, Amplitude=65530, Delay=2000))
					i+=1
				else: 
					for j in range(P.GetSize(Vars=Vars)):
						ScenarioFile.write("\nPATTERN_GENERATOR SINUS {Index} {SamplingFreq} {Offset} {Freq} {Amplitude} {Delay}".format(Index=i, SamplingFreq=1000000, Offset=0, Freq=i*1000+1000, Amplitude=65530, Delay=2000))
						i+=1
			ScenarioFile.write( ScenarioStage(Stage, "Generate clocks and resets :") );Stage+=1;Step=1
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStep(Stage, Step, "Set clocks + clock enables :") );Step+=1
			for Clk in ClockInputs:
				ScenarioFile.write( ScenarioComment("Clock period : {0} ns ({1:.4} Hz)".format(Clk.SpecialParameters['Period_ns'], float(1000000000.0/(Clk.SpecialParameters['Period_ns'])))) )
				ScenarioFile.write(ScenarioSetClk(Sig=Clk, Period_ns=Clk.SpecialParameters['Period_ns']))
			# Add clock enable generators------------------------------------------------------
			for i, Cke in enumerate(ClockEnables):
				ScenarioFile.write(ScenarioSetClkEnable(Sig=Cke, RefClock=Cke.SpecialParameters['MainClock'], Divider=Cke.SpecialParameters['Divider']))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStep(Stage, Step, "Assert and de-assert resets :") );Step+=1
			for Rst in ResetInputs:
				ScenarioFile.write(ScenarioSet(Rst, 1, ArraySizes))
			ScenarioFile.write(ScenarioWait("1 us", Comment="Reset duration : 1 us"))
			for Rst in ResetInputs:
				ScenarioFile.write(ScenarioSet(Rst, 0, ArraySizes))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Setup input GPIOs and configurable parameters:") );Stage+=1;Step=1
			for i,P in enumerate(GPIO):
			  if P.Direction=='IN':
				  P._UsedParams.update(Vars)
				  ScenarioFile.write(ScenarioSet(P, 0, ArraySizes))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Simulate for 100 us:") );Stage+=1;Step=1
			if RAMInterface is True:
				ScenarioFile.write( ScenarioStep(Stage, Step, "Write data to memory:") );Step+=1
				RAM_Data=None
				RAM_Addr=None
				RAM_Write=None
				for i,P in enumerate(GPIO):
					if not ('RAMFunction' in P.SpecialParameters): continue
					if P.SpecialParameters['RAMFunction']=='data': # Data
						RAM_Data = P
					elif P.SpecialParameters['RAMFunction']=='address': # Address
						RAM_Addr = P
					elif P.SpecialParameters['RAMFunction']=='write': # Write bit
						RAM_Write = P
					else:
						logging.error("Wrong value '{1}' for RAM Function of signal '{0}'.".format(TBGenDir, P.SpecialParameters['RAMFunction'])); 
						return False
				
				if None in [RAM_Data, RAM_Addr, RAM_Write]: 
					logging.error("Missing functions for RAM interface : RAM_Data={0}, RAM_Addr={1}, RAM_Write={2}.".format(TBGenDir, P.SpecialParameters['RAMFunction']));
					return False
				#------------------- RAM LOADING SCENARIO -------------------
				RAM_Data._UsedParams.update(Vars)
				RAM_Addr._UsedParams.update(Vars)
				RAM_Write._UsedParams.update(Vars)
				ScenarioFile.write(ScenarioComment("RAM signals reset"))
				ScenarioFile.write(ScenarioSet(RAM_Data, 0, ArraySizes))
				ScenarioFile.write(ScenarioSet(RAM_Addr, 0, ArraySizes))
				ScenarioFile.write(ScenarioSet(RAM_Write, 0, ArraySizes))
				ScenarioFile.write(ScenarioWait("50 ns", Comment="Wait before loading memory"))
				ScenarioFile.write(ScenarioComment("Start memory loading"))
				ScenarioFile.write(ScenarioSet(RAM_Write, 1, ArraySizes))
				AddrSize=float(RAM_Addr.GetSize(Vars))
				AddrRange=int(math.pow(AddrSize,2.0))
				for i in range(AddrRange):
					ScenarioFile.write(ScenarioSet(RAM_Data, i*10, ArraySizes))
					ScenarioFile.write(ScenarioSet(RAM_Addr, i, ArraySizes))
					ScenarioFile.write(ScenarioWait("{0} ns".format(MainClockPeriod), Comment="1 clock cycle"))
				ScenarioFile.write(ScenarioComment("RAM signals reset"))
				ScenarioFile.write(ScenarioSet(RAM_Write, 0, ArraySizes))
				ScenarioFile.write(ScenarioWait("10 ns"))
				ScenarioFile.write(ScenarioSet(RAM_Data, 0, ArraySizes))
				ScenarioFile.write(ScenarioSet(RAM_Addr, 0, ArraySizes))
				ScenarioFile.write(ScenarioWait("20 ns", Comment="Wait after memory is loaded"))
				
				ScenarioFile.write( ScenarioStep(Stage, Step, "Wait for simulation run") );Step+=1 # If no RAM => no RAM section => no simu run section
			ScenarioFile.write(ScenarioWait("1000 us", Comment="run 1000 us"))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Setup checkers:") );Stage+=1;Step=1
			for Sig in GPIO:
				if Sig.Direction=="OUT":
					Sig._UsedParams.update(Vars)
					ScenarioFile.write(ScenarioCheck(Sig, 1, ArraySizes))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Assert resets:") );Stage+=1;Step=1
			for Rst in ResetInputs:
				ScenarioFile.write("\nGPIO SET {Name} 1".format(Name=Rst.Name))
			ScenarioFile.write(ScenarioWait("1 us"))
			#------------------------------------------------------------------------
			ScenarioFile.write( ScenarioStage(Stage, "Scenario result final display:") );Stage+=1;Step=1
			ScenarioFile.write( "\nALL WAIT ALL" )
			ScenarioFile.write( "\nScheduler PRINT_STATUS" )
			ScenarioFile.write( "\nScheduler END_TEST" )
			ScenarioFile.write( "\n " )
			ScenarioFile.write( "\n " )
			
		logging.info("TBGen files for the entity '{0}' successfully generated.".format(Mod.Name))
		
		# Display the port names to be added to the emulator packages-----------------------------
		print("Now you can add the folling port names to the GPIO emulator package:")
		
		for P in ResetInputs+ClockInputs+ClockEnables+GPIO:
			if P.Type=="logic":
				SIZE=P.GetSize(Vars)
				if SIZE==1:
					print("\t {0},".format(P.Name))
				else:
					for i in range(SIZE):
						print("\t {0}_{1},".format(P.Name, i))
			else:
				for i in range(P.GetSize(Vars)):
					for j in range(ArraySizes[P.Type]):
						print("\t {0}_{1}_{2},".format(P.Name, i, j))
		i=0
		for P in AcqInputs:
			SIZE=P.GetSize(Vars)
			if P.Type=='logic':
				print("\t {0}_{1},".format(P.Name, i))
				i+=1
			else: 
				for n in range(SIZE):
					print("\t {0}_{1},".format(P.Name, n))
				i+=SIZE
		
		return True

#====================================================================	
def ScenarioStage(Stage, Description):
	"""
	Return a comment string for TBGen scenario describing a new stage.
	"""
	return """
GPIO COMMENT  "##########################################################################################"
GPIO COMMENT  "# {Stage}. {Desc}"
GPIO COMMENT  "##########################################################################################"  """.format(Stage=Stage, Desc=Description)

#====================================================================	
def ScenarioStep(Stage, Step, Description):
	"""
	Return a comment string for TBGen scenario describing a new Step.
	"""
	return """
GPIO COMMENT  "---------------------------------------------"
GPIO COMMENT  "# {Stage}.{Step} {Desc}"
GPIO COMMENT  "---------------------------------------------" """.format(Stage=Stage, Step=Step, Desc=Description.replace('\n',' / '))

#====================================================================	
def ScenarioComment(Comment):
	"""
	Return a comment string for simple TBGen scenario comment.
	"""
	return '\nGPIO COMMENT  "# {Comment}"'.format(Comment=Comment)

#====================================================================	
def ScenarioSet(Sig, Val, ArraySizes):
	"""
	Return a string of scenario GPIO SET command for TBGen.
	"""
	SetString=''
	SIZE=Sig.GetSize()
	if Sig.Type=="logic":
		if SIZE==1:
			SetString+="\nGPIO SET {Name} {Value}".format(Name=Sig.Name, Value=0 if Val==0 else 1)
		else:
			SetString+="\nGPIO SET_VECT {Name}_{MSb} {Name}_0 {Value:#010x}".format(Name=Sig.Name, MSb=SIZE-1, Value=Val)
	else:
		for j in range(SIZE):
			SetString+="\nGPIO SET_VECT {Name}_{Index}_{MSb} {Name}_{Index}_0 {Value:#010x}".format(Name=Sig.Name, Index=j, MSb=ArraySizes[Sig.Type]-1, Value=Val)
	return SetString

#====================================================================	
def ScenarioCheck(Sig, Val, ArraySizes):
	"""
	Return a string of scenario GPIO CHECK command for TBGen.
	"""
	CheckString=''
	if Sig.Type=="logic":
		SIZE=Sig.GetSize()
		if SIZE==1:
			CheckString+="\nGPIO CHECK {Name} {Value}".format(Name=Sig.Name, Value=0 if Val==0 else 1)
		else:
			CheckString+="\nGPIO CHECK_VECT {Name}_{MSb} {Name}_0 {Value:#010x}".format(Name=Sig.Name, MSb=SIZE-1, Value=Val)
	else:
		for j in range(ArraySizes[Sig.Type]):
			CheckString+="\nGPIO CHECK_VECT {Name}_{MSb} {Name}_0 {Value:#010x}".format(Name=Sig.Name, MSb=SIZE-1, Value=Val)
	return CheckString
	
#====================================================================
def ScenarioSetClk(Sig, Period_ns):
	"""
	Return a string of clock generator command for TBGen.
	"""
	return "\nGPIO SET_CLK {Name} {HalfPeriod_ps} {HalfPeriod_ps} 0".format(Name=Sig.Name, HalfPeriod_ps=int((Period_ns/2)*1000))

#====================================================================
def ScenarioSetClkEnable(Sig, RefClock, Divider):
	"""
	Return a string of clock enable generator command for TBGen.
	"""
	return "\nGPIO SET_CLK_EN {Name} {RefClock} {Divider}".format(Name=Sig.Name, RefClock=RefClock, Divider=Divider)

#====================================================================
def ScenarioWait(Time, Comment=None):
	"""
	Return a comment string for simple TBGen scenario comment.
	"""
	if not (Comment is None):
		return ScenarioComment(Comment)+'\nGPIO WAIT {Time}'.format(Time=Time)
	else:
		return '\nGPIO WAIT {Time}'.format(Time=Time)
#====================================================================
def TBGenDeclarations():
	"""
	Return a comment string for simple TBGen scenario comment.
	"""
	return """
-- ########### TBGEN signals ###########################################################
type EMU_INDEXES is (
CONTROLLER,
-- Add here generic emulators you need in your testbench
EMU_GPIO,
EMU_PATTERN_GENERATOR
);

-- For each emulator (except controller), use following syntax to get its index in the type (to update)
constant EMU_GPIO_IND              : integer := EMU_INDEXES'pos(EMU_GPIO);
constant EMU_PATTERN_GENERATOR_IND : integer := EMU_INDEXES'pos(EMU_PATTERN_GENERATOR);

-- NB_EMU should take the value of the highest index of the type (to update)
constant NBEMU : integer := EMU_PATTERN_GENERATOR_IND;

-- Semaphores useful for TBGEN emulators synchronization with scheduler
signal ArraySemaphore : t_ArraySemaphore(NBEMU downto 1);
signal ArraycontSigs  : std_logic_vector(NBEMU downto 1) := (others => '1');

-- Stimulis files paths (to update)
constant STIMULI_CTRL     : string := "./files_stimulis/" & scenario & "_" & mode & "/Scheduler.txt";
constant STIMULI_GPIO     : string := "./files_stimulis/" & scenario & "_" & mode & "/GPIO.txt";
constant STIMULI_PATTERN_GENERATOR     : string := "./files_stimulis/" & scenario & "_" & mode & "/PATTERN_GENERATOR.txt";

-- GPIO signals, directly fed by data customized in emuGPIO_TSA_pkg
signal gpio1 : std_logic_vector(NB_GPIO-1 downto 0)   := gpio_init;

"""






