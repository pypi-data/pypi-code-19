#!/usr/bin/python

import os, sys, re, logging, datetime
import shutil
import collections
import configparser
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import Timer 
	

#==================================================================
def GetConstraintsFromFile(ConstraintsFile):
	"""
	Return dictionnary of pair Net:Pad.
	"""
	# Test argument -------------------------------------------
	if not os.path.isfile(ConstraintsFile): 
		logging.error("Constraints file '{0}' isn't a regular file: parse aborted.".format(ConstraintsFile))
		return {}
		
	Format=ConstraintsFile.split('.')[-1]
	logging.debug("Constraints file type '{0}'.".format(Format))
	# Process file --------------------------------------------
	Constraints = {}#collections.OrderedDict()
	with open(ConstraintsFile, "r") as CFile:
		Key="?"
		for Line in CFile.readlines():
			# Now Parse IO line
			if Format=="ucf":
				Matched = re.match(
'^\s*NET\s*\"?(?P<PadName>[a-zA-Z0-9_()<>]+)\"?\s+LOC\s*=\s*\"?(?P<PadID>[a-zA-Z0-9_]+)\"?\s*.*\s*;(\s*[#]*(?P<Comment>.*))*$', Line)
			elif Format=="tcl":
				Matched = re.match(
'^\s*set_location_assignment\s*\"?(?P<PadID>[a-zA-Z0-9_]+)\"?.*\s+-to\s*\"?(?P<PadName>[a-zA-Z0-9_()\][]+)\"?.*\s*.*$', Line)
			elif Format=="pdc":
				Matched = re.match(
'^\s*set_io\s*\"?(?P<PadName>[\\a-zA-Z0-9_()\][]+)\"?.*\s+\-pinname\s*\"?(?P<PadID>[a-zA-Z0-9_]+)\"?.*\s*.*$', Line)

			if Matched: 
				PadName = Matched.group('PadName')
				PadID   = Matched.group("PadID")
#				Comment = Matched.group("Comment").strip('\n \r')
#				Comment = Comment.replace(',','')
				PadName=PadName.replace('"','').strip()
				if "<" in PadName: # UCF Format
					RootName, Index = PadName.split('<')
					Index=Index.replace('>', '')
					Constraints["{0}:{1}".format(RootName, Index)]=PadID
				elif r"\[" in PadName: # PDC Format
					RootName, Index = PadName.split(r"\[")
					Index=Index.replace(r"\]", '')
					Constraints["{0}:{1}".format(RootName, Index)]=PadID
				elif r"[" in PadName: # TCL Format
					RootName, Index = PadName.split(r"[")
					Index=Index.replace(r"]", '')
					Constraints["{0}:{1}".format(RootName, Index)]=PadID
				else:
					Constraints[PadName]=PadID
	return Constraints
	
#==========================================================================
# CONSTRAINTS FILES MANAGEMENT
#==========================================================================
def GenConstraintDict(Module, FPGAInterfaceDict):
	"""
	return dictionary with bit-to-pad assignments.
	"""
	ConstraintsList=[]
	ClockManagerDict={}
	#---------------------------------------------
	def GetAvailablePads(FPGAInterfaceDict, PortDirection):
		AvailablePads=FPGAInterfaceDict[PortDirection] # First select pad dedicated as INPUT or OUTPUT
		if len(AvailablePads)==0:	
			AvailablePads=FPGAInterfaceDict["INOUT"] # Then try generic pads
		return AvailablePads
	#---------------------------------------------
	
	#---------------Begin with clocks and reset signals------------------
	if not "CLOCK" in FPGAInterfaceDict:
		logging.error("[pyInterCo.HW.HWConstraints.GenConstraintDict] Empty interface dictionary.")
		return {}
	# TODO : do not consider provided constraint pads (in library) ("ignored" constraints)
	for Signal, PadType, Parameters in Module.GetPadConstraints():
