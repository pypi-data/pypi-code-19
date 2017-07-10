#!/usr/bin/python

import os
import re
import argparse, logging, sys, os
import datetime
import getpass
import shlex
import shutil
import string
import tempfile

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
from HdlLib.Utilities import Timer, Misc
from HdlLib.Utilities.RemoteOperations import RemoteOperations
from HdlLib.Utilities import SafeRun

class FpgaOperations(RemoteOperations):
	#------------------------------------------------------------------------------
	def __init__(self, RemoteSubFolder="UnknownTool"):
		"""
		Environment variables settings
		"""
		RemoteOperations.__init__(self,	RemoteSubFolder=RemoteSubFolder)
#		self.HwLibPath  = HwLibPath
	#------------------------------------------------------------------------------
	def Synthesize(self, HwModel, TopName, SourceList, ConstraintFile, SrcDirectory, OutputPath, RscEstimation=False): 
		"""
		Execute a_safe_run.exe remotely with synthesis scripts. 
			* Source paths are given relatively to SrcDirectory
		"""
		ResultFilesDict={}
		###############################################################################
		#                              100% LOCAL PART
		###############################################################################
#		AdacsysHome=os.path.normpath(os.path.expanduser("~/.adacsys"))
		LocalSynthesisPath=os.path.abspath(OutputPath)
		if not os.path.isdir(LocalSynthesisPath): os.makedirs(LocalSynthesisPath)
		#----------------------------------------------------
		if RscEstimation is True:
			SynthesisScript=HwModel.GetRscEstimationScript() # Stops after mapping stage
		else:
			SynthesisScript=HwModel.GetSynthesisScript()
		if SynthesisScript is None: 
			logging.error("No synthesis script found in configuration file. Aborted.")
			return ResultFilesDict
		elif not os.path.isfile(SynthesisScript): 
			logging.error("Synthesis script found in configuration file ('{0}') is not a proper file. Synthesis aborted.".format(SynthesisScript))
			return ResultFilesDict
		shutil.copy(SynthesisScript, LocalSynthesisPath)
		
		# Create two files : a script and a source list.
		SynthesisScript=os.path.join(LocalSynthesisPath, os.path.basename(SynthesisScript))
		SourcesFileName = HwModel.GetSourcesFileName()
		if SourcesFileName is None: 
			logging.error("No SourcesFileName option found in configuration file. Synthesis aborted.")
			return ResultFilesDict
		LocalSourceList=os.path.join(LocalSynthesisPath, SourcesFileName)
		#----------------------------------------------------
		if self.RemoteHost:
			SynthesisPath="FpgaSynthesis/{0}_Synthesis_{1}".format(TopName, Timer.TimeStamp())
			TargetSrcDirectory='/'.join([SynthesisPath, 'src'])
		else:
			SynthesisPath=LocalSynthesisPath
			TargetSrcDirectory=SrcDirectory
			if not os.path.isdir(SynthesisPath): os.makedirs(SynthesisPath)
		
		#----------------------------------------------------
		# Create a source-list file from template
		#----------------------------------------------------
		SLT=HwModel.GetSourcesTemplate()
		if SLT is None: 
			logging.error("No template found for source list file. Aborted.")
			return ResultFilesDict
		SourceListTemplate=string.Template(SLT)
		LanguageDict={".vho":"vhdl", ".vhd":"vhdl", ".vhdl":"vhdl", ".vh":"verilog", ".v":"verilog", ".xci": "ip", ".xdc":"xdc"}
		
		ConstrSrcPath=os.path.relpath(ConstraintFile, os.path.abspath(SrcDirectory))
		with open(LocalSourceList, "w+") as SourceListFile:
			for RelSourcePath in SourceList+[ConstrSrcPath,]:
#				print(RelSourcePath)
				Extension="."+RelSourcePath.split('.')[-1]
				try: Language = LanguageDict[Extension]
				except: 
					logging.error("Unknown extension of source '{0}'".format(RelSourcePath))
