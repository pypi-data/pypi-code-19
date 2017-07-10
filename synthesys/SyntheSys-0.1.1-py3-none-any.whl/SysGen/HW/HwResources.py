
__all__ = ()

import os, sys, logging, re
import math 

#=======================================================================
class HwResources():
	"""
	Object used for Resource comparison.
	"""
	#---------------------------------------------------------------
	def __init__(self, RscDict=None, FPGAModel=None):
		"""
		Initialize RscDict attribute.
		"""
		if RscDict is None:
			self.RscDict = dict()
		else:
			self.RscDict = RscDict
		self.FPGAModel=FPGAModel
	#---------------------------------------------------------------
	def __repr__(self):
		"""
		Return Hardware model string representation.
		"""
		return "HwResources(RscDict={0})".format(repr(self.RscDict))
	#---------------------------------------------------------------
	def __str__(self):
		"""
		Return Hardware model name.
		"""
		StringRep=""
		for Name, (Used, Available, Percentage) in self.RscDict.items():
			StringRep+=", {0}={1}/{2}({3:.2f}%)".format(Name.upper(), Used, Available, Percentage*100)
		return StringRep[2:]
	#---------------------------------------------------------------
	def CompleteRscInfo(self, FPGAModel, RscName, Used, Available, Percentage):
		"""
		Fill Available and Percentage variables.
		"""
		if Available==-1: 
			AvRsc=self.FPGAModel.AvailableResources().RscDict
			if RscName in AvRsc: Available=AvRsc[RscName][0]
		if Percentage==-1: Percentage=float(Used)/float(Available)
		return Available, Percentage
	#---------------------------------------------------------------
	def AddResources(self, Name, Used, Available, Percentage):
		"""
		Fill dictionary 'Resources' from Key/Value pair.
		"""
		Name=Name.upper()
		if self.FPGAModel: Available, Percentage=self.CompleteRscInfo(FPGAModel, Name, Used, Available, Percentage)
		self.RscDict[Name]=(int(Used), int(Available), int(Percentage))
		return True
	#---------------------------------------------------------------
	def GetResourcesDict(self):
		"""
		return Resource dictionary attribute.
		"""
		return self.RscDict
	#---------------------------------------------------------------
	def SetFromSynthesisDir(self, SynthesisDir):
		"""
		Fill dictionary 'Resources' from .map file (in SynthesisDir).
		Use consummed resources.
		"""		
		self.RscDict={}
		MapFile=None		
		for FileName in os.listdir(SynthesisDir):
			if FileName.endswith(".map"): 
				MapFile=os.path.join(SynthesisDir, FileName)
				break
		if not MapFile: 
			logging.error("[HwResources.SetFromSynthesisDir] Unable to find *_map.map file: can't fetch resources.'")
			return self.RscDict
		Rsc = self.GetUsedResourcesDict(MapFile)