#		print("Sig:", Signal)
#		print("PadType:", PadType)
#		print("Parameters:", Parameters)
#		input()
		if Parameters is None: pass
		elif Parameters.lower()=="ignore": continue # Provided constraints
		
		if not PadType in FPGAInterfaceDict:
			print("FPGAInterfaceDict:", list(FPGAInterfaceDict.keys()))
			logging.error("[GenConstraintDict] No {0} pads available for signal '{1}' on this FPGA board. Ignored.".format(PadType, Signal))
			Answer=''
			while not(Answer in ['y', 'n']):
				Answer=input("Continue ? y/n : ").lower()
			if Answer=='y': continue
			else: sys.exit(1)
			
		AvailablePads=FPGAInterfaceDict[PadType].copy()
		if len(AvailablePads)==0:
			logging.error("[GenConstraintDict] No more {0} pads available for clock signal '{0}' on this FPGA board. Ignored.".format(PadType, Signal))
			Answer=''
			while not(Answer in ['y', 'n']):
				Answer=input("Continue ? y/n : ").lower()
			if Answer=='y': continue
			else: sys.exit(1)

		while len(AvailablePads):
			Net, PadConstraintList = AvailablePads.popitem()
			# (Pad, IOStandard , Voltage, Freq, DiffPair)
			MatchConstraint=True
			if not (Parameters is None): 
				# Test for specific constraints
				for i, Item in enumerate(Parameters.split(',')):
					if i>(len(PadConstraintList)-2): 
						logging.warning("[GenConstraintDict] Signal '{0}': Ignore remaining constraint parameter from '{1}' (included).".format(Signal, Item))
						continue
					if Item!=PadConstraintList[i+1]:
						MatchConstraint=False
			elif not (PadConstraintList[4] is None): 
				MatchConstraint=False
				continue # DiffPair => do not connect single ended to differential
			if MatchConstraint is True:
				PadConstraintList = FPGAInterfaceDict[PadType].pop(Net)
				Pad, IOStandard, Voltage, Freq, DiffPair = PadConstraintList
				ConstraintsList.append({"Port": Signal, "Name": Signal.Name, "Direction":Signal.Direction, "Net":Net, "TargetPad": Pad, "CtrlPad":None, "Tag": Parameters, "IOStandard":IOStandard, "Voltage":Voltage, "Freq":Freq, "DiffPair":DiffPair})
				logging.debug("Assign pad '{0} to net '{1}' of module '{2}'.".format(Pad, Signal, Module))
				break
		
		if MatchConstraint is False:
			if PadType=="CLOCK" and len(FPGAInterfaceDict[PadType])!=0:
				logging.debug("Clock '{0}' has to be driven from a clock manager".format(Signal))
				if not (Parameters is None): 
					Params=Parameters.split(',')
					if len(Params)>=4: TargetFrequency=Params[3] # Frequency parameter
					else: 
						logging.warning("No frequency target is given for clock '{0}'.".format(Signal))
						TargetFrequency=None
				else: 
					logging.warning("No frequency target is given for clock '{0}'.".format(Signal))
					TargetFrequency=None

				# TODO : manage clock frequency constraint ?
				Pads, Diff=PopClock(FPGAInterfaceDict[PadType])
				ClockManagerDict[Signal]=(TargetFrequency, Diff, Pads)

				for PadAlias, (Pad, IOStandard, Voltage, Freq, DiffPair) in Pads:
					ConstraintsList.append({"Port": Signal.Copy(), "Name": PadAlias, "Direction":Signal.Direction, "Net":PadAlias, "TargetPad": Pad, "CtrlPad":None, "Tag": Parameters, "IOStandard":IOStandard, "Voltage":Voltage, "Freq":Freq, "DiffPair":DiffPair})
					logging.debug("Assign pad '{0}' to new clock net '{1}' of module '{2}'.".format(Pad, Signal, Module))
					
			else:
				logging.error("[GenConstraintDict] No {0} pads available for signal '{0}' on this FPGA board. Ignored.".format(Type, Signal))

	return ConstraintsList, ClockManagerDict
	