#					input()
					continue
				Library = "work"

				AbsSrcPath = os.path.normpath(os.path.join(TargetSrcDirectory, RelSourcePath))
				PathFromSynthesis  = os.path.relpath(AbsSrcPath, SynthesisPath)
				Substitutes={
					"Library"  : Library,
					"Language" : Language,
					"Source"   : PathFromSynthesis,
				}
				SourceListFile.write('\n'+SourceListTemplate.safe_substitute(Substitutes))
		#----------------------------------------------------
		# Setup SafeRun variables 
		#----------------------------------------------------
		SetupVars={
			"FPGA"            : HwModel.GetFPGA(),
			"TOPENTITY"       : TopName,
			"CONSTRAINTS"     : '"{0}"'.format("/".join([TargetSrcDirectory, RelSourcePath,])),
			"OUTPUTPATH"      : SynthesisPath,
			"SRCLIST"         : "/".join([SynthesisPath, os.path.basename(LocalSourceList)]) if self.RemoteHost else LocalSourceList,
			}
		Templates=HwModel.GetTemplates(SetupVars, SynthesisPath if self.RemoteHost is False else LocalSynthesisPath)
		#----------------------------------------------------
		# Create a a_safe_run setup script
		#----------------------------------------------------
		SetupSafeRun="/".join([LocalSynthesisPath, "SafeRun_SynthesisSetup.run"])
#		MaxNameWidth=max(*list(map(len, list(SetupVars.keys()))))+2
		with open(SetupSafeRun, "w+") as SetupFile:
			for VarName, VarValue in SetupVars.items():
				SetupFile.write(('\n{0}={1}').format(VarName, VarValue))#: <'+str(MaxNameWidth)+'
			SetupFile.write('\n\n')
			
		#----------------------------------------------------
		# Now execute synthesis flow script
		#----------------------------------------------------
#		if not os.path.isdir(OutputPath): os.makedirs(OutputPath)
		
#		def CleanOutput(): # Clean output directory
#			try:  os.remove(SynthesisScript) 
#			except:  logging.warning("Unable to remove '{0}'".format(SynthesisScript))
		
		###############################################################################
		if self.RemoteHost:
			#----------------------------------------------------
			# Copy scripts to remote host
			#----------------------------------------------------
			DirList=[TargetSrcDirectory,] # To be created
			SetupFileDict={ # Files to be moved
				SetupSafeRun    : os.path.basename(SetupSafeRun),
				ConstraintFile  : "/src/"+os.path.basename(ConstraintFile),
				SynthesisScript : os.path.basename(SynthesisScript),
				LocalSourceList : os.path.basename(LocalSourceList),
				}
			SrcDict={}
			for S in SourceList:
				AbsSrcPath=os.path.abspath(os.path.join(SrcDirectory, S))
				SrcDict[AbsSrcPath]=S
			for T in Templates:
				SetupFileDict[os.path.abspath(T)]=os.path.basename(T)
				
			#----------------------------------------------------
#			if self.SendPaths(DirList, SetupFileDict) is False: return None
			if self.CreateHostDir(DirList=DirList) is False: return ResultFilesDict
			if self.SendPathsRelative(FileDict=SetupFileDict, HostAbsPath=SynthesisPath) is False: return ResultFilesDict
			if self.SendPathsRelative(FileDict=SrcDict, HostAbsPath=TargetSrcDirectory) is False: return ResultFilesDict
			#----------------------------------------------------
			
			RemoteSetupSafeRun    = '/'.join([SynthesisPath, os.path.basename(SetupSafeRun)])
			RemoteSynthesisScript = '/'.join([SynthesisPath, os.path.basename(SynthesisScript)])
			
			Success=self.RemoteRun(
				Command='chmod 777 {SynthesisScript}'.format(SynthesisScript=RemoteSynthesisScript),
				ScriptsToSource=[HwModel.GetSetupEnvScript(),], 
				abort_on_prompts='True', warn_only=True
				)
