"""
Partage de ressources : réduction du graph APCG

	Réduction du nombre d'operateurs:
		Si operateur a nombre d'arguments variable :
			Si contraintes de ressources large :
				> type accumulation
			Sinon
				> type partage du temps
		Sinon
			Si contraintes de ressources large :
				> multiplication du nombre d'operateur
			Sinon
				> type partage du temps
			
Reaffectation des taches aux PE.
"""

import logging, os, sys
import networkx as nx

#sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))
from SyntheSys.Analysis import Operation
from SyntheSys.Synthesis.Optimizations import ResourceEstimation
from Utilities.Misc import SyntheSysError


#=======================================================================
def CandidateModules(TaskGraph, Constraints=None, FpgaDesign=None):
	"""
	List candidate modules for each task. 
		APCG        : Node graph
		Constraints : Constraints object
	"""
	TaskMapping={}
	TestMapping={}
	OutputTask=None
	InputTask=None
	for i,Task in enumerate(TaskGraph.nodes()):
		TaskName=Task.GetName()
		ProcessingTask=False
		if Task.IsOutput(): OutputTask=Task
		elif Task.IsInput(): InputTask=Task
		else:
			ProcessingTask=True
		Serv=Task.GetService(Constraints)

		if Serv is None:
			logging.error("[SyntheSys.Synthesis.ResourceSharing.CandidateModules] No such service '{0}' in library.".format(TaskName))
			return {}, None, None
#			continue
		else:
			T=Task if ProcessingTask is True else None
			CModules=Serv.GetModules(Constraints=Constraints, Task=T)
			if not CModules:
				logging.error("[RS.CandidateModules] Cannot find modules associated with service '{0}'.".format(Serv.Name))
				sys.exit(1)
				
			if FpgaDesign is None:
				TaskMapping[Task]=CModules
			else:
				CModulesName=[M.Name for M in CModules]
				TaskMapping[Task]=[M for M in FpgaDesign.ModuleList() if M.Name in CModulesName]

	return TaskMapping, InputTask, OutputTask

#=======================================================================
def RemoveDominated(Candidates, Constraints):
	"""
	List candidate modules for each task. 
	"""
	return Candidates
	
#=======================================================================
def ModuleSelections(TaskMapCandidates, OutputModules, Constraints):
	"""
	Assigns the minimum area circuit module among its candidate module set to that operation.
	The selected circuit module is also configured to have the same bit-width as the operation.
	The initial assignment thus creates the most specific module selection for the dependence
	graph.
	However, if there is a feedback constraint, the initial module selection might not be 
	valid because it may prevent the dependence graph from being schedulable with the 
	current system data introduction interval value.
	
		From AllCandidates, select only those that match DII and Freq constraints.
	"""
	FPGA=Constraints.HwModel.GetFPGA(FullId=False)
	# First get Throughput for module of output tasks/operations
	for MinimalThroughput, GlobalDII in GetThroughputList(OutputModules, HwModel=Constraints.HwModel):
		TaskMappingOneModule={}
		for Task, ModuleList in TaskMapCandidates.items():
			SelectedMod=None
			if not ModuleList: 
				logging.error("Empty list of module for task {0}".format(Task))
				raise TypeError("Empty list of module for task {0}".format(Task))
			# Select module that has the lowest resource footprint
			for M in ModuleList:
				MT=M.GetThroughput(FPGA)
				if MT>=MinimalThroughput:
					if SelectedMod is None:
						SelectedMod=M
					elif SelectedMod.GetUsedResources(FPGA)>M.GetUsedResources(FPGA):
						SelectedMod=M
			if SelectedMod is None :
				logging.warning("No module has a throughput >= {0} for task '{1}'".format(MinimalThroughput, Task))
				SelectedMod=M
			logging.debug("Select Module {0} for Task '{1}'".format(SelectedMod.ID(), Task))
			TaskMappingOneModule[Task]=SelectedMod
	
		yield TaskMappingOneModule, GlobalDII
		