#==========================================================================
def GenConstraintDict_AVA(Module, InterfaceDict, CtrlInterfaceDict):
	ConstraintsList=[]
	#---------------------------------------------
	def GetAvailablePads(InterfaceDict, PortDirection):
		AvailablePads=InterfaceDict[PortDirection] # First select pad dedicated as INPUT or OUTPUT
		if len(AvailablePads)==0:	
			AvailablePads=InterfaceDict["INOUT"] # Then try generic pads
		return AvailablePads
	#---------------------------------------------
	
	#---------------Begin with clocks and reset signals------------------
	if not "CLOCK" in InterfaceDict:
		logging.error("[pyInterCo.HW.HWConstraints.GenConstraintDict] Empty interface dictionary.")
		return {}
		
	AvailablePads=InterfaceDict["CLOCK"]
	ClockResetList=Module.GetClockNames()+Module.GetResetNames()
	for ClockReset in ClockResetList:#[:]:
		if len(AvailablePads)==0:
			logging.warning("No more clock pads available for clock signal '{0}' on this FPGA board.".format(ClockReset))
			AvailablePads=GetAvailablePads(InterfaceDict, PortDirection="IN")
		ClockResetList.remove(ClockReset)
		(Tag, TargetPad)=AvailablePads.popitem(last=False)
	
		CtrlPads=CtrlInterfaceDict["CLOCK"] if "CLOCK" in CtrlInterfaceDict else {}
		# Get signal object corresponding to ClockReset name
		Found=False
		for OPName, OP in Module.OrthoPorts.items():
			if OP.OrthoName()==ClockReset:
				Found=True
				# MAP IT
				logging.debug("Assign clock pad '{0}' to net '{1}'.".format(TargetPad, ClockReset))	
				Sig=OP.Copy()
				Sig.Name=ClockReset
				CtrlPad=CtrlPads[Tag] if Tag in CtrlPads else None
				ConstraintsList.append({"Port": Sig, "Name": ClockReset, "Direction":"CLOCK", "Net": ClockReset, "TargetPad": TargetPad, "CtrlPad":CtrlPad, "Tag": Tag})
				break
		if Found is False:
			logging.error("[GenConstraintDict] Clock or reset signal '{0}' not found in module '{1}'".format(ClockReset, Module))
	# Assign other clocks as inputs
	
	#---------------Then continue with normal IOs------------------
	for PName, Port in Module.GetExternalPorts(CalledServ=None).items():
		if len(InterfaceDict)==0:
			logging.error("[GenConstraintDict] No pads available for this FPGA board.")
		PortSize=Port.GetSize()
		PortDirection=Port.Direction.upper()
		CtrlPads=CtrlInterfaceDict[PortDirection] if PortDirection in CtrlInterfaceDict else {}
		if PortSize!=1: # Means it is a vector
			#---------------------------------------------
			# Find bit order:
			#---------------------------------------------
			SubMapping=[]
			AvailablePads=InterfaceDict[PortDirection]
			if len(AvailablePads)==0:
				AvailablePads=GetAvailablePads(InterfaceDict, PortDirection=PortDirection)
				if len(AvailablePads)==0:	
					logging.error("[GenConstraintDict] No more '{1}' or 'INOUT' pads available for signal '{0}' on this FPGA board.".format(PName, PortDirection))
					continue
			for Index in reversed(range(PortSize)):
				if len(AvailablePads)==0:
					logging.error("[GenConstraintDict] No more '{1}' or 'INOUT' pads available for signal '{0}' on this FPGA board.".format(PName, PortDirection))
					break
				(Tag, TargetPad)=AvailablePads.popitem(last=False)
				CtrlPad=CtrlPads[Tag] if Tag in CtrlPads else None
				SubMapping.append({"Port":Port, "Name":PName, "Direction": PortDirection, "Net": PName, "TargetPad": TargetPad, "CtrlPad":CtrlPad, "Index":Index, "Tag": Tag,})
				logging.debug("Assign {2} pad '{0}' to net '{1}'.".format(TargetPad, PName+"[{0}]".format(Index), PortDirection))	
			ConstraintsList.append(SubMapping)
		else: # Means it is not a vector
			AvailablePads=GetAvailablePads(InterfaceDict, PortDirection=PortDirection)
			if len(AvailablePads)==0:
				AvailablePads=InterfaceDict[PortDirection]
				if len(AvailablePads)==0:	
					logging.error("[GenConstraintDict] No more '{1}' or 'INOUT' pads available for signal '{0}' on this FPGA board.".format(PName, PortDirection))
					continue
			(Tag, TargetPad)=AvailablePads.popitem(last=False)
			CtrlPad=CtrlPads[Tag] if Tag in CtrlPads else None
			ConstraintsList.append({"Port":Port, "Name":PName, "Direction":PortDirection, "Net": PName, "TargetPad": TargetPad, "CtrlPad":CtrlPad, "Tag": Tag})
			logging.debug("Assign {2} pad '{0}' to net '{1}'.".format(TargetPad, PName, PortDirection))	

	return ConstraintsList
	
