	
import os, sys, logging
import networkx as nx

from SyntheSys.Analysis import RessourceNode, SelectGroup, TestGroup
from Utilities.Misc import SyntheSysError


#=======================================================================
def ScheduleToAPCG(Scheduling, TaskGraph, FpgaDesign=None):
	"""
	Build a APCG graph with modules as vertices and agglomerate tasks dependences
	as edges.
	"""
	global Colors
	APCG=nx.DiGraph()
	ModuleColorDict={}
	#------------------------------------------------------
	# Create nodes
	for M, TaskList in Scheduling.items():
#		print("M:", M)
#		print("T:", TaskList)
		#----------------------
		# Attribute a color for each type of module
		ModuleName=M.Name
		if not ModuleName in ModuleColorDict:
			try: ModuleColorDict[ModuleName]=Colors.pop(0)
			except: 
#				logging.warning("No more colors available for module graph display. Keep it white")
				ModuleColorDict[ModuleName]="white"
		
		#----------------------
		FirstTask=None
		for T in TaskList:
			if T:
				FirstTask=T
				break
		if FirstTask is None: 
			logging.warning("[ScheduleToAPCG] No task scheduled on module '{0}'.".format(M))
			continue # No task scheduled on this module
			
		# Set Node corresponding to the module--------------------------------
		if FpgaDesign is None:
			if FirstTask.IsInput():
				Node = RessourceNode.IPNode(Module=M, Service=M.GetProvidedService(), Type="Communication")
			elif isinstance(FirstTask, (TestGroup.TestGroup, SelectGroup.SelectGroup)):
				Node = RessourceNode.IPNode(Module=M, Service=M.GetProvidedService(), Type="Control", BranchNumber=4)# TODO : optimize it
			elif FirstTask.GetName()=="Reduce" or FirstTask.GetName()=="Map":
				Node = RessourceNode.IPNode(Module=M, Service=M.GetProvidedService(), Type="MapReduce")
			else:
				Node = RessourceNode.IPNode(Module=M, Service=M.GetProvidedService(), Type="Processing")
		else:
			Node = FpgaDesign.GetNodeFromModule(M)
			if Node is None:
				logging.error("[ScheduleToAPCG] Module '{0}' not found in FpgaDesign NoC mapping.".format(M))
				raise SyntheSysError
		#---------------------------------------------------------------------
		for T in TaskList:
			if T:
#				print("Node:", Node)
#				print("T:", T)
#				input()
				Node.AddTask(T)
				T.Node=Node
#		if FirstTask.IsInput():
#			APCG.add_node(Node, color="black", style='filled', fillcolor=ModuleColorDict[ModuleName], shape='component', rank="source", rankdir="TB", pos="0,0!") #, width=1.2
#		else:
		APCG.add_node(Node, color="black", style='filled', fillcolor=ModuleColorDict[ModuleName], shape='component') #, width=1.2
	
	#------------------------------------------------------
	# Create edges
	for Node in APCG.nodes():
		for Task in Node.GetTasks():
			for Successor in TaskGraph.successors(Task):
				Data=APCG.get_edge_data(Node, Successor.Node, None)
				if Data is None:
					APCG.add_edge(Node, Successor.Node, weight=1, label="1", arrowhead="open") #, color='red', weight=str(Input)
				else:
					Data["weight"]+=1
					Data["label"]+=str(Data["weight"])
	return APCG 
	

#==========================================
def FitAPCG(APCG, HwModel):
	"""
	Reduce APCG by sharing task between nodes.
	The output is a factorized APCG.
	"""
	if HwModel is None: 
		logging.info("No hardware model specified: fully developped APCG produced.")
	else:
		InitialOrder=APCG.order()
		ScheduledDict=Scheduling.ASAP_ALAP(APCG)
		while(HwModel.AvailableResources()>HwModel.EvaluateResources(APCG)):
			if not RemoveOneNode(APCG, ScheduledDict):
				logging.error("[FitAPCG] Unable to reduce APCG. Skipped.")
				break
		FinalOrder=APCG.order()
		logging.info("[Resources sharing] APCG reduced by {0:.2f}%.".format( (InitialOrder-FinalOrder)/InitialOrder ))
	return APCG

#==========================================
def RemoveOneNode(APCG, ScheduledDict):
	"""
	Move task from a selected Node to another and remove it's original Node from the APCG.
	Node are selected by larger scheduling margin.
	"""
	SortedByMarginNode=sorted(list(ScheduledDict.keys()), key=lambda x: ScheduledDict[x][1]-ScheduledDict[x][0], reverse=True)
	if len(SortedByMarginNode)<2:
		logging.error("[RemoveOneNode] No node available for removal.")
		return None
	RefNode=SortedByMarginNode.pop(0)
	RemovedNode=SortedByMarginNode.pop(0)
	
	MovedTasks=RemovedNode.GetTasks()
	for MovedTask in MovedTasks:
		RefNode.AddTask(MovedTask)
	
	APCG.remove_node(RemovedNode)
		
	# Set new margin for RefNode
	ScheduledDict[RefNode]=( 
				max(ScheduledDict[RefNode][0], ScheduledDict[RemovedNode][0]), 
				min(ScheduledDict[RefNode][1], ScheduledDict[RemovedNode][1]) 
				)
	
	return APCG


	
	
