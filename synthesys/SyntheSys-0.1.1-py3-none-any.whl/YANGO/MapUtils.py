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
def ManDist(C1, C2, ARCG):
	"""
	Return sum of communication volume of both direction of arc between two IPs.
	"""
	if ARCG.has_edge(C1, C2):
#		print("ARCG[{0}][{1}] =".format(C1, C2), ARCG[C1][C2]['ManhattanDist'])
		return ARCG[C1][C2]['ManhattanDist']
	else:
#		print("Skip", C1, C2)
		return 0
	
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
		
	for CurrentIP in Mapping:
		if not CurrentIP in APCG: continue
		for SuccessorIP in APCG.successors(CurrentIP):
			if SuccessorIP in Mapping:
				CurrentIPCoord, SuccessorIPCoord=Mapping[CurrentIP], Mapping[SuccessorIP]
				ManhattanDist=ManDist(C1=CurrentIPCoord, C2=SuccessorIPCoord, ARCG=ARCG)
#				if CurrentIPCoord is None and SuccessorIPCoord is None:
#					# Both are not mapped node 
##					MDList=[e["ManhattanDist"] for n0, n1, e in UARCG.edges(data=True)]
##					ManhattanDist=min(MDList) if len(MDList)>0 else 0
#					ManhattanDist=0
#				elif CurrentIPCoord is None:
#					# IP is not mapped 
##						x2,y2=SuccessorCoord
#					MDList=[e["ManhattanDist"] for n0, n1, e in ARCG.edges(nbunch=[SuccessorIPCoord,], data=True) if not (n1 in MappedCoordinates)]
#					ManhattanDist=min(MDList) if len(MDList)>0 else 0
##						for x, y in ARCG.nodes():
##							if (x,y) in MappedCoordinates: continue
##							ManhattanDist=min(abs(x-x2)+abs(y-y2), ManhattanDist)
#						
#				elif SuccessorIPCoord is None:
#					# Successor is not mapped 
##						x1,y1=CurrentIPCoord
#					MDList=[e["ManhattanDist"] for n0, n1, e in ARCG.edges(nbunch=[CurrentIPCoord,], data=True) if not (n1 in MappedCoordinates)]
#					ManhattanDist=min(MDList) if len(MDList)>0 else 0
##						ManhattanDist=0
##						for x, y in ARCG.nodes():
##							if (x,y) in MappedCoordinates: continue
##							ManhattanDist=min(abs(x-x1)+abs(y-y1), ManhattanDist)
#				else:
##					if SuccessorIPCoord==CurrentIPCoord:
##						logging.critical("[CalculateCost] Successor ({0}) and current ({1}) have the same coordinates: aborted.".format(SuccessorIP, CurrentIP))
##						logging.critical("[CalculateCost] Current mapping: \n{0}.".format("\n".join(["{0} => {1}".format(k,v) for k,v in Mapping.items()])))
##						raise TypeError
#					# Really mapped node 
##						x1,y1=IPCoord
##						x2,y2=SuccessorCoord
##						ManhattanDist=abs(x1-x2)+abs(y1-y2)
#					ManhattanDist=1
				CommunicationVolume=ComVol(CurrentIP, SuccessorIP, APCG)
				Cost+=CommunicationVolume*ManhattanDist
#	print("Cost:", Cost)
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
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
