
import sys, os, logging
import subprocess
#sys.path.append("./Drawing/")
#import Drawing

#==============================================================
class Emulation():
	"""
	Object that represent a Emulation.
	It allows to configure/run Emulation and fetch results.
	"""
	#------------------------------------------------------
	def __init__(self, Module, Architecture, OutputPath="./"):
		"""
		Configure a new Emulation environment.
		"""
		if not os.path.isdir(str(OutputPath)):
			logging.error("Unable to generate files for application: incorrect output directory '{0}'.".format(str(OutputPath))) 
			return None # Thread, Event, FPGACmds
		self.SrcList=Module.GenSrc(Synthesizable=True, OutputDir=OutputPath, TestBench=True, IsTop=True)
		DepDict=Module.GetDependencies()
		self.Packages=DepDict["package"]
		self.Libraries=DepDict["library"]
		self.TopName=Module.Name
		self.Architecture=Architecture
		self.User="matthieu.payet"
		self.Server="aod2"
		self.OutputPath=OutputPath
		self.TraceFile=None
		self.ClockNames=Module.GetClocks()
		TRServList = [Serv for Serv in [x[0] for x in list(Module.ReqServ.values())] if Serv.Name=="TrafficReceptor"]
		self.TraceNames = ["{0} DataIn".format(x.Alias) for x in TRServList]
		self.TraceNames=list(set(self.TraceNames))
		
	#------------------------------------------------------
	def Run(self, Emulator="AVA-Soft"):
		"""
		Launch Emulation with specified simulator. 
		"""
		if Emulator=="AVA-Soft":
			AVAProj=RFI.AVASoftProject(
					ProjectName=self.TopName,
					TB="TB_TrafficSynthesis",
					Architecture=self.Architecture, 
					ProjectPath=os.path.join("/", "home", self.User), 
					OutputPath=self.OutputPath)
			AVAProj.ServerConfig(User=self.User, Server=self.Server, Password="55paymat07")
			AVAProj.SetTBParameters(ClockNames=self.ClockNames, StimNames=["Rst","Reset"], TraceNames=self.TraceNames)
			AVAProj.SetRunParameters(ClkDiv=10, Latency=10)
			AVAProj.SetSources(self.SrcList, self.Packages, self.Libraries)
			for Src in self.SrcList:
				if Src.endswith(self.TopName+".vhd") or Src.endswith(self.TopName+".v"):
					break
			AVAProj.SetTop(self.TopName, TopPath=Src)
			Msg=AVAProj.Run()
		
		return Msg
		
	#------------------------------------------------------
	def GetResults(self):
		"""
		Return traffic synthesis results (?). 
		"""
		self.TraceFile=AVAProj.GetTraces()
		return self.TraceFile
	
	
#==============================================================
class TrafficEmulation(Emulation):
	"""
	Sub class of Emulation dedicated to NoC Traffic Emulation.
	"""
	#------------------------------------------------------
	def __init__(self, TopModule, Architecture, TrafficMatrix={}, OutputPath="./"):
		"""
		Configure traffic parameters.
		"""
		Emulation.__init__(self, Module=TopModule, Architecture=Architecture, OutputPath=OutputPath)
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