#=======================================================================
#=======================================================================
#   NON USED FUNCTION
#=======================================================================
#=======================================================================
def ASAP_ALAP(APCG):
	"""
	Return a dictionary with ASAP and ALAP CSteps.
	"""
	ASAPDict, NbCStep=ScheduleASAP(APCG)
	ALAPDict=ScheduleALAP(APCG, CStepMax=NbCStep)
	
	ScheduleDict={}
	for Node, ASAPCStep in ASAPDict.items():
		ScheduleDict[Node]=(ASAPCStep, ALAPDict[Node])
	return ScheduleDict
	
#=======================================================================
def ScheduleASAP(APCG):
	"""
	Assign time step at each Node of APCG using ASAP scheduling.
	return Scheduled Dictionary and the number of CStep as a tuple.
	"""
	ScheduledDict={}
	ComNode=GetComNode(APCG)
	if ComNode is None:
		logging.error("[ScheduleASAP] No communication node in APCG: aborted.")
		return {}
		
	# For each data to be produced that dependencies has been fullfilled assign an operator => ASAP scheduling
	CStep=0
	ScheduledDict[ComNode]=CStep
	Pending=HasPendingNodesASAP(APCG, ScheduledDict, ComNode)
	while len(Pending): # Has Pending Operations for scheduling
		CStep+=1
		for Node in Pending:
#				logging.debug("Schedule {0} to CStep={1}".format(repr(O), CStep))
#				O.Schedule(CStep=CStep) # Schedule operation
			ScheduledDict[Node]=CStep
			
		Pending=HasPendingNodesASAP(APCG, ScheduledDict, ComNode)
		
	logging.debug("[ScheduleASAP] Number of control-steps: {0}".format(CStep))
	return ScheduledDict, CStep
		
#=======================================================================
def ScheduleALAP(APCG, CStepMax):
	"""
	Assign time step at each Node of APCG using ALAP scheduling.
	"""
	ScheduledDict={}
	ComNode=GetComNode(APCG)
	if ComNode is None:
		logging.error("[ScheduleALAP] No communication node in APCG: aborted.")
		return {}
		
	# For each data to be produced that dependencies has been fullfilled assign an operator => ASAP scheduling
	CStep=CStepMax
	ScheduledDict[ComNode]=CStep
	Pending=HasPendingNodesALAP(APCG, ScheduledDict, ComNode)
	while len(Pending): # Has Pending Operations for scheduling
		CStep+=1
		for Node in Pending:
#				logging.debug("Schedule {0} to CStep={1}".format(repr(O), CStep))
#				O.Schedule(CStep=CStep) # Schedule operation
			ScheduledDict[Node]=CStep
			
		Pending=HasPendingNodesALAP(APCG, ScheduledDict, ComNode)
		
	return ScheduledDict
		

#=======================================================================
def HasPendingNodesASAP(APCG, ScheduledDict, ComNode):
	"""
	Return True if data parent operation is not scheduled yet, False otherwise.
	"""
	PendingNodes=[]
	for Node in ScheduledDict:
#		print("From:", Node)
		for SuccessorNode in APCG.successors(Node):
			if SuccessorNode is ComNode: continue
			elif not (SuccessorNode in ScheduledDict): 
				if not (SuccessorNode in PendingNodes): 
#					print("\tSuccessor:", SuccessorNode)
					PendingNodes.append(SuccessorNode)
	return PendingNodes

#=======================================================================
def HasPendingNodesALAP(APCG, ScheduledDict, ComNode):
	"""
	Return True if data parent operation is not scheduled yet, False otherwise.
	"""
	PendingNodes=[]
	for Node in ScheduledDict:
		for PredecessorNode in APCG.predecessors(Node):
			if PredecessorNode is ComNode: continue
			elif not (PredecessorNode in ScheduledDict): 
				if not (PredecessorNode in PendingNodes): 
					PendingNodes.append(PredecessorNode)
	return PendingNodes

#=======================================================================
#def GetTaskForScheduling(CDFG, TaskList):
#	"""
#	Return list of data that dependencies are fullfilled
#	"""
#	ToBeScheduled=[]
#	for D in CDFG.nodes():
#		Task=D.GetProducer()
#		if Task in TaskList and Task not in ToBeScheduled:
#			if Task.DepSatisfied() and not Task.IsScheduled(): 
#				ToBeScheduled.append(Task)
#	return ToBeScheduled
	
#=======================================================================
def GetComNode(APCG):
	"""
	Find and return the communication node of APCG.
	"""
	ComNode=None
	#-------------------------------------
	for Node in APCG.nodes():
		if Node.GetType()=="Communication":
			ComNode=Node
			break
	#--------------------------------------
	return ComNode
	
	
	






