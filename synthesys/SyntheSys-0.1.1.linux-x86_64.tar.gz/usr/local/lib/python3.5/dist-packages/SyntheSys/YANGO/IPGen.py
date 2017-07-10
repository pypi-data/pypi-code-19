#! /usr/bin/python

import os, sys, re, logging
import math
import shutil

from SyntheSys.Utilities import DesignTree
from SyntheSys.SysGen import HDLEditor



ExtensionDict = HDLEditor.ExtensionDict

#==================================================================
# IPs parameters avalability
#==================================================================
def AvailableValues(Parameter):
	"""
	Return a list of available values for this parameter.
	"""
	AvailableList=[]
	if   Parameter == "FluxCtrl":   AvailableList = ["HandShake","CreditBased",]
	elif Parameter == "Category":   AvailableList = ["Application", "Management"]
	
	return {Parameter:AvailableList}
	
#==================================================================
# Return IP IOs and module name 
#==================================================================
def Parse(SourceList=[]):
	"""
	Parse sources, find top component and return IP IOs and module name of the top.
	"""
	# Build Design tree-----------------------------------
	Design = DesignTree.Design(SourceList)
	if( len(Design.TopComponentList)>0 ):
		TopComponent=Design.TopComponentList[0]
		Module=TopComponent.EntityName
		Signals=[[x.Name, x.IO.upper(), x.Size, x.Type] for x in TopComponent.PortList]
		DesignSources = TopComponent.GetSources() 
		if len(DesignSources) != len(SourceList):
			for Src in SourceList:
				if not DesignSources.count(Src): 
					DesignSources.insert(0, Src)
		Generics = TopComponent.GetGenerics() 
		#Sources=Design.VerilogList+DesignSources # Verilog is not supported yet
		return Module, Signals, DesignSources, Generics
	else: return ("", [], SourceList, {})

#==================================================================
# Generate a wrapper HDL file for specified IP according to signal Dictionnary.
#==================================================================
def GenWrapper(Module, SignalDict, OutputDir):
	"""
	Generate a wrapper HDL file for specified IP according to signal Dictionnary.
	"""
	if not isinstance(SignalDict, dict): return False
	# TODO
	return True

#==================================================================
# IP HDL File generation
#==================================================================
def GenHDL(Module, FluxCtrl="HandShake", OutputPath="./IP", Sources= []):
	"""
	Generate HDL files (VHDL or Verilog) for a NoC of specified type and for specified parameters.
		FluxCtrl     = "HandShake" or "CreditBased"
		VC           = Number of virtual channels (natural)
		Language     = "VHDL" or "Verilog"
		OutputPath   = Output directory path
	"""
	SourceList=[]
	# Check arguments-----------------------------------------------------------
	OutputPath=os.path.join(OutputPath, Module)
	# Create the subdirectory for the NoC
	if not os.path.isdir(OutputPath):# First create tree if it doesn't already exist
		try: os.makedirs(OutputPath)# Recreate the whole directory tree
		except: 
			logging.error("Directory '{0}' cannot be created: IP generation aborted.".format(OutputPath))
			return False # Failure
		logging.info("Directory '{0}' did not already exist : successfully created.".format(OutputPath))
	# Check library-------------------------------------------------------------
	# TODO
	#---------------------------------------------------------------------------
	# Copy source files
	for Source in Sources: # Source paths are relative to LibPath
		shutil.copy(Source, OutputPath)
		SourceList.append(os.path.join(OutputPath, os.path.basename(Source)))
	return SourceList # Success
				
#==================================================================
# Copy each source file from list to library subdirectory.
#==================================================================
def AddSourcesToLib(IPName, Sources=[], LibPath="./", Management=False):
	"""
	Copy each source file from list to library subdirectory "IPName".
	Into Subdirectory "Management" or "Application" if specified (default: Application).
	"""	
	if Management: SubCategory="Management"
	else:          SubCategory="Application"
	
	TargetFolder = os.path.join(LibPath, "IP", SubCategory, IPName)
	if os.path.exists(TargetFolder): shutil.rmtree(TargetFolder)
	os.makedirs(TargetFolder)
	for SourceFile in Sources: shutil.copy(SourceFile, TargetFolder)	
				
#==================================================================
# Search in directory tree for specified file, and copy it to output folder.
#==================================================================
def CopySources(InputFolder, OutputFolder):
	"""
	Search recursively into InputDirectory folders.
	Then copy the file that match key words in 'KeyWords' to OutputFolder.
	"""		
	if os.path.isdir(InputFolder):
		for FileName in [x for x in os.listdir(InputFolder) if not x.startswith('.')]:
			# Copy source files
			if re.match("\.(vhd|v)$", FileName):
				shutil.copy(os.path.join(InputFolder, FileName), OutputFolder)
				logging.info("File '{0}' copied to '{1}'.".format(FileName,OutputFolder))
	else: logging.error("Source folder '{0}' does not exist: copy aborted.".format(InputFolder))
	
#==================================================================
# Main tests.
#==================================================================
if __name__ == "__main__":
	
	print("IPGen module test.")
	
	
	
	
	
	
	