#=======================================================================
def GetThroughputList(OutputModules, HwModel):
	"""
	Get Throughput for module of output tasks/operations
	TODO : Améliorer en scannant le graph et prenant le minimum des débits maximaux.
	"""
	ListOfModules=[]
	for CandidateList in OutputModules.values():
		for C in CandidateList:
			ListOfModules.append(C)
			
	FPGA=HwModel.GetFPGA(FullId=False)
	
	
	ThroughputDict={x.GetThroughput(FPGA):x for x in ListOfModules}
	LastThroughput=None
	for Throughput in sorted(list(ThroughputDict.keys()), reverse=True):
		M = ThroughputDict[Throughput]
		DII=M.GetDataIntroductionInterval()
		if LastThroughput == Throughput: continue
		else: yield Throughput, DII

#--------------------------------------------------------------------
#--------------------------------------------------------------------
#  EXPLORATION DU PARTAGE DES RESSOURCES :
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#Result: t s , m, cOps
def DynamicAllocate(GlobalDII, Task, TSMin , TSMax, CurrentSched, TaskMapping, FPGAModel, TaskGraph, FpgaDesign=None):
	"""
	DynamicAllocate() returns not only the time slot (TS) for the operation to schedule, 
	but also the hardware resource for the operation to bind to. 
	The hardware resource can be either a newly allocated circuit module, or a previously 
	allocated circuit module that is free at the preferred scheduling time slot TS, 
	depending on the algorithm in the DynamicAllocate() function. 
	"""
	logging.debug("Evaluate task {0} for TSmin={1}, TSMax={2}".format(Task, TSMin , TSMax))
	# Récupérer la liste des composants compatibles avec l'operation.
	CompModList=CompatibleAllocatedModules(Task, CurrentSched, TaskMapping) 
	
	# TODO : Fix the WorthShare function
	if (not WorthShare(Task)) or len(CompModList)==0: # Liste vide ou pas intéret de partager (partager coute plus que pas partager).
		if FpgaDesign is None:
			# If allocating module make resources exceed FPGA available resources: force sharing
			RscExceeded, RscEstimated=ResourceEstimation.AllocExceedRsc(FPGAModel, Task, TaskMapping[Task], CurrentSched, TaskGraph=TaskGraph)
			if RscExceeded is True:
		#		if ResourceEstimation.AllocExceedRsc(FPGAModel, Task, TaskMapping[Task], CurrentSched, TaskGraph=TaskGraph) is True: 
				# Force sharing 
				logging.debug("Allocating module make resources exceed the FPGA available resources: force sharing")
				pass
			else:
				# Retourne date d'ordonnancement minimale et nouveau composant (pas de conflit d'operations)
				logging.debug("No worth share or no module yet => Allocate new module, task at TS="+str(TSMin))
				NewModule=TaskMapping[Task].Copy()
				AddNewModule(GlobalDII, CurrentSched, NewModule=NewModule)
				return TSMin, NewModule, None, False
		else:
			NewModule=FpgaDesign.GetUnscheduledEquivalentMod(TaskMapping[Task], CurrentSched)
			logging.debug("Unscheduled Equivalent Module: {0}".format(NewModule))
			if NewModule is None:
				logging.error("[DynamicAllocate] given Fpga design does not contain any '{0}' module.".format(TaskMapping[Task]))
				raise SyntheSysError
			else:
				AddNewModule(GlobalDII, CurrentSched, NewModule=NewModule)
				return TSMin, NewModule, None, False
		
	MaxSimCompC=(0, None, -1, None)
	MaxSimCompNC=(0, None, -1, None)

	logging.debug("Available time slots (TS) : {0}".format(range(TSMin, TSMax+TaskMapping[Task].Latency, TaskMapping[Task].Latency)))
	for TS in range(TSMin, TSMax+1): # Pour chaque cycle d'horloge possible
		# récupérer le composant de la liste de similarité maximale s'il y a des composants dont les opérations ne commencent pas dans ce cycle
		logging.debug("* TS="+str(TS))
		(ConflictedTask, (Comp, Sim))=SelectMaxSimComp(
							GlobalDII    = GlobalDII, 
							TS           = TS, 
							Task         = Task, 
							CompModList  = CompModList, 
							CurrentSched = CurrentSched
							) 
		logging.debug("Select component '{0}' / similarity='{1}' {2}".format(Comp, Sim, '[CONFLICTED]' if ConflictedTask else ''))
		if ConflictedTask is None: # composant sans conflit
			
			logging.debug("Task withtout conflict (Maximal similarity={0})".format(Sim))
			if MaxSimCompNC[2] < Sim:# or MaxSimCompNC[1] is None: 
				MaxSimCompNC=(TS, Comp, Sim)
