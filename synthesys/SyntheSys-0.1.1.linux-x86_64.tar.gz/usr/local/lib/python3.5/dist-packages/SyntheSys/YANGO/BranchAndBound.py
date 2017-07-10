#! /usr/bin/python

import networkx as nx
import math, logging, sys
from YANGO import MapUtils

	
#=======================================================================
class BBTreeNode:
	#-----------------------------
	def __init__(self, APCG, ARCG, DimX, DimY, Parent=None):
		"""
		Init attributes
		"""
		self._Parent=Parent
		self._Children=[]
		self._APCG=APCG
		self._ARCG=ARCG
		self.DimX, self.DimY=DimX, DimY
		self._ChildPosition=0
		if self._Parent is None:
			self._Mapping={}
			# Sort the IPs by communication demand
			self._UnMappedIPList=MapUtils.GetIPListByCom(APCG)
		else:
			self._Mapping=Parent._Mapping.copy()
			self._UnMappedIPList=Parent._UnMappedIPList[:]
	#-----------------------------
	def GenerateChildren(self):
		"""
		return the list of node children sorted by communication demand.
		"""
		for IP in self._UnMappedIPList:
			Child=BBTreeNode(APCG=self._APCG, ARCG=self._ARCG, DimX=self.DimX, DimY=self.DimY, Parent=self)
			Child.Map(IP)
			self._Children.append(Child)
#			print("UnmappedIP:", len(Child._UnMappedIPList), [x._NodeModule.Name for x in Child._UnMappedIPList])
		
		# Set child position for mirror seeking algorithm
		for Child in self._Children:
			Child.SetChildPosition(self._Children.index(Child))
			
		return sorted(self._Children, key=lambda Child: MapUtils.CalculateCost(Child._Mapping, APCG=self._APCG, ARCG=self._ARCG))
	#-----------------------------
	def Map(self, IP):
		"""
		Calculate ideal position and assign nearest available tile.
		"""
		if IP in self._UnMappedIPList:
			Ix, Iy=MapUtils.IdealCoordinates(UIP=IP, Mapping=self._Mapping, APCG=self._APCG)
			if (Ix, Iy)==(-1,-1): Ix, Iy=0,0
			if (Ix, Iy) in self._Mapping.values():
				x,y=MapUtils.NearestAvailableCoord(Ix, Iy, self.DimX, self.DimY, Mapping=self._Mapping)
				self._Mapping[IP]=(x,y)
				self._UnMappedIPList.remove(IP)
				return (x, y)
			else:
				self._Mapping[IP]=(Ix, Iy)
				self._UnMappedIPList.remove(IP)
				return (Ix, Iy)
		else:
			logging.error("[BBTreeNode.Map] IP '{0}' not in UnMapped IP List: skipped.".format(IP))
			return None
	#-----------------------------
	def SetChildPosition(self, Pos):
		"""
		Assign attribute self._ChildPosition
		"""
		self._ChildPosition=Pos
	#-----------------------------
	def CalculateUBC(self):
		"""
		Calculate the Upper Bound Cost.
		UBC = minimal cost of legal descendant leaf node
		"""
		# Choose by greedely mapping the remaining unmapped IPs.
		UnMappedIPList=self._UnMappedIPList[:] # Sorted by decreasing order of their highest communication demand
		Mapping=self._Mapping.copy()
#		if sum([len(v) for k,v in Mapping.items()])==0:
#			return float('Infinity')
#		print("Mapping:", Mapping)
#		print("======> ", sum([len(v) for k,v in Mapping.items()]))
#		input()
		imax=100000
		i=0
		while(len(UnMappedIPList)>0):
			i+=1
			if i>imax:
				logging.error("Unable to calculate upper bound cost. Maybe there is no arc in the APCG. Is the APCG correct ?") 
				sys.exit(1)
#			print("UnMappedIPList:", UnMappedIPList)
			UnMappedIP=UnMappedIPList.pop(0)
			x,y=MapUtils.IdealCoordinates(UnMappedIP, Mapping=Mapping, APCG=self._APCG)
#			print("x,y =", x,y)
			if (x,y)==(-1,-1):
				UnMappedIPList.append(UnMappedIP)
				continue
			if (x,y) in Mapping.values():
				x,y=MapUtils.NearestAvailableCoord(x, y, self.DimX, self.DimY, Mapping=Mapping)
			
#			print("Map:", UnMappedIP, 'to', (x,y))
			Mapping[UnMappedIP]=(x,y)
