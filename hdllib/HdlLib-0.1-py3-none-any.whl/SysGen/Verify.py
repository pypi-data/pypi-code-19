
import sys, os, logging, re

from HdlLib.SysGen import LibEditor, HDLEditor, Constraints, Module
import HdlLib.SysGen



#===============================================================
def WrapForTest(Module):
	"""
	Return a service made up of the basic block and sharing component services.
	"""
	logging.debug("Wrap module for verifying")
	if Module is None:
		logging.error("[HdlLib.SysGen.Verify.WrapForTest] No Module specified. Aborted.")
		return False
	#---------------------------------
	# Create a new module DUT
	Infos={
		"Name"   : "DUT",
		"Version": "", # TODO get current time
		"Title"  : "DUT wrapper for {0} to be verified.".format(Module.Name),
		"Purpose": "DEVICE UNDER TEST module.",
		"Desc"   : "",
		"Tool"   : "",
		"Area"   : "",
		"Speed"  : "",
		"Issues" : "",
	}
	# Empty new module-----------------------------------
	Ports=[
		HDLEditor.Signal("Outputs",  Direction="OUT", Size=96, Type="logic"),
		HDLEditor.Signal("Inputs", Direction="IN",  Size=96, Type="logic"),
		HDLEditor.Signal("Clk",   Direction="IN",  Size=1,  Type="logic")
		]
#	Clocks=[HDLEditor.Signal(Name="DUT_Clock"),]
	DUTMod=LibEditor.NewModule(Infos=Infos, Params=[], Ports=Ports, Clocks=[], Resets=[], Sources=[])
			
	#---------------------------------	
	DUTMod.UpdateXML()
	#----------
	CopyMod, CopyServ, Mapping, StimuliList, TracesList, ClocksList = Module.CopyModule(Module)
	#---------------------------------
#	ClockServ=Library.Service("clock")
#	RstServ=Library.Service("reset")
	DUTMod.IdentifyServices([CopyServ, ])
	
	SubServices=[CopyServ,]
	Mappings=[Mapping,]
	DUTMod.MapSubServices(Services=SubServices, Mappings=Mappings)
	#----------
	XMLElmt=DUTMod.UpdateXML()
#	from lxml import etree
#	print(etree.tostring(XMLElmt, encoding="UTF-8", pretty_print=True))
	DUTMod.Reload()
	DUTMod.IdentifyServices([CopyServ,])
	#---------------------------------
	return DUTMod, StimuliList, TracesList, ClocksList


#===============================================================
def GetTopVerif(HwArchi):
	"""
	return verif controller top module.
	"""
	#---------------------------------
	Library = HdlLib.SysGen.XmlLibManager.XmlLibManager(HdlLib.SysGen.BBLIBRARYPATH)
	ControlVerifServ=Library.Service("ControlVerif") 
	ControlVerifServ.Alias="Ctrl"
	#---------------------------------
	return ControlVerifServ.GetModule(Constraints=Constraints.Constraints(None, HwModel=HwArchi))
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