#==========================================================================
def GenConstraintsFile(Module, HwModel, ControlHW, Library, OutputPath):
	"""
	Create constraints file according to ConstraintsList.
	ConstraintsList is build from Signals type and board constraints dictionary.
	"""
	global WriteConstraintFunc
	#-----------------
	ConstraintFormat=HwModel.Config.GetConstraintFormat() # TODO : Use it !
	if not ConstraintFormat in WriteConstraintFunc:
		logging.error("Unsupported constraint format '{0}'".format(ConstraintFormat))
		return None, None
		
	ModuleWrapper=None
	#----------------------------------------------------
#	if ControlHW is None:
	logging.debug("Generate constraints for standard synthesis.")
	FPGAInterfaceDict=HwModel.GetInterface()
	if len(FPGAInterfaceDict)==0: return None, None
#	CtrlInterfaceDict={}
	ConstraintsList, ClockManagerDict=GenConstraintDict(Module, FPGAInterfaceDict)
#	print("ClockManagerDict:", ClockManagerDict)
#	input()
	ModuleWrapper, NewClockSigs = Module.WrapForClocking(HwModel, ClockManagerDict, Library)
	if ModuleWrapper is None: return None, None
	
#	else: # Find a configuration for the couple Ctrl/Target.
#		# AVA-Test mode
#		logging.debug("Generate constraints for AVA-Test.")
#		CtrlConfigList=ControlHW.GetCtrlConfig(TargetHW=HwModel, Module=Module)
#		if len(CtrlConfigList)==0:
#			logging.error("[GetPadConstraints] No compatible configuration found for controller '{0}'.".format(ControlHW.Name))
#			return None, None
#		# Take first configuration found
#		CtrlInterfaceDict=ControlHW.GetCtrlConfigInterface(
#						CtrlConfig          = CtrlConfigList[0], 
#						TargetInterfaceDict = HwModel.GetInterface()
#						)
#		
#		InterfaceDict={}
#		for T in ["CLOCK", "IN", "OUT", "INOUT"]:
#			InterfaceDict[T]=collections.OrderedDict()
#		for k,v in CtrlInterfaceDict["CLOCK"].items():
#			InterfaceDict[T][k]=HwModel.InterfaceDict["CLOCK"].popitem(k)[1]
#		for k,v in CtrlInterfaceDict["IN"].items():
#			try: InterfaceDict[T][k]=HwModel.InterfaceDict["IN"].popitem(k)[1]
#			except: InterfaceDict[T][k]=HwModel.InterfaceDict["INOUT"].popitem(k)[1]
#		for k,v in CtrlInterfaceDict["OUT"].items():
#			try: InterfaceDict[T][k]=HwModel.InterfaceDict["OUT"].popitem(k)[1]
#			except: InterfaceDict[T][k]=HwModel.InterfaceDict["INOUT"].popitem(k)[1]
#		ConstraintsList=GenConstraintDict_AVA(Module, InterfaceDict, CtrlInterfaceDict)
	#----------------------------------------------------
	ConstFilePath=os.path.join(OutputPath, "{0}_{1}.{2}".format(Module.Name, HwModel, ConstraintFormat))
	with open(ConstFilePath, "w+") as ConstFile:
		ConstFile.write("\n# Constraints for '{0}'".format(HwModel))
		ConstFile.write("\n# Automatically generated file (date: {0})\n".format(Timer.TimeStamp()))
		
		#--------------------------------------------------
		NameList=[]
		PadNameList=[]
		for Cons in ConstraintsList:
			if isinstance(Cons, list):
				for C in Cons:
					NameList.append(C["Name"])
					PadNameList.append(C["TargetPad"])
			else: 
				NameList.append(Cons["Name"])
				PadNameList.append(Cons["TargetPad"])
		MaxNameWidth = max([len(x) for x in NameList])+2 if len(NameList)>0 else 0 
		MaxPadWidth = max([len(x) for x in PadNameList])+2 if len(NameList)>0 else 0
		#--------------------------------------------------
		Comments={
			"CLOCK" : 'CLOCK,  associated with control FGPA clock pad "{0}"',
			"OUT"   : 'OUTPUT, associated with control FGPA pad "{0}"',
			"IN"    : 'INPUT,  associated with control FGPA pad "{0}"',
			"INOUT" : 'INOUT,  associated with control FGPA pad "{0}"',
		}
		#--------------------------------------------------
		
		for Cons in ConstraintsList:
			#--------------------------------------------------
			if isinstance(Cons, list):
				Size=len(Cons)
				for i, CDict in enumerate(Cons):
					Port=CDict["Port"]
					Direction=CDict["Direction"]
					WriteConstraintFunc[ConstraintFormat](ConstFile,
							IO=Direction, 
							MaxNameWidth=MaxNameWidth, 
							MaxPadWidth=MaxPadWidth, 
							PortName=CDict["Name"], 
							Pad=CDict["TargetPad"],
							IOStandard=Cons["IOStandard"],
							Comments=Comments[Direction].format(CDict["CtrlPad"]) if CDict["CtrlPad"] else "",
							Index=CDict["Index"])
			#--------------------------------------------------
			else: 
				Port=Cons["Port"]
				Direction=Cons["Direction"]
				WriteConstraintFunc[ConstraintFormat](
						ConstFile,
						IO=Direction, 
						MaxNameWidth=MaxNameWidth, 
						MaxPadWidth=MaxPadWidth, 
						PortName=Cons["Name"], 
						Pad=Cons["TargetPad"], 
						IOStandard=Cons["IOStandard"],
						Comments=Comments[Direction].format(Cons["CtrlPad"] if Cons["CtrlPad"] else "")
						)
				
		ConstFile.write("\n\n")
		#--------------------------------------------------
	return ConstFilePath, ModuleWrapper, NewClockSigs
	