#			else:
#				logging.debug("Keep comp '{0}' instead of '{1}'".format(MaxSimCompNC[1], Comp))
		else: # Composant avec conflit
			logging.debug("Conflicted task (Maximal similarity={0})".format(Sim))
			if MaxSimCompC[2] < Sim: # Comparaison avec le meilleur composant choisi jusqu'alors
				logging.debug("Maximum similarity ({0}) < New similarity ({1}) ==> Change component.".format(MaxSimCompC[2], Sim))
				
				MaxSimCompC=(TS, Comp, Sim, ConflictedTask) # Met à jour le composant si meilleur niveau de similarité
			else:
				logging.debug("Maximum similarity ({0}) >= New similarity ({1}) ==> Keep old component.".format(MaxSimCompC[2], Sim))
#				MaxSimCompNC=(TS, MaxSimCompC[1], Sim) # Met à jour le composant si meilleur niveau de similarité
				# In case no more resources available
#				if DefaultComp[2] < Sim: 
#					DefaultComp=(TS, Comp, Sim, ConflictedTask)

	# Meilleur composant non conflictuel 
	if not (MaxSimCompNC[1] is None): 
		# S'il existe un meilleur composant non conflictuel : le retourner
		TS, Comp, Sim = MaxSimCompNC
		logging.debug("=> Non-conflicting share at TS="+str(TS))
		return TS, Comp, None, False
	# Meilleur composant conflictuel
	elif not (MaxSimCompC[1] is None):
		# Si désordonnancer la tache conflictuelle du composant conflictuel vaut le coup (associer la tache courante économise des ressources matérielles par rapport à la tache conflictuelle)
		logging.debug("# Conflicting share")
		TS, Comp, OldSim, ConflictedTask = MaxSimCompC
		NewSim = Similarity(ConflictedTask, CurrentSched[Comp])
		if OldSim < NewSim:
			logging.debug("New similarity '{0}' > old similarity '{1}'".format(OldSim, NewSim))
			logging.debug("\t---> unschedule")
			return TS, Comp, ConflictedTask, False
		else:
			logging.debug("New similarity '{0}' <= old similarity '{1}' : do not unschedule.".format(NewSim, OldSim))
	
	
	# No component without conflicted tasks
	if FpgaDesign is None:
		logging.debug("=> No component without conflicting tasks available. Test for resources availability.")
		RscExceeded, RscEstimated=ResourceEstimation.AllocExceedRsc(FPGAModel, Task, TaskMapping[Task], CurrentSched, TaskGraph=TaskGraph)
		if RscExceeded is True: 
			# Force sharing 
			logging.debug("Allocating module make resources exceed the FPGA available resources: force sharing")
			logging.debug("\t---> extend the latency (force sharing)")
			logging.warning("\t---> could be good to divide all throughputs by 2.")
			TS, Comp, OldSim, ConflictedTask = MaxSimCompC
			return TS, Comp, None, True
		else:
			logging.debug("Resources available")
			logging.debug("\t---> Allocate new module, task at TS="+str(TSMin))
			NewModule=TaskMapping[Task].Copy()
			AddNewModule(GlobalDII, CurrentSched, NewModule=NewModule)
			return TSMin, NewModule, None, False
	else:
		NewModule=FpgaDesign.GetUnscheduledEquivalentMod(TaskMapping[Task], CurrentSched)
		if NewModule is None:
			TS, Comp, OldSim, ConflictedTask = MaxSimCompC
			return TS, Comp, None, True
		else:
			AddNewModule(GlobalDII, CurrentSched, NewModule=NewModule)
			return TSMin, NewModule, None, False
		

