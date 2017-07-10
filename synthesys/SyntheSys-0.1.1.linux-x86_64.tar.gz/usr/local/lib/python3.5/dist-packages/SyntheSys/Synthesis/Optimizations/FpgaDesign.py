"""
FpgaDesign
"""
	
import os, sys, logging
#import networkx as nx

#from SyntheSys.Synthesis.Optimizations import ResourceSharing as RS
#from SyntheSys.Synthesis.Graphs import AppCharGraph
from SyntheSys.YANGO import MapUtils
from Utilities.Misc import SyntheSysError



#=========================================================
class FpgaDesign:
	""" 
	Contains every information about a NoC design mapped onto FPGA.
	"""		
	#-------------------------------------------------
	def __init__(self, BaseApp, DimX, DimY, NoCMapping, ARCG, NoCParams, Constraints):
		"""
		Initialization of the FpgaDesign attributes.
		"""
		self.Constraints = Constraints
		self.NoCParams   = NoCParams
		self.ARCG        = ARCG
		self.NoCMapping  = NoCMapping # {IP:(x,y),}
		self.DimX        = DimX
		self.DimY        = DimY
		self.Name        = "SyntheSysDesign_{FPGA}_NoC({X}x{Y})_{App}".format(FPGA=self.Constraints.HwModel.GetFPGA(), X=self.DimX, Y=self.DimY, App=BaseApp)
	#-------------------------------------------------
	def Coord(self, Mod):
		"""
		return module coordinates.
		"""
		if Mod in self.NoCMapping:
			return self.NoCMapping[Mod]
		else:
			logging.error("[FpgaDesign.Coord] Given module '{0}' not mapped to a place in Fpga design {1}".format(self.Name))
			raise SyntheSysError
	#-------------------------------------------------
	def ComLatency(self, Mod1, Mod2):
		"""
		return the estimated number of clock cycles needed to send a packet from Mod1 to Mod2.
		"""
		C1 = self.Coord(Mod1) # Predecessor
		C2 = self.Coord(Mod2) # Current
		Distance = MapUtils.ManDist(C1, C2, self.ARCG)
		return Distance+2
	#-------------------------------------------------
	def ModuleList(self):
		"""
		return list of design's modules.
		"""
		return [Node.GetModule() for Node in self.NoCMapping.keys()]
	#-------------------------------------------------
	def GetNodeFromModule(self, Mod):
		"""
		return node object corresponding to given module instance.
		"""
		for N in self.NoCMapping.keys():
			if N.GetModule() is Mod:
				return N
		return None
	#-------------------------------------------------
	def GetUnscheduledEquivalentMod(self, Mod, Sched):
		"""
		return Equivalent module from existing mapping that is not scheduled yet.
		"""
		Found=None
		for M in self.ModuleList():
			if not (M in Sched):
				if M.Name==Mod.Name:
					if Found is None:
						Found=M
					else:
						# TODO : Choose the best module position on the NoC
						break
		return Found
	#-------------------------------------------------
	def ResetScheduling(self):
		"""
		Empty Nodes's task lists.
		"""
		for N in self.NoCMapping.keys():
			N.ClearTasks()
		return 
	#-------------------------------------------------
	def ReloadModules(self, Lib):
		"""
		Replace old modules by those from given lib.
		"""
		for Node in self.NoCMapping.keys():
			OldMod=Node.GetModule()
			for M in Lib.Modules:
				if M.Name==OldMod.Name:
					Node.SetModule(M.Copy())
					break
	#-------------------------------------------------
	def WriteFile(self, OutputPath):
		"""
		Generate *.soc file in given OutputPath.
		"""
		SoCFilePath = os.path.join(OutputPath, self.Name+'.soc')
		with open(SoCFilePath, "wb+") as SoCFile:
			# TODO : fill file
#			SoCFile.write(self.Constraints.AsXml())
#			SoCFile.write(self.NoCParams.AsXml())
#			SoCFile.write(self.ARCG.AsXml())
#			SoCFile.write(self.NoCMapping.AsXml())
#			SoCFile.write(self.DimX.AsXml())
#			SoCFile.write(self.DimY.AsXml())
#			SoCFile.write(self.Name.AsXml())
			pass
		return 
	#-------------------------------------------------
	def SetupFrom(self, SoCFilePath):
		"""
		Setup attribute from given *.soc file.
		"""
		logging.error("TODO: define function SetupFrom of FpgaDesign")
		sys.exit(1)
		return