#			input()
		
		if self.IsLegalNode():
			return MapUtils.CalculateCost(Mapping=Mapping, APCG=self._APCG, ARCG=self._ARCG)
		else:
			return float('Infinity')
	#-----------------------------
	def CalculateLBC(self):
		"""
		Calculate the Lower Bound Cost.
		"""
		# Decomposed into 3 components : Intercommunication(MappedIP) + Intercommunication(NonMappedIP) + Intercommunication(MappedIP and NonMappedIP)
		Mapping=self._Mapping.copy()
		for UnMappedIP in self._UnMappedIPList:
			Mapping[UnMappedIP]=None
		return MapUtils.CalculateCost(Mapping=Mapping, APCG=self._APCG, ARCG=self._ARCG)
	#-----------------------------
	def GetMirror(self, ChildrenIDs=None):
		"""
		Find mirror of this node using its identifier.
		"""
		if self._Parent is None:
			if ChildrenIDs is None: return self
			else:
				Mirror=None
				ChildID=ChildrenIDs.pop(0)
				SelectedChild=self
				while(len(SelectedChild._Children)>=ChildID):
					MirrorPos=abs(len(self._Children)-1-ChildID)
					SelectedChild=self._Children[MirrorPos]
				
					if len(ChildrenIDs)>0:
						ChildID=ChildrenIDs.pop(0)
					else:
						Mirror=SelectedChild
						break
				return Mirror
		elif ChildrenIDs is None: 
			return self._Parent.GetMirror([self._ChildPosition,])
		else:
			return self._Parent.GetMirror([self._ChildPosition,]+ChildrenIDs)
	#-----------------------------
	def IsLeafNode(self):
		"""
		return true if all IPs have been mapped
		"""
		return len(self._UnMappedIPList)==0
	#-----------------------------
	def IsLegalNode(self):
		"""
		return true if node satisfies the bandwidth constraints.
		"""
#		logging.warning("[IsLegalNode] to be done.")
		return True
	#-----------------------------
	def GetMapping(self):
		"""
		return _Mapping attribute.
		"""
		return self._Mapping
	#-----------------------------
	def __repr__(self):
		"""
		return string representation.
		"""
		return self.__str__()
	#-----------------------------
	def __str__(self):
		"""
		return string representation.
		"""
		return "<TREENODE:Mapped={0}{1}>".format(len(self._Mapping), list(self._Mapping.keys()))
#==========================================
def Map(APCG, ARCG, DimX, DimY):
	"""
	Perform the branch and bound mapping algorithm : EPAM-?? (with ?? the routing algorithm).
	Supported routing algorithm:
		XY
		OE (odd-even)
		WF (west-first)
	"""
	RootNode=BBTreeNode(APCG, ARCG, DimX, DimY)
	PriorityQueue=[RootNode,]
	
	MaxUBC=float('Infinity')
	BestMappingCost=float('Infinity')
	BestLeaf=None
	
	Cnt=DimX*DimY
	UBCDict={}
	while(len(PriorityQueue)>0):
#		print("PriorityQueue:", len(PriorityQueue))
		TreeNode=PriorityQueue.pop(0)
		if TreeNode in UBCDict: 
#			print("UBC =",UBCDict[TreeNode])	
			UBCDict.pop(TreeNode)
#		print("Node :", TreeNode)
#		print("MAPPING:\n", "\n".join(["{0} => {1}".format(k,v) for k,v in TreeNode._Mapping.items()]))
		
		for TreeNodeChild in TreeNode.GenerateChildren():
#			print("    > Node child:", TreeNodeChild)
			# Node has a mirror in PriorityQueue
			if TreeNodeChild.GetMirror() in PriorityQueue:
#				print("\tMIRROR ALREADY QUEUED")
				continue
			LBC=TreeNodeChild.CalculateLBC()
#			print("UnmappedIP:", len(TreeNodeChild._UnMappedIPList), [x._NodeModule.Name for x in TreeNodeChild._UnMappedIPList])
#			print("LBC =",LBC, "(MaxUBC =",MaxUBC,")")
#			print()
			if LBC>MaxUBC:
#				print("LBC =",LBC, "(MaxUBC =",MaxUBC,")")
#				print("\tLBC>MaxUB: SKIPPED")
				continue
#			print("UnmappedIP:", len(TreeNodeChild._UnMappedIPList), [x._NodeModule.Name for x in TreeNodeChild._UnMappedIPList])
			if TreeNodeChild.IsLeafNode():
#				print("\tLEAF NODE !!!!!!!!!!!!!!!!!!!!!")
				TreeNodeCost=MapUtils.CalculateCost(Mapping=TreeNodeChild._Mapping, APCG=APCG, ARCG=ARCG)
				if TreeNodeCost<BestMappingCost:
					BestMappingCost=TreeNodeCost
					BestLeaf=TreeNodeChild
			else:
				UBC=TreeNodeChild.CalculateUBC()
				UBCDict[TreeNodeChild]=UBC
#				print("UBC =",UBC)
				if UBC<MaxUBC:
					MaxUBC=UBC
					PriorityQueue.insert(0, TreeNodeChild)
				else:
					PriorityQueue.append(TreeNodeChild)
		
		PriorityQueue=sorted(PriorityQueue, key=lambda x: UBCDict[x])
#		print("Next in PriorityQueue", len(PriorityQueue), "Mapped={0}".format(len(self._Mapping)))
#		print("PriorityQueue", PriorityQueue)
#		Cnt-=1
#		if Cnt==0:
#			logging.critical("To much loops. Mapping failed...")
#			sys.exit(1)
	BestMapping=BestLeaf.GetMapping() if BestLeaf else {}
	return BestMapping, BestMappingCost


