#====================================================================
def AddNewModule(GlobalDII, CurSched, NewModule):
	"""
	Insert NewModule in CurSched dictionary with appropriate task list length.
	"""
	if NewModule in CurSched:
		logging.error("New module already in schedule dictionary.")
		raise TypeError
	DII = NewModule.GetDataIntroductionInterval()
	SharingCapability = int(GlobalDII/DII)
	if SharingCapability<1:
#		logging.error("[ResourceSharing.AddNewModule] SharingCapability={0}. GlobalDII={1}. DII={2}".format(SharingCapability, GlobalDII, DII))
		CurSched[NewModule]=[None,]
	else:
		CurSched[NewModule]=[None for i in range(SharingCapability)]

#====================================================================
def CompatibleAllocatedModules(Task, CurrentSched, TaskMapping):
	""" 
	return a sublist of allocated modules that are compatible with Task.
	"""
	CompModList=[]
	
	CompModule=TaskMapping[Task]
	for AllocatedModule in CurrentSched.keys():
		if AllocatedModule.Name==CompModule.Name:
			CompModList.append(AllocatedModule)
	return CompModList
	
#====================================================================
def WorthShare(Task):
	"""
	return False if the sharing overhead is larger than the hardware area being saved.
	"""
	return False
	
#====================================================================
def SelectMaxSimComp(GlobalDII, TS, Task, CompModList, CurrentSched):
	"""
	Calcul le partitionnement en cliques de coût minimal sur le graphe de compatibilité 
	pondéré pour trouver le meilleur partage de ressources pour chaque composant. 
	Dans le cas où plus d'un composant sans conflit de ressources, la similarité moyenne de
	chaque composant est calculée. Le composant avec la meilleure similarité moyenne
	est retournée. Si aucun composant non conflictuel ne peut être trouvé, la différence de 
	similarité moyenne est calculée (différence de similarité moyenne entre les opérations 
	conflictuelles et l'opération courante). Le composant avec la meilleure différence de
	similarité moyenne est retournée. 
	"""
	ConfTaskList=[]
	ConfModList=[]
	NoConfModList=[]
	
#	print("CurrentSched:", [str(k)+':'+str(v) for k,v in CurrentSched.items()])
	for Mod in CompModList:
		TaskList = CurrentSched[Mod]
		ModuloTS = TS%max(Mod.Latency,1)
		Conflict = False
		# Detect scheduling conflicts 
#		print("TS:", TS)
#		print("TaskList:", TaskList)
#		print("ModuloTS:",ModuloTS)
		if ModuloTS>=len(TaskList):
			for i in range(ModuloTS-len(TaskList)+1):
				logging.warning("[SelectMaxSimComp] ModuloTS>=len(TaskList) for module '{0}'".format(Mod))
				TaskList.append(None)
