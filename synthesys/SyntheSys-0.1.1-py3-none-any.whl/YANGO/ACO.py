#! /usr/bin/python

import networkx as nx
import math, logging, sys

NB_CTRL_FLITS=2
FLITWIDTH=16

	
#===================================================================
def GetIPListByCom(APCG, IPSet=None):
	"""
	Return a list of APCG nodes sorted by communication requirements.
	"""
#	NeighborDict = nx.average_neighbor_degree(APCG)
#	print("[GetIPListByCom] NeighborDict:")
#	for k,v in NeighborDict.items():
#		print("\t", k, "=>",v)
	DegreeDict=APCG.degree()
#	print("[GetIPListByCom] DegreeDict:")
	SortedIPList=sorted(DegreeDict, key=DegreeDict.get, reverse=True)
#	for IP in SortedIPList:
#		print("\t", IP, "=>", DegreeDict[IP])
#	print("[GetIPListByCom] SortedIPList:", SortedIPList)
	if IPSet is None: return SortedIPList
	else: return list(filter(lambda x: x in IPSet, SortedIPList))
	
#===================================================================
def NearestAvailableCoord(Refx, Refy, DimX, DimY, Mapping):
	"""
	Find nearest available coordinates from specified coordinates.
	"""
	if len(Mapping)>=DimX*DimY:
		logging.critical("No space left. Unable to find available coordinates: mapping failed.")
		logging.critical("{0} Mapped coordinates: {1}.".format(len(Mapping), list(Mapping.values())))
		sys.exit(1)
	Candidates=[(Refx, Refy)]
	def Neighbors(Candidates):
#		print("---\nGiven candidates:", Candidates)
#		print("Manhattan distance:", MD)
		NewCandidates=[]
		Cx,Cy=Refx, Refy
		#LEFT: Add one candidate at extreme left
		MinX=Refx
		for x,y in Candidates:
			if x<MinX: MinX=x;Cx,Cy=x,y
		if Cx>0: NewCandidates.append((Cx-1,Cy))
		#DOWN: decrement y of coordinates under reference
		for x,y in Candidates:
			if y<=Refy: 
				if y>0: NewCandidates.append((x,y-1))
		#RIGHT: Add one candidate at extreme right
		MaxX=Refx
		for x,y in Candidates:
			if x>MaxX: MaxX=x;Cx,Cy=x,y
		if Cx<(DimX-1): NewCandidates.append( (Cx+1,Cy) )
		#UP: increment y of coordinates above reference
		for x,y in Candidates:
			if y>=Refy: 
				if y<(DimY-1): NewCandidates.append((x,y+1))
		return NewCandidates
		
	MappedCoord=Mapping.values()
	while(len(Candidates)>0):
		Candidates=Neighbors(Candidates)
#		print("New Candidates:", Candidates)
#		print("MappedCoord:", MappedCoord)
		for C in Candidates:
			if not (C in MappedCoord):
#				print("Nearest available coordinates of", (Refx, Refy), "is ", C)
				return C
				
	logging.critical("Unable to find available coordinates: mapping failed.")
	logging.critical("{0} Mapped coordinates: {1}.".format(len(Mapping), list(Mapping.values())))
	sys.exit()
	
#===================================================================
def IdealCoordinates(UIP, Mapping, APCG):
	"""
	Return ideal coordinates for an unmapped IP given a Mapped IP list.
	"""
	if len(Mapping)==0: return 0, 0
	TotalComVol=lambda x,y: ComVol(x, y, APCG)+ComVol(y, x, APCG)
	
	ComVolList=[(TotalComVol(UIP, MIP), x,y) for MIP, (x,y) in Mapping.items()]
	X, Y =0, 0
	for CV, x, y in ComVolList:
		X+=CV*x
		Y+=CV*y
	SumComVol=sum([CV for CV, x, y in ComVolList])
	if SumComVol==0:
		return (-1,-1)
	else:
#			print("IdealCoordinates:", int(X/SumComVol), int(Y/SumComVol))
		return int(X/SumComVol), int(Y/SumComVol)
		
#===================================================================
def ComVol(IP1, IP2, APCG):
	"""
	Return sum of communication volume of both direction of arc between two IPs.
	"""
	global NB_CTRL_FLITS, FLITWIDTH
	
	ComVolume=0
	if APCG.has_edge(IP1, IP2):
		ComVolume=APCG[IP1][IP2]['BitVolume']+NB_CTRL_FLITS*FLITWIDTH
		if ComVolume<0:
			logging.critical("[ComVol] ComVolume={0}".format(ComVolume))
			sys.exit(1)
		
	return ComVolume
	
#===================================================================
def CalculateCost(Mapping, APCG, ARCG):
	"""
	Calculate the Cost of total energy consummed by all mapped IPs.
	"""
	MappedCoordinates=Mapping.values()
	if None in MappedCoordinates:
		# Partial cost calculation : min(e(NonMapped))
		UARCG=ARCG.subgraph( [N for N,Attr in ARCG.node.items() if not (N in MappedCoordinates)] )
	Cost=0
	for IP in Mapping:
		for Successor in APCG.successors(IP):
			if Successor in Mapping:
				IPCoord, SuccessorCoord=Mapping[IP], Mapping[Successor]
				if IPCoord is None and SuccessorCoord is None:
					# Both are not mapped node 
					MDList=[e["ManhattanDist"] for n0, n1, e in UARCG.edges(data=True)]
					ManhattanDist=min(MDList) if len(MDList)>0 else 0
				elif IPCoord is None:
					# IP is not mapped 