#			SetupEnvScript=HwModel.GetSetupEnvScript()
			Success=self.RemoteRun(
				Command='./{SynthesisScript}'.format(SetupSafeRun=RemoteSetupSafeRun, SynthesisScript=os.path.basename(RemoteSynthesisScript)),
				ScriptsToSource=[],
				FromDirectory=SynthesisPath,
				abort_on_prompts='True', warn_only=True
				)
			if Success:
				# Fetch result files (bitstream, MAP report and PAR report)
				if RscEstimation is True: 
					RemoteResultFilesDict={}
				else:# Else fetch binary file
					BitStreamExt=HwModel.GetBitStreamExt()
					if BitStreamExt is None: return ResultFilesDict
					BitStreamPath="/".join([SynthesisPath, "{0}{1}".format(TopName, BitStreamExt)])
					RemoteResultFilesDict={'Binary':BitStreamPath}
				
				MapReportExt=HwModel.GetMapReportExt()
				if MapReportExt is None: return RemoteResultFilesDict
				ParReportExt=HwModel.GetParReportExt()
				if ParReportExt is None: return RemoteResultFilesDict
				MapReportPath="/".join([SynthesisPath, "{0}{1}".format(TopName, MapReportExt)])
				ParReportPath="/".join([SynthesisPath, "{0}{1}".format(TopName, ParReportExt)])
				
				RemoteResultFilesDict.update({'PlaceReport':MapReportPath, 'RouteReport':ParReportPath})
				ResultFilesDict={}
#				print("TopName", TopName)
				for FileType, ResultFilePath in RemoteResultFilesDict.items():
#					print("Fetch", ResultFilePath, "from host")
					if not self.DownloadFromHost(HostPath=ResultFilePath, LocalPath=LocalSynthesisPath):
						return {}
					ResultFilesDict[FileType]=os.path.join(LocalSynthesisPath, os.path.basename(ResultFilePath))
#					get(remote_path="/".join([SynthesisPath, "{0}-par_pad.csv".format(TopName)]), local_path=LocalSynthesisPath)
#					get(remote_path="/".join([SynthesisPath, "{0}_pad.txt".format(TopName)]), local_path=LocalSynthesisPath)
#					get(remote_path="/".join([SynthesisPath, "par_usage_statistics.html"]), local_path=LocalSynthesisPath)
				logging.info("'{0}' binary generation success.".format(TopName))
				# Now remove remote directory
				self.RemoteRun(Command='rm -rf {SynthesisPath}'.format(SynthesisPath=SynthesisPath), abort_on_prompts='True', warn_only=True)
				return ResultFilesDict
			else:
				# Now remove remote directory
				self.RemoteRun(Command='rm -rf {SynthesisPath}'.format(SynthesisPath=SynthesisPath), abort_on_prompts='True', warn_only=True)
				
				logging.error("'{0}' binary generation failure.".format(TopName))
				return ResultFilesDict
		else: # Local synthesis
			with Misc.cd(SynthesisPath):
				if not SafeRun.SafeRun(CaseInsensitive=not sys.platform.startswith('win'), CommandFiles=[SetupSafeRun, SynthesisScript]):
					logging.info("'{0}' binary generation success.".format(TopName))
					BitStreamExt=HwModel.GetBitStreamExt()
					if BitStreamExt is None: return ResultFilesDict
					BitStreamPath=os.path.join(SynthesisPath, "{0}.{1}".format(TopName, HwModel.GetBinaryExtension()))
					ResultFilesDict={'Binary':BitStreamPath}
					return ResultFilesDict
				else:
					logging.error("'{0}' binary generation failure.".format(TopName))
					return ResultFilesDict
		
		#----------------------------------------------------
	
#=======================================================================
def Synthesize(HwModel, ConstraintFile, Module, SrcDirectory, OutputPath="./FpgaSynthesis", RscEstimation=False, RemoteHost=None):
	"""
	Synthesize module design onto HwModel architecture with ConstraintFile as pad assignment constraints.
	"""
	# Launch [remote] synthesis flow
#	print("[Synthesize] SourceList:\n", '\n'.join(Module.Sources["RTL"]))
#	input("Synthesize / RscEstimation={0}".format(RscEstimation))
	#---------
	LocalUser=getpass.getuser()
	#---------
