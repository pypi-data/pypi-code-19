"""
######################
SCHEDULING
######################
Ordonnancement : Ajout de la notion de temps (mise en pipeline). Generation d'une FSM. Notion de C-Steps (control-steps) = cycle d'horloge.
	- Interval d'initialisation : nombre de cycle d'horloge a attendre entre deux cycle d'ordonnancement (1 pour pipeline maximum). C'est la contrainte de pipelining !
	- Latence : nombre de cycles d'horloges entre la premiere entree et la premiere sortie de donnees.
	- Debit : 1 operation tous les D cycles d'horloge.
	
Types de boucles: a bornes fixes, a bornes conditionnelles (sortie de boucle conditionnelle)
Pour determiner le nombre maximal d'iteration de boucles, il suffit des elements suivants :
	1. Iterateur constant
	2. Condition de test par rapport a une valeur constante
	3. Un increment constant de l'iterateur

"""
	
import os, sys, logging
import networkx as nx

from SyntheSys.Synthesis.Optimizations import ResourceSharing as RS
from SyntheSys.Synthesis.Graphs import AppCharGraph
from SyntheSys.Analysis import RessourceNode, SelectGroup, TestGroup


"""
######################
TIMING CONTROL
######################

* Pipeline rampup : temps de remplissage du pipeline == duree totale de la traversee du pipe
* Pipeline rampdown : temps de vidage du pipeline == duree totale de la traversee du pipe

L'effet des rampup/rampdown sont negligeable pour les grands pipelines.
-----------------------------------------

There are three types of feedback:
	> data dependent, 
	> control dependent, 
	> inter-block feedback.

DATA FEEDBACK:
	Intra-cycle Feedback: OKAY rien a faire.
	Multi-cycle Feedback: 
		creating a 'n' element shift register to delay 'n' clock cycle.
			> sur le chemin direct (1) et retour (2) soit '2*n' registres
		=> Num Shift Elements = (feed-forward latency)/Initiation Interval (II)
CONTROL FEEDBACK:
	Temps de controle superieur a 1 cycle de d'horloge.
	
-----------------------------------------


"""


	
#=======================================================================
#	Algorithm : Iterative Modulo Exploration
#	1: IMS_EXPLORE(T ) begin
#	2:	Calculate the δ min ;
#	3:	Calculate the δ max ;
#	4:	for δ = δ min to δ max do
#	5:		f δ = δ ∗ T ;
#	6:		for i = 1 to K do
#	7:			M S = Module Selection(f δ );
#	8:			if ESTIMATE_COST() > C best _ solution then
#	9:				continue;
#	10:			Iterative Modulo Scheduling (IM S);
#	11:			Estimate area cost and update;
#	12:		Record the current solution;
#	13:	Compare and pick the best solution;
#	14: end
#=======================================================================
def HardwareOrientedIterativeModuloExploration(TaskGraph, Constraints, FpgaDesign=None):
	"""
	Algorithm : Iterative Modulo Exploration
		APCG       : directed graph with Nodes as vertex
		Throughput : Throughput Constraint
		
	(TS=Time Slot)
	"""
#	BestArea       =
#	
#	MS = ModuleSelection()
#	InitialScheduling = Schedule(TaskGraph, MS)
#	BestThroughput    = WorstSchedulingThroughput(TaskGraph)
		
	# Candidate circuit modules set is determined for each task based on the input library of circuit modules and the synthesis constraints
	TaskMapCandidates, InputTask, OutputTask=RS.CandidateModules(
							TaskGraph=TaskGraph, 
							Constraints=Constraints, 
							FpgaDesign=FpgaDesign
							) 
	# ====> TaskMapCandidates = { Task : [ List, of, candidate, modules], etc.}
#	print("TaskMapCandidates:", '\n'.join([str(k)+":"+str([str(i) for i in v]) for k,v in TaskMapCandidates.items()]))
	if not TaskMapCandidates:
		return None, None, None
#	AllCandidates=RemoveDominated(AllCandidates) # Remove modules that cost is always higher than others for same DII or Throughput
	
	# DII mean Data introduction interval
	# MinDist matrix calculation algorithm used in determing the minimum system data introduction interval (Appendix B1)
	
	#------------------Communication Tasks-----------------