#						x2,y2=SuccessorCoord
					MDList=[e["ManhattanDist"] for n0, n1, e in ARCG.edges(nbunch=[SuccessorCoord,], data=True) if not (n1 in MappedCoordinates)]
					ManhattanDist=min(MDList) if len(MDList)>0 else 0
#						for x, y in ARCG.nodes():
#							if (x,y) in MappedCoordinates: continue
#							ManhattanDist=min(abs(x-x2)+abs(y-y2), ManhattanDist)
						
				elif SuccessorCoord is None:
					# Successor is not mapped 
#						x1,y1=IPCoord
					MDList=[e["ManhattanDist"] for n0, n1, e in ARCG.edges(nbunch=[IPCoord,], data=True) if not (n1 in MappedCoordinates)]
					ManhattanDist=min(MDList) if len(MDList)>0 else 0
#						ManhattanDist=0
#						for x, y in ARCG.nodes():
#							if (x,y) in MappedCoordinates: continue
#							ManhattanDist=min(abs(x-x1)+abs(y-y1), ManhattanDist)
				else:
					if SuccessorCoord==IPCoord:
						logging.critical("[CalculateCost] Successor and IP have the same coordinates: aborted.")
						logging.critical("[CalculateCost] Current mapping: \n{0}.".format("\n".join(["{0} => {1}".format(k,v) for k,v in Mapping.items()])))
						raise TypeError
					# Really mapped node 
#						x1,y1=IPCoord
#						x2,y2=SuccessorCoord
#						ManhattanDist=abs(x1-x2)+abs(y1-y2)
					ManhattanDist=ARCG[IPCoord][SuccessorCoord]["ManhattanDist"]
				CommunicationVolume=ComVol(IP, Successor, APCG)
				Cost+=CommunicationVolume*ManhattanDist
	return Cost
	
#===================================================================
def FastMapping(APCG, ARCG, DimX, DimY):
	"""
	Calculate the Cost of total energy consummed by all mapped IPs.
	"""
	#----------
	def FastMap(IP, Mapping, APCG):
		if len(Mapping)==0: Ref=int(DimX/2), int(DimY/2)
		else: 
			Ref=IdealCoordinates(IP, Mapping, APCG)
			if Ref==(-1,-1): Ref=int(DimX/2), int(DimY/2)
		if Ref in Mapping.values():
			Mapping[IP]=NearestAvailableCoord(Ref[0], Ref[1], DimX, DimY, Mapping)
		else:
			Mapping[IP]=Ref
	#----------
	
	Mapping={}
	IPList=[]
	# Process node by dicreasing degree indice 
	while len(Mapping)<APCG.order():
		if len(IPList)>0: IP=IPList.pop(0)
		else: IP=[ip for ip in GetIPListByCom(APCG) if not(ip in Mapping)][0]
		UnMappedSuccessors=[IP for IP in APCG.successors(IP) if not(IP in Mapping)]
		for IP in GetIPListByCom(APCG, UnMappedSuccessors):
			if IP in Mapping:
				logging.error("Already mapped IP")
				sys.exit(1)
			FastMap(IP, Mapping, APCG)
			IPList.append(IP)
#		print(len(Mapping))
		if len(IPList)==0 and len(Mapping)==0:
			logging.error("[FastMapping] No IP to map... aborted.")
			break
	ECost=CalculateCost(Mapping, APCG, ARCG)
	
	return Mapping, ECost
	
#===================================================================
def ACOMappingScheduling(TaskGraph, ARCG, BestResult, EvaluateSolution, PheromonesProba):
	"""
	Map and schedule Task graph on ARCG using ACO heuristic algorithm.
		- BestResult can me min() or max() function for any criteria.
		- EvaluateSolution function returns a result value for a given mapping/Scheduling.
		- PheromonesProba function calculates the probability that results lead to good final solution
	"""
	ExplorationFinished=False
	while ExplorationFinished is False:
	
		InitSolution=ACOInit()
		BestResult=EvaluateSolution(InitSolution)
		# Pheromones are the probability that this decision would lead to a good final solution
		PheromonesValues=1/BestResult # initializing the pheromones
	
		for Ant in AntColony(): 
			Candidates=GetCandidates() # Task without predecessors
			
			# local search
			while len(Candidates)>0: # a Task is selected and assigned to a proper tile
				Task=SelectTask()
				Tile.SetTask(Task)
				Candidates.update() # the candidates set can be updated with the tasks that have become eligible, based on the task selected
			
			BestResult=BestOf(EvaluateSolution(Ant), BestResult)# Evaluate solution 
			
		ExplorationFinished=ToBeDone # TODO : The maximum number of generations or evaluations has not been reached
		if ExplorationFinished is False:
			PheromonesValues.update()
			RandomMove(Probability=Pr) # Changing the position of the jobs inside the trace results in different priority values for the scheduling.
			# Loop again
			
	return MaxTotalLatency, TaskMapping, TileMapping
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