#	if HwLibPath is None: 
#		logging.error("[HdlLib.Utilities.FpgaOperations.Synthesize] Hardware library path (HwLibPath) must be defined. Exit.")
#		return None #sys.exit(1)
	FpgaFlow=FpgaOperations(RemoteSubFolder="{0}-{1}".format(LocalUser, Timer.TimeStamp()))
	FpgaFlow.SetRemoteHost(RemoteHost)
	
	#-------------------------
	# Fetch Synthesis source(s)
	#-------------------------
	EntityName, TopPath=Module.GetTop()
	#-------------------------
	# Synthesize !
	#-------------------------
	SourceList=Module.Sources["RTL"] # Module.GetSources(Synthesizable=True, Constraints=None, IsTop=False, IgnorePkg=True)

	ConstrSourceList=Module.GetLastCreatedInstance().GatherConstraintSources(FromInst=Module.Name)
	
	RelSources=[os.path.relpath(S, SrcDirectory) for S in SourceList+ConstrSourceList]
	ResultFilesDict=FpgaFlow.Synthesize(
				HwModel=HwModel, 
				TopName=EntityName, 
				SourceList=RelSources,  
				ConstraintFile=ConstraintFile, 
				SrcDirectory=SrcDirectory, 
				OutputPath=OutputPath,
				RscEstimation=RscEstimation
				)
	if RemoteHost: FpgaFlow.Disconnect()
	return ResultFilesDict
#	sys.exit(0)
	
#=======================================================================
def Upload(HwModel, BinaryPath, ScanChainPos=1, Remote=True):
	"""
	Upload specified binary to FPGA on HwModel.
	"""
	if BinaryPath is None or not os.path.isfile(str(BinaryPath)):
		logging.error("No binary specified for upload.")
		return False
		
	#----------------------------------------------------
	# Create a temporary directory for the upload scripts
	#----------------------------------------------------
	UploadDirPath=tempfile.mkdtemp(prefix='Upload_{0}_'.format(Timer.TimeStamp()))#, dir=AdacsysHome)
	
	#----------------------------------------------------
	# Fetch Upload script and copy to Upload directory
	#----------------------------------------------------
	UploadScript=HwModel.GetUploadScript(UploadDirPath)
	if UploadScript is None: 
		logging.error("No upload script found. Aborted.")
		return None
#	shutil.copy(UploadScript, UploadDirPath)
#	UploadScript=os.path.join(UploadDirPath, os.path.basename(UploadScript))
	
	#----------------------------------------------------
	# Setup SafeRun variables 
	#----------------------------------------------------
	SetupVars={
		"SCANCHAINPOS" : str(ScanChainPos),
		"BITSTREAM"    : str(BinaryPath),
		}
	UploadSetupFile=HwModel.GetUploadSetupFile(SetupVars, UploadDirPath)
	if UploadSetupFile is None: 
		logging.error("Upload Setup File not found. Aborted.")
		return None
		
#	shutil.copy(UploadSetupFile, UploadDirPath)
#	UploadSetupFile=os.path.join(UploadDirPath, os.path.basename(UploadSetupFile))
	SetupVars["UPLOAD_SETUP_SCRIPT"]="/".join([UploadDirPath, os.path.basename(UploadSetupFile)]) if Remote else os.path.abspath(UploadSetupFile)
	
	#----------------------------------------------------
	# Create a a_safe_run setup script
	#----------------------------------------------------
	SetupSafeRun="/".join([UploadDirPath, "SafeRun_UploadSetup.run"]) if Remote else os.path.join()
	MaxNameWidth=max(*list(map(len, list(SetupVars.keys()))))+2
	with open(SetupSafeRun, "w+") as SetupFile:
		for VarName, VarValue in SetupVars.items():
			SetupFile.write(('\n{0: <'+str(MaxNameWidth)+'} = {1}').format(VarName, VarValue))
	
	#----------------------------------------------------
	# Local upload
	#----------------------------------------------------
	with Misc.cd(UploadDirPath):
		if not SafeRun.SafeRun(CaseInsensitive=not sys.platform.startswith('win'), CommandFiles=[SetupSafeRun, UploadScript]):
			logging.info("'{0}' upload success.".format(HwModel.Name))
			return True
		else:
			logging.error("'{0}' upload failure.".format(HwModel.Name))
			return False




##==================================================================
#def GetConnectionParam(): 
#	"""
#	return parameters for connection.
#	"""
#	User, Pass, Host, Port = "ava-server", "5M96uL3t", "aod2", None
#	logging.debug("User={0}, Host={1}, Port={2}".format(User, Host, Port))
#	return User, Pass, Host, Port







	