#		for WantedRsc in ["SLICE_REGISTER", "SLICE_LUT", "RAMB36E1/FIFO36E1", "RAMB18E1/FIFO18E1", "BUFG/BUFGCTRL", "ILOGICE1/ISERDESE1", "OLOGICE1/OSERDESE1", "BSCAN", "BUFHCE", "BUFO", "BUFIODQS", "BUFR", "CAPTURE", "DSP48E1", "EFUSE_USR", "FRAME_ECC", "GTXE1", "IBUFDS_GTXE1", "ICAP", "IDELAYCTRL", "IODELAYE1", "MMCM_ADV", "PCIE_2_0", "STARTUP", "SYSMON", "TEMAC_SINGLE", ]:
#			for Item in list(Rsc.keys()):
#				if Item.upper().replace(" ","_").find(WantedRsc)!=-1: 
#					self.RscDict[WantedRsc] = Rsc[Item]
#					break
		for RName, (Used, Available, Percentage) in Rsc.items():
			self.RscDict[RName.upper().replace(" ","_")]=(Used, Available, Percentage)
				
		return self.RscDict
	#---------------------------------------------------------------------------------------------------
	# COMPARATORS
	#---------------------------------------------------------------------------------------------------
	def __lt__(self, Other):
		"""
		Operation: <
		"""
		if isinstance(Other, HwResources): 
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): raise NameError
				elif Used>=Other.RscDict[RName][0]:
					return False
		else:
			logging.critical("[HwResources.__lt__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return True
	#-------------------------------------------------
	def __le__(self, Other):
		"""
		Operation: <=
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): raise NameError
				elif Used>Other.RscDict[RName][0]:
					return False
		else:
			logging.critical("[HwResources.__le__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return True
	#-------------------------------------------------
	def __eq__(self, Other):
		"""
		Operation: ==
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): return False
				elif Used!=Other.RscDict[RName][0]:
					return False
		else:
			logging.critical("[HwResources.__eq__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return True
	#-------------------------------------------------
	def __ne__(self, Other):
		"""
		Operation: !=
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): return True
				elif Used!=Other.RscDict[RName][0]:
					return True
		else:
			logging.critical("[HwResources.__ne__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return False
	#-------------------------------------------------
	def __gt__(self, Other):
		"""
		Operation: >
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): 
					logging.error("No such resource '{0}' in {1}.".format(RName, Other))
					raise NameError
				elif Used<=Other.RscDict[RName][0]:
					logging.debug("Test number of "+RName+"s:"+str(Used)+"<="+str(Other.RscDict[RName][0]))
					return False
				logging.debug("Test number of "+RName+"s:"+str(Used)+">"+str(Other.RscDict[RName][0]))
		else:
			logging.critical("[HwResources.__gt__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return True
	#-------------------------------------------------
	def __ge__(self, Other):
		"""
		Operation: >=
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in self.RscDict.items():
				if not (RName in Other.RscDict): raise NameError
				elif Used<Other.RscDict[RName][0]:
					logging.debug("Test number of "+RName+"s:"+str(Used)+"<"+str(Other.RscDict[RName][0]))
					return False
				logging.debug("Test number of "+RName+"s:"+str(Used)+">="+str(Other.RscDict[RName][0]))
		else:
			logging.critical("[HwResources.__ge__] Unable to compare HwResources with type '{0}'.".format(type(Other)))
			raise TypeError
		return True
	#-------------------------------------------------
	def __add__(self, Other):
		"""
		Operation: +
		"""
		if isinstance(Other, HwResources):	
			R=HwResources()
			R+=self
			R+=Other
			return R
		else:
			logging.critical("[HwResources.__add__] Unable to add HwResources with type '{0}'.".format(type(Other)))
			raise TypeError("[HwResources.__add__] Unable to add HwResources with type '{0}'.".format(type(Other)))
		
	#-------------------------------------------------
	def __iadd__(self, Other):
		"""
		Operation and assignment: += 
		"""
		if isinstance(Other, HwResources):	
			for RName, (Used, Available, Percentage) in Other.RscDict.items():
				if self.FPGAModel: Available, Percentage=self.CompleteRscInfo(self.FPGAModel, RName, Used, Available, Percentage)
				if not (RName in self.RscDict): 
					self.RscDict[RName]=(Used, Available, Percentage)
				else:
					NewUsed=Used+self.RscDict[RName][0]
					self.RscDict[RName]=(NewUsed, Available, float(NewUsed)/float(Available))
		else:
			logging.critical("[HwResources.__iadd__] Unable to add HwResources with type '{0}'.".format(type(Other)))
			print("type(self):", type(self))
			print("type(Other):", type(Other))
			raise TypeError("[HwResources.__iadd__] Unable to add HwResources with type '{0}'.".format(type(Other)))
		return self

#======================================================================
def GetUsedResourcesDict(MapFilePath):
	""" 
	Parse the '.map' file and fetch resources utilization and availability.
	"""
	Resources = {}
	logging.debug("Parse resource file '{0}'.".format(MapFilePath))
	with open(MapFilePath, 'r') as RsrcFile:
		for Line in RsrcFile.readlines():
#			Matched = re.match("^\s*Number\s+of\s+(?P<Resource>[\w/\s]+)s\s*:\s*(?P<Used>[,0-9]+)\s+out\s+of\s+(?P<Available>[,\d]+)\s+(?P<Percentage>[,\d]+)%\s*$", Line) # ISE format
			Matched = re.match("^\s*\|\s*(Slice|Block)\s*(?P<Resource>[\w\d]+).*\s*\|\s*(?P<Used>[<.,\d]+)\s*\|\s*([<,.\d]+)\s*\|\s*(?P<Available>[<,.\d]+)\s*\|\s*(?P<Percentage>[<,.\d]+)\s*\|\s*.*$", Line) # Vivado format
			if Matched:
				Correspondances={"LUT":"LUTs", "RAM":"RAM", "REGISTER":"Registers"}
					
				for Elmt, Identifier in Correspondances.items():
					if Matched.group("Resource")==Identifier:
						Used=Matched.group("Used").replace(',','.').replace('<','')
						Available=Matched.group("Available").replace(",", ".").replace('<','')
						Percentage=Matched.group("Percentage").replace(',','.').replace('<','')
						logging.debug("{0}:{1}/{2}({3}%)".format(Elmt, Used, Available, Percentage))
						Resources[Elmt]=[
							int(math.ceil(float(Used))), 
							int(math.ceil(float(Available))), 
							float(Percentage)/100
							]
	return Resources
	
	
	
	