#==================================================================
def XDC_AssignNet(ConstFile, IO, MaxNameWidth, MaxPadWidth, PortName, Pad, IOStandard, Comments, Index=None):
	if Index is None: FullPortName='{'+PortName+'}'
	else:             FullPortName='{'+PortName+'[{INDEX}]'.format(INDEX=Index)+'}'
	
	OptionalAttr={
		"CLOCK" : "\ncreate_clock -period 5.0 [get_ports {PORT}]\nset_input_jitter [get_clocks -of_objects [get_ports {PORT}]] 0.05",
		"IN"    : "",
		"OUT"   : "",
		"INOUT" : "",
		}
	
	Line=('set_property PACKAGE_PIN {PAD} [get_ports {PORT}]\nset_property IOSTANDARD {IOSTD} [get_ports {PORT}]\n{OPT}').format(PORT=FullPortName, PAD=Pad, IOSTD=IOStandard, OPT=OptionalAttr[IO])#+"# "+Comments
	if Pad.upper()=="NC":
		Line="# "+Line
	ConstFile.write('\n'+Line) # Ignore comments
	return 
	
#==================================================================
def UCF_AssignNet(ConstFile, IO, MaxNameWidth, MaxPadWidth, PortName, Pad, IOStandard, Comments, Index=None):
	if Index is None: FullPortName='"'+PortName+'"'
	else:             FullPortName='"'+PortName+'<{0}>"'.format(Index)
	
	OptionalAttr={
		"CLOCK" :" | IOB = TRUE | IOSTANDARD = LVCMOS25 | CLOCK_DEDICATED_ROUTE = TRUE", # | DRIVE = 24
		"OUT"   :" | IOB = TRUE | IOSTANDARD = LVCMOS25", # | DRIVE = 24
		"IN"    :" | IOB = TRUE | IOSTANDARD = LVCMOS25",
		"INOUT" :" | IOB = TRUE | IOSTANDARD = LVCMOS25",
		}#" | IOB = True"
	
	Line=('NET {0: <'+str(MaxNameWidth)+'} LOC = {1: <'+str(MaxPadWidth)+'}{2}; ').format(FullPortName, '"'+Pad+'"', OptionalAttr[IO])+"# "+Comments
	if Pad.upper()=="NC":
		Line="# "+Line
	ConstFile.write('\n'+Line) # Ignore comments
	return 
	