#	OutputTask, InputTask=None, None
#	for Task in TaskGraph.nodes():
#		if Task.IsOutput(): OutputTask=Task
#		elif Task.IsInput(): InputTask=Task
	if InputTask is None: logging.error("Input communication task not found. Scheduling aborted."); return None, {}, -1
	elif OutputTask is None: logging.error("Output communication task not found. Scheduling aborted."); return None, {}, -1
	
	ComModule = TaskMapCandidates[InputTask][0] # TODO : improve module selection
	#------------------------------------------------------

	OutputModules={T:TaskMapCandidates[T] for T in TaskGraph.predecessors(OutputTask) if T in TaskMapCandidates}
	BestSched={}
	for TaskMapping, GlobalDII in RS.ModuleSelections(TaskMapCandidates, OutputModules, Constraints=Constraints):
#	for DII, Freq in DII_Freq_Range(TaskMapCandidates, Cons=C): # Iterate through each feasible DII with corresponding clock frequencies that meet the throughput constraint. 
#		print("#################################")
#		print("## GlobalDII:", GlobalDII)
#		print("## TaskMapping:", ','.join([str(k)+":"+str(v) for k,v in TaskMapping.items()]))
#		print("#################################")
#		input()
		
		# MODULE SELECTION
		# Module selection based on a non-dominated module set
#		TaskMapping=RS.InitialModuleSelection(TaskMapCandidates, Constraints, DII, Freq)
		if not CorrectMS(TaskMapping, TaskGraph): # Vérifie l'ordonnançabilité du module selectionné et le modifie jusqu'à ce que le graphe soit ordonnançable ou qu'il n'y est plus de modifications possible.
			logging.error("Unable to schedule tasks for DII={0} and Freq={1}.".format(DII, Freq))
			sys.exit(1)
#		CreateWCG()
		
		# performs pipeline scheduling and resource sharing based on the current module selection, then updates the module selection and the loop continues.
#		CurSched=EmptyScheduling(TaskMapping, GlobalDII) # Initialize one module per type of module.
		CurSched={ComModule:[InputTask, OutputTask],}
		
#		print("CurSched :", [str(k)+':'+str([str(i) for i in v]) for k,v in CurSched.items()])
#		input()
#		while ModuleSelectionImprovable(TaskGraph, CurSched):
		# PERFORM ITERATIVE MODULO SCHEDULING at each iteration
#		UnscheduleTasks(CurSched)
		
		TaskList=[T for T in TaskGraph.nodes() if not (T.IsInput() or T.IsOutput())]
		TaskList=sorted(TaskList, key=lambda T: Height(T, TaskGraph)) # determine the schedule priority for each operation
		
		CurSched[ComModule]=[None, None]
		Schedule(Task=InputTask, TS=0, Module=ComModule, Scheduling=CurSched)
		Schedule(Task=OutputTask, TS=1, Module=ComModule, Scheduling=CurSched)
		
		InputTask.RecurseNextSetupEarliestStart(TaskMapping, CurSched)
		OutputTask.SetupLatestStart(TaskMapping, OutputTask)
#		print("Initial scheduling:", CurSched)
#		input()
		while len(TaskList):
#			print("TaskList", TaskList)
			Task=TaskList.pop(0)
#			print("--------------")
#			print("Task:", Task)
			# Calculate the scheduling window
			TSMin, TSMax = Task.Makespan() # Calculate the earliest possible start time for each operation

			(TS, SelectedMod, TaskToReplace, TaskShared) = RS.DynamicAllocate(
							GlobalDII   = GlobalDII, 
							Task        = Task, 
							TSMin       = TSMin, 
							TSMax       = TSMax, 
							CurrentSched= CurSched, 
							TaskMapping = TaskMapping, 
							FPGAModel   = Constraints.HwModel, 
							TaskGraph   = TaskGraph,
							FpgaDesign  = FpgaDesign
							)

#			print("TS            :", TS)
#			print("SelectedMod   :", SelectedMod.ID())
#			print("TaskToReplace :", TaskToReplace)
#			print("TaskShared    :", TaskShared)

			if TaskToReplace:
				TaskList.append(TaskToReplace)
				TaskToReplace.Unschedule()
				CurSched[SelectedMod][CurSched[SelectedMod].index(TaskToReplace)]=None

			
			Sched=Schedule(
				Task=Task, 
				TS=TS, 
				Module=SelectedMod, 
				Scheduling=CurSched
				)
				
			if TaskShared is True:
#				for m, TSDict in CurSched.items():
#					print(m, ': ', ", ".join(["{0}:{1}".format(i,item) for i,item in enumerate(TSDict)]))
#				print("==========")
				for T in TaskGraph.nodes():
					T.ResetStartTimes()
				InputTask.RecurseNextSetupEarliestStart(TaskMapping, Sched)
				OutputTask.SetupLatestStart(TaskMapping, OutputTask)
#				input()
#			for m, TSDict in CurSched.items():
#				print(m, ': ', ", ".join(["{0}:{1}, ".format(i,item) for i,item in enumerate(TSDict)]))
#			input()
		
		if Latency(CurSched) < Latency(BestSched):
			BestSched = CurSched
		
	return AppCharGraph.ScheduleToAPCG(BestSched, TaskGraph=TaskGraph, FpgaDesign=FpgaDesign), BestSched, Latency(BestSched)
	
##=======================================================================
#def NoCOrientedIterativeModuloExploration(TaskGraph, NoCMapping, FpgaDesign=None):
#	"""
#	Algorithm : Iterative Modulo Exploration
#		APCG       : directed graph with Nodes as vertex
#		Throughput : Throughput Constraint
#		
#	(TS=Time Slot)
#	"""
#	# Candidate circuit modules set is determined for each task based on the input library of circuit modules and the synthesis constraints
#	TaskMapCandidates, InputTask, OutputTask=RS.NoCCandidateModules(
#							TaskGraph=TaskGraph, 
#							NoCMapping=NoCMapping
#							) 
#	# ====> TaskMapCandidates = { Task : [ List, of, candidate, modules], etc.}
##	print("TaskMapCandidates:", '\n'.join([str(k)+":"+str([str(i) for i in v]) for k,v in TaskMapCandidates.items()]))
#	if not TaskMapCandidates:
#		return None, None, None
##	AllCandidates=RemoveDominated(AllCandidates) # Remove modules that cost is always higher than others for same DII or Throughput
#	
#	# DII mean Data introduction interval
#	# MinDist matrix calculation algorithm used in determing the minimum system data introduction interval (Appendix B1)
#	
#	#------------------Communication Tasks-----------------
#	if InputTask is None: logging.error("Input communication task not found. Scheduling aborted."); return None, {}, -1
#	elif OutputTask is None: logging.error("Output communication task not found. Scheduling aborted."); return None, {}, -1
#	
#	ComModule = TaskMapCandidates[InputTask][0] # TODO : improve module selection
#	#------------------------------------------------------

#	OutputModules={T:TaskMapCandidates[T] for T in TaskGraph.predecessors(OutputTask) if T in TaskMapCandidates}
#	BestSched={}
#	for TaskMapping, GlobalDII in RS.ModuleSelections(TaskMapCandidates, OutputModules, Constraints=Constraints):
#		InputTask.RecurseNextSetupEarliestStart(TaskMapping, Sched)
#		OutputTask.SetupLatestStart(TaskMapping, OutputTask)
##		print("#################################")
##		print("## GlobalDII:", GlobalDII)
##		print("## TaskMapping:", ','.join([str(k)+":"+str(v) for k,v in TaskMapping.items()]))
##		print("## TaskMapping:", [str(i) for i in TaskMapping.values()])
##		print("#################################")
##		input()
#		
#		# MODULE SELECTION
#		# Module selection based on a non-dominated module set
##		TaskMapping=RS.InitialModuleSelection(TaskMapCandidates, Constraints, DII, Freq)
#		if not CorrectMS(TaskMapping, TaskGraph): # Vérifie l'ordonnançabilité du module selectionné et le modifie jusqu'à ce que le graphe soit ordonnançable ou qu'il n'y est plus de modifications possible.
#			logging.debug("Unable to schedule tasks for DII={0} and Freq={1}.".format(DII, Freq))
##		CreateWCG()
#		
#		# performs pipeline scheduling and resource sharing based on the current module selection, then updates the module selection and the loop continues.
#		CurSched=EmptyScheduling(TaskMapping, GlobalDII) # Initialize one module per type of module.
##		print("CurSched	:", [str(k)+':'+str([str(i) for i in v]) for k,v in CurSched.items()])
##		input()
##		while ModuleSelectionImprovable(TaskGraph, CurSched):
#		# PERFORM ITERATIVE MODULO SCHEDULING at each iteration
#		UnscheduleTasks(CurSched)
#		
#		TaskList=[T for T in TaskGraph.nodes() if not (T.IsInput() or T.IsOutput())]
#		TaskList=sorted(TaskList, key=lambda T: Height(T, TaskGraph)) # determine the schedule priority for each operation
#		
#		CurSched[ComModule]=[None, None]
#		Schedule(Task=InputTask, TS=0, Module=ComModule, Scheduling=CurSched)
#		Schedule(Task=OutputTask, TS=1, Module=ComModule, Scheduling=CurSched)
#		
##		print("Initial scheduling:", CurSched)
##		input()
#	
#		while len(TaskList):
##			print("TaskList", TaskList)
#			Task=TaskList.pop(0)
#			# Calculate the scheduling window
#			TSMin, TSMax = Task.Makespan() # Calculate the earliest possible start time for each operation