#		print("TaskList:", TaskList)
#			logging.error("")
#			sys.exit(1)
		if TaskList[ModuloTS] is None:
			Conflict=False
			NoConfModList.append(Mod)
		else:
			Conflict=True
			ConfModList.append(Mod)
			ConfTaskList.append(TaskList[ModuloTS])
			
	if len(NoConfModList)==1:
		M=NoConfModList[0]
		return None, (M, Similarity(Task, CurrentSched[M]))
		
	elif len(NoConfModList)>1:
		SList=[(M, Similarity(Task, CurrentSched[M]))for M in NoConfModList]
		SList=sorted(SList, key=lambda MTuple: MTuple[1], reverse=True)
		SelectedModule, Sim=SList[0]
		return None, (SelectedModule, Sim)
	else:
		# Only conflicted modules
		# Consider only modules that do not affect the global latency
#		for M in ConfModList:
#			print("M:", M, "CurrentSched[M]=", CurrentSched[M], "(Ref:{0})".format(TS))
		MList=[M for M in ConfModList if not AssignCStep(TS, CurrentSched[M])]
		if len(MList)!=0: ConfModList=MList
		
		SList=[(M, Similarity(Task, CurrentSched[M])) for M in ConfModList]
		
		SList=sorted(SList, key=lambda MTuple: MTuple[1], reverse=True)
		
		SelectedModule, Sim=SList[0]
#		print("SelectedModule with", [str(t) for t in CurrentSched[SelectedModule]])
#		input()
		return ConfTaskList[ConfModList.index(SelectedModule)], (SelectedModule, Sim)
		
#====================================================================
def AssignCStep(TS, ConfTasks):
	for T in ConfTasks:
#		print("\tConfTask:", T, "CStep=", T._CStep, "(Ref:{0})".format(TS))
		if T is None: continue
		if T._CStep==TS: return True
	return False
#====================================================================
def Similarity(Task, AssignedTasks):
	"""
	Ce calcul résulte de la somme des poids entre l'opération courante et toutes les 
	opérations affectées à ce composant. 
	Cette somme est divisée par le nombre d'opérations actuellement affectées.
	The three similarities (Port, Source, Sink) are added up.
	"""
	FilteredTasks=[T for T in AssignedTasks if not (T is None)]
	PortSim=Task.PortSimilarity(FilteredTasks)
	SourceSim=Task.SourceSimilarity(FilteredTasks)
	SinkSim=Task.SinkSimilarity(FilteredTasks)
	
	return sum([PortSim, SourceSim, SinkSim])
	
#====================================================================
def minDist(scc):
	dist=nx.shortest_path(G)
#	print("distance from u to v:", dist[u][v])
	
#====================================================================
#--------------------------------------------------------------------
#--------------------------------------------------------------------
#  RAFINEMENT DE LA SELECTION GLOBALE DE MODULE
#--------------------------------------------------------------------
#--------------------------------------------------------------------
def globalMSRefine():
	initialize(mi2f_ree[:])
	for op in DG:
		if notWorthShare(op):
			continue
		for mi in ree_mi2f[:]:
			if moduleType(mi)==MS(op) or fullOrEmpty(mi):
				continue
			if compatible(op, mi) and changeable(op, mi):
				setMS(op, mi)
			for M in [CurrentModule, NewModule]: # of op
				update(mi2f_ree[:])
			break


#--------------------------------------------------------------------
#--------------------------------------------------------------------
#  BIT WIDTH MORPHING
#--------------------------------------------------------------------
#--------------------------------------------------------------------
def bitWidthMorph(s):
	for ms in s.sharedModule():
		sort(ms.mi)
		initialize(mi2f_ree[:])
		for mi1 in ms.mi[:-1]:
			if mi2f_ree[mi1].full():
				continue
			mi2 = mi1.next()
			while not mi2f_ree[mi2].empty():
				if mi2.width() == mi1.width():
					mi2=mi2.next()
					continue
				if mi2.width() < mi1.width() - w_compatible:
					break
				bOps=mi2.boundOps()
				sort(bOps)
				for op in bOps:
					if op.width() < mi1.width() - w_compatible:
						break
					bitWidthMorph(mi1.width())
					update(mi2f_ree[mi1]); update(mi2f_ree[mi2])
				mi2=mi2.next()
				