#==================================================================
def TCL_AssignNet(ConstFile, IO, MaxNameWidth, MaxPadWidth, PortName, Pad, IOStandard, Comments, Index=None):
	if Index is None: FullPortName=PortName
	else:             FullPortName=PortName+'[{0}]'.format(Index)
	
	OptionalAttr={
		"CLOCK" : "",
		"OUT"   : "",
		"IN"    : "",
		"INOUT" : "",
		}
		
	Line=('set_location_assignment {0: <'+str(MaxPadWidth-2)+'} -to {1: <'+str(MaxNameWidth-2)+'}{2} ').format(Pad, FullPortName, OptionalAttr[IO])
	if Pad.upper()=="NC":
		Line="# "+Line
	ConstFile.write('\n#'+Comments) # Ignore comments
	ConstFile.write('\n'+Line) # Ignore comments
	return
	
#==================================================================
def PDC_AssignNet(ConstFile, IO, MaxNameWidth, MaxPadWidth, PortName, Pad, IOStandard, Comments, Index=None):
	if Index is None: FullPortName='"'+PortName+'"'
	else:             FullPortName='"'+PortName+r'\['+str(Index)+r'\]"'
	
	OptionalAttr={
		"CLOCK" : "",
		"OUT"   : "",
		"IN"    : "",
		"INOUT" : "",
		}
		
	Line=('set_io {0: <'+str(MaxNameWidth+2)+'}  -pinname {1: <'+str(MaxPadWidth)+'}{2}').format(FullPortName, '"'+Pad+'"', OptionalAttr[IO])
	if Pad.upper()=="NC":
		Line="# "+Line
	ConstFile.write('\n'+Line) # Ignore comments
	return
	
#==================================================================
def PopClock(AvailablePads):
	"""
	Get single ended or differential pair clock from dict of pads.
	"""
#	while len(AvailablePads):
	if len(AvailablePads)!=0:
		Net, ConstraintList = AvailablePads.popitem()
		Pad, IOStandard, Voltage, Freq, DiffPair = ConstraintList
		if DiffPair:
			OtherNet, OtherConstraintList = GetDiffPair(AvailablePads, DiffPair)
			return [(Net, ConstraintList), (OtherNet, OtherConstraintList)], True
		
		return [(Net, ConstraintList),], False
	raise TypeError("[PopClock] Empty dictionary given !!!!")
	
#==================================================================
def GetDiffPair(AvailablePads, DiffPair):
	"""
	Get the other net forming a differential pair.
	"""
	for OtherNet, ConstraintList in AvailablePads.items():
		if ConstraintList[4]==DiffPair:
			break
	OtherConstraintList = AvailablePads.pop(OtherNet)
	return OtherNet, OtherConstraintList

###################################################################
WriteConstraintFunc={
		"ucf":UCF_AssignNet,
		"tcl":TCL_AssignNet,
		"pdc":PDC_AssignNet,
		"xdc":XDC_AssignNet,
	}
###################################################################
	
#==================================================================
# Main tests.
#==================================================================
if __name__ == "__main__":
	logging.critical("No test bench for the module '{0}'.".format(__file__))
	
	
	
	
	
	
	
	
	
	
	