#			(TS, SelectedMod, TaskToReplace) = RS.DynamicAllocate(
#							GlobalDII   = GlobalDII, 
#							Task        = Task, 
#							TSMin       = TSMin, 
#							TSMax       = TSMax, 
#							CurrentSched= CurSched, 
#							TaskMapping = TaskMapping, 
#							FPGAModel   = Constraints.HwModel, 
#							TaskGraph   = TaskGraph
#							)
##			print("--------------")
##			print("TS:", TS)
##			print("SelectedMod:", SelectedMod)
##			print("TaskToReplace:", TaskToReplace)

#			if TaskToReplace:
#				TaskList.append(TaskToReplace)
#				TaskToReplace.Unschedule()
#				CurSched[SelectedMod][CurSched[SelectedMod].index(TaskToReplace)]=None
#			
#			Sched=Schedule(
#				Task=Task, 
#				TS=TS, 
#				Module=SelectedMod, 
#				Scheduling=CurSched
#				)
#			if TaskShared is True:
#				for T in TaskGraph.nodes():
#					T.ResetStartTimes()
#				InputTask.RecurseNextSetupEarliestStart(TaskMapping, Sched)
#				OutputTask.SetupLatestStart(TaskMapping, OutputTask)
#		
#		if Latency(CurSched) < Latency(BestSched):
#			BestSched = CurSched
#	return AppCharGraph.ScheduleToAPCG(BestSched, TaskGraph=TaskGraph, FpgaDesign=FpgaDesign), BestSched, Latency(BestSched)
	
#=======================================================================
#  CORRECTION DE LA SELECTION INITIALE DE MODULES
#=======================================================================
def CorrectMS(TaskMapping, TaskGraph):
	# SCC (Strongly Connected Component) decomposition of a dependence graph
	# Évalué grace à l'algorithme de détection de SCC de Kosaraju (citation 35)
	for scc in GetSCC(TaskMapping, TaskGraph=TaskGraph):
		for v in scc:
			SetupSmallerLatencyModules(v) 
		validMS=False
		while not validMS:
			(slack, posSlackOps)=minDist(scc) # Vérifie l'ordonnançabilité du SCC courant
			if slack <= 0:
				validMS=True
			else:
				sorted(posSlackOps)
				update=False
				for v in posSlackOps:
					if setSmallerLatencyModule(v):
						update = True
						break
				if not update:
					break
		if not validMS:
			return False
	return True
	
#=======================================================================
def EmptyScheduling(TaskMapping, GlobalDII):
	"""
	Add one module per module type as key.
	"""
	Sched={}
	for T, M in TaskMapping.items():
		if M not in Sched:
			DII = M.GetDataIntroductionInterval()
			SharingCapability = int(GlobalDII/DII)
#			print("T:", T)
#			print("M:", M)
#			print("DII:", DII)
#			print("GlobalDII:", GlobalDII)
#			print("SharingCapability:", SharingCapability)
#			input()
			if SharingCapability<1:
				Sched[M]=[None,]
#				logging.error("[ResourceSharing.AddNewModule] SharingCapability={0}. GlobalDII={1}. DII={2}".format(SharingCapability, GlobalDII, DII))
#				sys.exit(1)
			else:
				Sched[M]=[None for i in range(SharingCapability)]
	return Sched
	
#=======================================================================
def ModuleSelectionImprovable(TaskGraph, CurSched):
	"""
	return True if module selection is improvable
	"""
	if len(CurSched)==0:
		return True
	else:
		return False
	
