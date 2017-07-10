
"""
Allocation de ressources : association operateur / composant materiel (non instancie)

	Factorisation d'operateurs:
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
				
				
Interval d'initialisation : nombre de cycle d'horloge a attendre entre deux cycle d'ordonnancement (1 pour pipeline maximum). C'est la contrainte de pipelining !

---------------------------------------------
Partage des resources en cas d'exclusion mutuelle. 
	> If, elif, else avec le meme operateur.
	> return apres chaque condition
---------------------------------------------


"""

import logging, os
import networkx as nx


#=======================================================================
class IPNode:
	NbNodes=0
	#-----------------------------
	def __init__(self, Module, Service=None, Type="Processing", ID=0, BranchNumber=10):
		"""
		Init attributes
		"""
		self._NodeModule  = Module
		self._NodeService = Service
		self._ParamDict   = {}
		self._NodeTasks   = []
		self._ModuleType  = Type
		IPNode.NbNodes   += 1
		self._ID          = IPNode.NbNodes
		self._ConfigOffset= 0
		Sizes             = [P.GetSize() for N,P in self._NodeModule.GetDataPorts().items() if "IN" in P.Direction]
		self._InputsWidth = sum(Sizes)
		self.BranchNumber= BranchNumber
			
	#-----------------------------
	def GetName(self):
		"""
		return name of Module.
		"""
		return self._NodeModule.Name
	#-----------------------------
	def AddTask(self, Task):
		"""
		Add an Task to list of scheduled Tasks
		"""
#		Task.SetNode(self)
#		raise TypeError
		self._NodeTasks.append(Task)
	#-----------------------------
	def GetModule(self):
		"""
		Return node Module
		"""
		return self._NodeModule
	#-----------------------------
	def SetModule(self, M):
		"""
		Return node Module
		"""
		self._NodeModule = M
	#-----------------------------
	def GetService(self):
		"""
		Return node Service
		"""
		return self._NodeService
	#-----------------------------
	def UpdateParamDict(self, ParamDict):
		"""
		Return node scheduled Tasks
		"""
		return self._ParamDict.update(ParamDict)
	#-----------------------------
	def GetTasks(self):
		"""
		Return node scheduled Tasks
		"""
		return self._NodeTasks
	#-----------------------------
	def ClearTasks(self):
		"""
		Return node scheduled Tasks
		"""
		del self._NodeTasks[:]
	#-----------------------------
	def GetTaskAddress(self, Task):
		"""
		Return the address of a task header in a node program memory.
		"""
#		print("Self:", self)
#		print("Task:", Task)
#		print("self._ConfigOffset:", self._ConfigOffset)
#		print("-----------------\nNodeTasks of",self._NodeModule.Name)
#		for T in self._NodeTasks:
#			print("[GetTaskAddress] T:", T)
			
		if not Task in self._NodeTasks: return None
		else: 
			TasksNbTargets = []
			for T in self._NodeTasks:
				if T is Task: break
				TasksNbTargets.append(max(len(T.GetNextTasks()), 1))
				
			return sum(TasksNbTargets)+self._ConfigOffset
	#-----------------------------
	def GetDataID(self, Type="HEADER_CONFIG", MemoryRead=False, Branch=None, NbBranch=None, FlitWidth=16, StartIndex=0, TaskID=0):
		"""
		Return Data identifier of a packet HEADER, for a given data path (graph edge).
		If CurrentTask is None, it means that it is a communication task.
		"""
#		print("Node:", self)
#		print("Type:", Type)
#		print("TaskID:", TaskID)
#		print("StartIndex:", StartIndex)
#		print("NbBranch:", NbBranch)
#		print("Branch:", Branch)
#		if input()=='O': raise TypeError
		TestTypes=["TESTRUN", "DATARUN"]
		AcceptedConfTypes=["RUNNING", "HEADER_CONFIG", "MULTICAST_CONFIG", "CONSTANT_CONFIG", "READ_HEADER_CONFIG", "READ_MULTICAST_CONFIG", "REDUCE_INPUT_NUMBER", "BRANCH_CONFIG"]+TestTypes
		if Type=="RUNNING":
			TypeID=0
		elif Type=="BRANCH_CONFIG":
			TypeID=3
			input()
		elif Type in TestTypes:
			TypeID=TestTypes.index(Type)
		elif Type in ["HEADER_CONFIG", "MULTICAST_CONFIG", "CONSTANT_CONFIG", "READ_HEADER_CONFIG", "READ_MULTICAST_CONFIG", "REDUCE_INPUT_NUMBER"]:
			TypeID=1
		elif not Type in AcceptedConfTypes:
			logging.error("[RessourceNode.GetDataID] Given type '{0}' not as supported type ({1})".format(Type, AcceptedConfTypes))
			raise TypeError("Unsupported type") 
		else:
			raise TypeError("Unsupported type") 

		if Type in ["RUNNING", "CONSTANT_CONFIG", "REDUCE_INPUT_NUMBER"]:
			Index  = int(StartIndex)
			TaskID = TaskID
		else:
			Index  = 1 if MemoryRead==True else 0
			TaskID = 0
		
