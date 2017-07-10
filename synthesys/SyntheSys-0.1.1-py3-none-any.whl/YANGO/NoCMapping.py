#! /usr/bin/python

import networkx as nx
import math, logging, sys

from YANGO import Matrix
from YANGO import BranchAndBound
from YANGO import MapUtils

#=====================================================
def NewTCG(ServiceTree, *Attributes):
	"""
	Create a new directed graph from the specified tree of service.
	"""	
	if len(ServiceTree)==0: return None
	
	G=nx.DiGraph(*Attributes)
	AddServNode(ServiceTree, G)
	return G
	
#=====================================================
def AddServNode(SubServiceTree, G, Parent=None):
	"""
	Recursive function building a directed graph from the specified tree of service.
	"""
	if len(SubServiceTree)==0: return False
	for AService in SubServiceTree:
		if AService.Type!="Activity":
			# Share communication services
#			logging.debug("Share communication service '{0}'".format(AService.Name))
			ComServ=None
			# Seeking for existing communication node
			for AServ in G.node:
				if AServ.Service==None: # Means that it already have a dataflow service
					ComServ=AServ
			if ComServ==None:
				pass # Link with new communication service
			else:
				# Link with already existing communication service
				AService=AServ
				if Parent!=None: G.add_edge(Parent, AService)
				return True
		else:
			# Duplicate activity service
			G.add_node(AService, **SubServiceTree[AService][1]) # SubServiceTree[AServ] =[AServ, Params, Children]
			
		if Parent!=None: G.add_edge(Parent, AService)
		AddServNode(SubServiceTree[AService][2], G, AService) # SubServiceTree[AServ] =[AServ, Params, Children]
		
		return True
		
#=====================================================
def SetNoCParam(G):
	"""
	Return NoC parameters and add position to each edge parameter.
	"""
	if G==None: 
		logging.error("No TCG specified: return empty matrix")
		return {"Dimensions":"0x0"}, [[None]]
	NoCParams={}
	
	NbNodes = G.number_of_nodes()
	logging.debug("Number of NoC nodes: {0}".format(NbNodes))
		
	M = Matrix.Matrix(NbElement=NbNodes)
	DimX, DimY = M.Size()
	Dim="{0}x{1}".format(DimX, DimY)
#	logging.debug("The TCG Number of nodes is {0}. New NoC dimensions : {1}".format(NbNodes, Dim))
	NoCParams["Dimensions"]=Dim
	
	return NoCParams, M
	
#=====================================================
def SetupFlitWidth(ModuleList):
	"""
	Browse Module List and choose the power of two immediatly above the module input width.
	"""
#	raise TypeError
	MaxWidth=2
	for M in ModuleList:
#		print("Mod:", repr(M))
#		input()
#		IPServ.GetInterfaces("BasicBlock", Direction="OUT")
		Width=max([P.GetSize() for PName, P in M.Ports.items()])
		MaxWidth=max(Width, MaxWidth)

	PowersOfTwo=[2**i for i in range(7)]
	for Pow in PowersOfTwo:
		if Pow<MaxWidth: continue
		else: return Pow
	logging.error("[SetupFlitWidth] MaxWidth={0}, PowersOfTwo max={1}. Cannot find the optimal flitwidth for this module list.".format(MaxWidth, max(PowersOfTwo)))
	
	raise TypeError
#=====================================================
#def GetNeighborDegreeDict(G):
#	"""
#	Return a dictionary of NoC, Neighbor indices pairs.
#	"""
#	return nx.average_neighbor_degree(G)
		
#=====================================================
#def NewMeshGraph(DimX, DimY, **Attr):
#	"""
#	Return regular mesh graph.
#	"""
#	Mesh=nx.grid_2d_graph(DimX+1, DimY+1).to_directed()
#	for N1, N2, Attributes in Mesh.edges_iter(data=True):
#		for AName, AValue in Attr.items():
#			Attributes[AName]=AValue
#	return Mesh
		
#=====================================================
def GenerateARCG(DimX, DimY):
	"""
	Return complete graph with edges representing paths in NoC.
	"""
#	print("[GenerateARCG] DimX:", DimX)
#	print("[GenerateARCG] DimY:", DimY)
#	print("[GenerateARCG] Number of nodes:", (DimX)*(DimY))
	ARCG=nx.complete_graph(DimX*DimY).to_directed()
	LabelList=[]
	for x in range(DimX):
		for y in range(DimY):
			LabelList.append( (x,y) )
	LabelMapping={LabelList.index(Label):Label for Label in LabelList}
#	print("[GenerateARCG] LabelList:", LabelList)
#	print("[GenerateARCG] LabelMapping:", LabelMapping)
#	input()
	nx.relabel_nodes(ARCG, LabelMapping, copy=False)
	for N1, N2, Data in ARCG.edges_iter(data=True):
		x1,y1=N1
		x2,y2=N2
		ManhattanDist=abs(x1-x2)+abs(y1-y2)
		Data["ManhattanDist"]=ManhattanDist
		Data["Path"]=GetPath(N1, N2)
	return ARCG
	
#=====================================================
def GetPath(Node1, Node2):
	"""
	Return the list of coordinate tuple of node to go through between Node1, Node2.
	"""
	StartX, StartY=Node1
	EndX, EndY=Node2
	
	CoordList=[]
	if StartX!=EndX:
		for x in range(int(StartX+(EndX-StartX)/abs(EndX-StartX)), EndX+1):
			CoordList.append( (x,StartY) )
	if StartY!=EndY:
		for y in range(int(StartY+(EndY-StartY)/abs(EndY-StartY)), EndY+1):
			CoordList.append( (EndX,y) )
	return CoordList
	
#=====================================================
def ConfigureNoC(FlitWidth, NbCtrlFlits=2):
	"""
	Return the list of coordinate tuple of node to go through between Node1, Node2.
	"""
	BranchAndBound.NB_CTRL_FLITS=NbCtrlFlits
	BranchAndBound.FLITWIDTH=FlitWidth
	return 
	
#==========================================
def Map(APCG, ARCG, DimX, DimY, Algo=None):
	"""
	Perform a mapping of APCG on ARCG using specified algorithm or random.
	"""
	#----------------------------------------
	if Algo is None:
		logging.debug("Use Fast mapping.")
		Mapping, ECost=MapUtils.FastMapping(APCG, ARCG, DimX, DimY)
	#----------------------------------------
	elif Algo=="BranchAndBound":
		logging.debug("Use Branch and Bound mapping algorithm.")
		Mapping, ECost=BranchAndBound.Map(APCG, ARCG, DimX, DimY)
	else:
		logging.error("Algorithm '{0}' not a valid or supported mapping algorithm.".format(Algo))
		sys.exit(1)
		
	return Mapping, ECost


























#	