#=======================================================================
def GetSCC(TaskMapping, TaskGraph):
	"""
	Return list of Strongly Connected Component cliques.
	"""
	return tuple()
	
#=======================================================================
def UnscheduleTasks(CurSched):
	"""
	Unschedule every task for every modules.
	"""
	for Mod, TaskList in CurSched.items():
		for T in TaskList:
			if T: T.UnSchedule()
	return CurSched
	
#=======================================================================
def Height(Task, TaskGraph):
	"""
	It computes the longest path from P to the end of the 
	graph (the STOP pseudo-operation).
	The larger Height(P) is, the smaller is the amount of 
	slack available to schedule operation P.
	
	For P and Q its successor.
	Height(P)=
		0 if Task is OUTPUT
		max-Q ∈ Succ(P) (Height(Q) + Delay(P,Q)), otherwise.
	"""
	if Task.IsOutput():
		return 0
	else:
		H=max([Height(S, TaskGraph)+Delay(Task, S, TaskGraph) for S in TaskGraph.successors(Task)])
		return H
	
#=======================================================================
def Schedule(Task, TS, Module, Scheduling):
	"""
	Assign a time slot to the Task.
	"""
#	print("Sched: {0} with {1}".format(Task, [str(i) for i in Scheduling[Module]]))
#	input()
	Task.Schedule(CStep=TS, Module=Module)
	if Module in Scheduling:
		TaskList=Scheduling[Module]
#		print("TaskList:", [str(i) for i in TaskList])
		Index=TS % max(1,Module.Latency)
#		print("len(TaskList):", len(TaskList))
#		print("Index:", Index)
		if Index>=len(TaskList):
			for i in range(Index-len(TaskList)+1):
				logging.warning("[Schedule] TS % max(1,Module.Latency)>=len(TaskList) for module '{0}'".format(Module))
				TaskList.append(None)
		if TaskList[Index] is None: TaskList[Index]=Task
		else:
			Scheduling[Module].insert(Index+1, Task)
#			Scheduling[Module].append(Task)
			logging.debug("Conflicted schedule occured : share module (and increase global latency).")
#			logging.error("Conflicted schedule occured : aborted.")
#			raise TypeError
	else:
		Scheduling[Module]=[Task,]
		
	return Scheduling
	
#=======================================================================
def Latency(Scheduling):
	"""
	"""
	if len(Scheduling)==0:
		return float('inf')
	Lat=0
	for M, TList in Scheduling.items():
		for T in TList:
			if T is None: continue
			Lat = max(T.GetStartTime()+M.Latency, Lat) 
	return Lat
#=======================================================================
def Delay(Task, S, TaskGraph):
	"""
	return distance from 
	"""
	PredDict, DistDict=nx.bellman_ford(TaskGraph, Task, weight='NegativeWeight')
	return -DistDict[S]
	
##=======================================================================
#def DII_Freq_Range(Candidates, Cons):
#	"""
#	This range is bounded by the minimum data introduction interval δ min 
#	due to the recurrence constraint and by the maximum data introduction
#	interval δ max due to the maximum clock frequency of the circuit 
#	modules in the library.
#	The maximum initiation interval δ max is bound by the operating 
#	frequency of the slowest circuit module used within the data path.
#	"""
#	#Freq = DII * TC
#	# RMII : recurrence minimum initiation interval
##	RMII   = max([Delay(Cycle)/Distance(Cycle) for Cycle in ListCycles(APCG)])
##	MaxDII = min(min(Mod.GetMaxFreq())/Throughput for Mod in ModList)

#	MinDII  = 1
#	MaxDII  = 1
#	FreqMin = 9000
#	for Task, CandidateList in Candidates.items():
#		for C in CandidateList:
#			MinDII=min(MinDII, C.GetDataIntroductionInterval())
#			CFreq=C.GetMaxFreq(Cons.HwModel.GetFPGA(FullId=False))
#			if CFreq is None:
#				logging.error("[SyntheSys.Scheduling.DII_Freq_Range] HwModel '{0}' not supported for module '{1}'.".format(Cons.HwModel, C))
#				input()
#				continue
#			FreqMin=min(FreqMin, CFreq)
#	
#	MaxDII = int(FreqMin / Cons.Throughput)
#	
#	for DII in range(MinDII, MaxDII+1):
#		yield (DII, FreqMin)
		
	
	
	