#		print("self._ModuleType:", self._ModuleType)
		if self._ModuleType=="Processing":
			IndexBitWidth= int(self._InputsWidth/FlitWidth-1).bit_length()
		elif self._ModuleType=="Control":
			IndexBitWidth= (self.BranchNumber-1).bit_length() 
		elif self._ModuleType=="MapReduce":
			IndexBitWidth=int(15).bit_length()
		else:
			logging.error("Node type should be either 'Processing' or 'Control'. Given {0}.".format(self._ModuleType))
			raise TypeError

		if Branch is None:
			TypeBitWidth=1
			TaskBitWidth  = int(FlitWidth/2)-IndexBitWidth-TypeBitWidth
			DataIDStringTemplate = "{0:0"+str(TaskBitWidth)+"b}{1:0"+str(IndexBitWidth)+"b}{2:0"+str(TypeBitWidth)+"b}"
			DataIDString         = DataIDStringTemplate.format(TaskID, Index, TypeID)
		else:
			TypeBitWidth=2
			if NbBranch:
				BranchBitWidth   = int(NbBranch-1).bit_length()
				TaskBitWidth     = int(FlitWidth/2)-IndexBitWidth-TypeBitWidth-BranchBitWidth
				RequiredBitWidth =BranchBitWidth+TaskBitWidth+IndexBitWidth+TypeBitWidth+FlitWidth/2
#				print("* FlitWidth:", FlitWidth)
#				print("TypeBitWidth:", TypeBitWidth)
#				print("IndexBitWidth:", IndexBitWidth)
#				print("TaskBitWidth:", TaskBitWidth)
#				print("BranchBitWidth:", BranchBitWidth)
#				print("=> RequiredBitWidth:", RequiredBitWidth)
				#-----------------------------
				assert (RequiredBitWidth==FlitWidth), "Required bit width {0} not equal to Flitwidth".format(RequiredBitWidth, Flitwidth)
				assert (Branch.bit_length()<=BranchBitWidth), "Required bit width for the 'Branch' field ({0}=>{1} bits) exceeds the available bits ({2}).".format(Branch, Branch.bit_length(), BranchBitWidth)
				assert (TaskID.bit_length()<=TaskBitWidth), "Required bit width for the 'TaskID' field ({0}=>{1} bits) exceeds the available bits ({2}).".format(TaskID, TaskID.bit_length(), TaskBitWidth)
				assert (Index.bit_length()<=IndexBitWidth), "Required bit width for the 'Index' field ({0}=>{1} bits) exceeds the available bits ({2}).".format(Index, Index.bit_length(), IndexBitWidth)
				assert (TypeID.bit_length()<=TypeBitWidth), "Required bit width for the 'TypeID' field ({0}=>{1} bits) exceeds the available bits ({2}).".format(TypeID, TypeID.bit_length(), TypeBitWidth)
				
				if self._ModuleType=="Control":
					assert BranchBitWidth!=0, "Available bits ({0}) for the 'Branch' field is zero.".format(BranchBitWidth)
				assert TaskBitWidth!=0, "Available bits ({0}) for the 'TaskID' field is zero.".format(TaskBitWidth)
				assert IndexBitWidth!=0, "Available bits ({0}) for the 'Index' field is zero.".format(IndexBitWidth)
				assert TypeBitWidth!=0, "Available bits ({0}) for the 'TypeID' field is zero.".format(TypeBitWidth)
				#-----------------------------
				
				DataIDStringTemplate = "{0:0"+str(BranchBitWidth)+"b}{1:0"+str(TaskBitWidth)+"b}{2:0"+str(IndexBitWidth)+"b}{3:0"+str(TypeBitWidth)+"b}"
#				print("DataIDStringTemplate:", DataIDStringTemplate)
#				print("Branch, TaskID, Index, TypeID:", Branch, TaskID, Index, TypeID)
				DataIDString         = DataIDStringTemplate.format(Branch, TaskID, Index, TypeID)
#				print(DataIDString)
#				print(len(DataIDString))
#				input()
			else:
				logging.error("[RessourceNode.GetDataID] NbBranch should be a non zero number of bits.")
				raise TypeError("[RessourceNode.GetDataID] NbBranch should be a non zero number of bits.")
#		if Type=="CONSTANT_CONFIG":
#		print("TargetTask          :", TargetTask)
#		print("TaskBitWidth        :", TaskBitWidth)
#		print("IndexBitWidth       :", IndexBitWidth)
#		print("TypeBitWidth        :", TypeBitWidth)
#		print("PreviousTasks       :", PreviousTasks)
#		print("CurrentTask         :", CurrentTask)
#		print("TaskID         :", TaskID)
#		print("Index               :", Index)
#		print("Type                :", Type)
#		print("TypeID              :", TypeID)
#		print("DataIDString        :", DataIDString)
#		print("DataID              :", int(DataIDString, 2))
#		input()
		return int(DataIDString, 2)
	#-----------------------------
	def GetType(self):
		"""
		Return node Module type
		"""
		return self._ModuleType
	#-----------------------------
	def GetTargetList(self):
		"""
		Return target node.
		"""
		return [O.GetNode() for O in self._NodeTasks]
#	#-----------------------------
#	def SetCoordinates(self, x, y):
#		"""
#		Set coordinate attributes.
#		"""
#		self._x=x
#		self._y=y
#		return True
#	#-----------------------------
#	def GetCoordinates(self):
#		"""
#		Set coordinate attributes.
#		"""
#		return self._x, self._y
	#-----------------------------
	def GetOutputVolume(self):
		"""
		return the number of bits of outputs.
		"""
		return self._NodeModule.GetOutputDataSize()
	#-------------------------------------------------
	def __str__(self):
		"""
		return string representation.
		"""
		return "{0}:".format(self._ID)+str(self._NodeModule)
	#-------------------------------------------------
	def __repr__(self):
		"""
		return detailed string representation.
		"""
		return "<Node {0}: ".format(self._ID)+str(self._NodeModule)+"/Op:"+str(self._NodeTasks)+">"
















