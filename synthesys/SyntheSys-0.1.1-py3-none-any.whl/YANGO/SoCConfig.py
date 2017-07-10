#! /usr/bin/python
"""
Implement function for system configuration : data path, stimuli values
"""
import os, sys, logging
import collections
import struct

from SyntheSys.YANGO import NoCFunctions
from SyntheSys.Analysis.TestGroup import TestGroup
from SyntheSys.Analysis.SelectGroup import SelectGroup
	

TEST_CODES=["TESTRUN", "DATARUN"]
CONFIG_CODES=["RUNNING", "HEADER_CONFIG", "MULTICAST_CONFIG", "CONSTANT_CONFIG", "READ_HEADER_CONFIG", "READ_MULTICAST_CONFIG", "REDUCE_INPUT_NUMBER", "BRANCH_CONFIG"]+TEST_CODES
	
#========================================================================
def GenStim(TaskStimDict, NoCMapping, Schedule, ComServ, ConstConfig=False):
	"""
	Generate NoC Communication port stimuli from : 
		- TaskStimDict  : a per operation values assignments.           [Operation=>Values]
		- NoCMapping    : mapping dictionnary [Node=>Coordinates]
		- AllocatedAPCG : Mapped and scheduled task communication graph [Node=>Operation]
		
	Payload register : hardcoded name
	"""
	#--------------------
	# Fetch communication port
	AppStimVal=[]
	
	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	
	# Inverse the Scheduling representation (Task=>Node)
	SchedDict={}
	for N,TList in Schedule.items():
		for T in TList:
			SchedDict[T]=N
	
	# GENERATE STIMULI FOR/BY EACH OPERATOR FOR EACH OPERATION (TASK)-------------
	StimValueDict={}
	ValueDict={}
	TaskList=list(TaskStimDict.keys())
#	print("TaskStimDict:", TaskStimDict)
#	input()
	while len(TaskList)>0:
		for Task, ArgValues in TaskStimDict.items():
			if Task.IsInput() or Task.IsOutput(): 
				if Task in TaskList: TaskList.remove(Task)
				continue
#			print("Task:", Task)
#			print("ArgValues:", ArgValues)
#			input()
			Node, Coordinates=GetNode(SchedDict[Task], NoCMapping)
			if Node is None:
				logging.warning("Ignore Node '{0}': no service associated.".format(Coordinates))
				continue
			#-------------------------------------------------
#			print("ArgValues.values():", [len(V) for idx, V in ArgValues.values()])
			# Remove target operation if no more TB values
			if sum([len(V) for Name, V in ArgValues.values()])==0:
#					if sum(map(len, list(ArgValues.values())))==0:
				if Task in TaskList:
					TaskList.remove(Task)
				continue
			#-------------------------------------------------
#			print("Task      :", Task)
#			print("ArgNames  :", [V for V in ArgValues])
#			print("ArgValues :", ArgValues)
#			print("Task inputs:", Task.Inputs)
			DataNames  = []
			TaskValues = []
			Index      = None
			for Idx in sorted(ArgValues.keys()):
				DataName, Values = ArgValues[Idx]
#				print(DataName)
#				print("Values:", ArgValues[Idx])
#				input()
				if len(Values)>0:
#					print("Idx:", Idx, "/ Index:", Index)
					if Index is None: 
						Index=Idx
#						print("First Update Index:", Index)
#					elif Idx>Index+1: break
					# Else, Idx is incremented by hardware
#					print("#***", DataName, "---> Index:", Idx)
					TaskValues.append(Values.pop(0))
#					print("pop:", TaskValues[-1])
					DataNames.append(DataName)
				else: 
#					print("ArgValues :", ArgValues)
#					print(DataName)
#					print("Values:", Values)
#					logging.error("Nothing associated with index {0}".format(Idx))
#					raise TypeError

					# Ignore constant values
					pass
#					break
#				print("> Index:", Index)
			
#				if ConstConfig==True:
#				input()
			#-------------------------------------------------
			# Generate Stimuli by service's interface
			if isinstance(Task, TestGroup):
				Type   = "SWITCH"
				TaskID=Node.GetTaskAddress(Task=Task)
				NbSwitchedData=Task.NbSwitchedData()
				DataID=GenCtrlID(TaskID=TaskID, Idx=Index, NbSwitchedData=NbSwitchedData, FlitWidth=FlitWidth, Type=Type)
#				print("[CTRL] DataID:", DataID)
			else: # TODO : manage SelectGroup
				if ConstConfig is True:
					Type   = "CONSTANT_CONFIG"
				else:
					Type   = "RUNNING"
				TaskID=Node.GetTaskAddress(Task)
				DataID=Node.GetDataID(Type=Type, FlitWidth=FlitWidth, StartIndex=Index, TaskID=TaskID)
#				print("Task:", Task, "=> TaskID:", TaskID)
#				print("               => DataID:", format(DataID, '08X'))
#				for i,t in enumerate(Node._NodeTasks):
#					print(str(Node.GetTaskAddress(t))+':'+str(t))
#				print("=============================")
#				if ConstConfig is True:
#				input()

			if DataID is None:
				logging.error("Task '{0}' is not mapped on node '{1}'. Stimuli generation skipped for this Task.".format(Task, Node))
				continue
			else:
				if ConstConfig is True: TaskValues.insert(0, CONFIG_CODES.index("CONSTANT_CONFIG"))
				Payload=GetNbData(TaskValues)

				TaskValuesFormated=[]
				for TV in TaskValues:
					if isinstance(TV, list) or isinstance(TV, tuple):
						TaskValuesFormated.append([RectifyFormat(x, FlitWidth) for x in TV])
					else:
						TaskValuesFormated.append(RectifyFormat(TV, FlitWidth))
				Stimuli, Vals=ComServ.GenInputStim(TaskValues=TaskValuesFormated, DataID=DataID, X=Coordinates[0], Y=Coordinates[1], PayloadReceived=Payload) 

			#-------------------------------------------------
				# Add node Stimuli to global stimuli
				for Name, Values in Stimuli.items():
					if Name in StimValueDict: StimValueDict[Name]+=Values
					else: StimValueDict[Name]=Values
				
				for Name, Values in Vals.items():
					if Name in ValueDict: ValueDict[Name]+=Values
					else: ValueDict[Name]=Values
			#-------------------------------------------------
	logging.debug("[GenStim] Generation of stimuli completed.")
	
#	print("ValueDict:",ValueDict)
#	input()
	return StimValueDict, ValueDict

#=================================================================
def RectifyFormat(Val, FlitWidth):
	if isinstance(Val, float):
		return IntegerEquivalentToFloat(Val, FlitWidth)
	else:
		return Val

#====================================================================
def IntegerEquivalentToFloat(FloatNum, FlitWidth):
	"""
	"""
	ByteSize=int(FlitWidth/8)
	TypeDict={1:'b', 2:'h', 4:'i', 8:'q'}
	Type=TypeDict[ByteSize]
	FloatFormat='d' if Type=='q' else 'f'
	FloatRep = struct.pack(FloatFormat, FloatNum)
#	print("FlitWidth:", FlitWidth)
#	print("FloatNum:", FloatNum)
#	print("ByteSize:",ByteSize)
#	print("Type:",Type)
#	print("FloatFormat:",FloatFormat)
#	print("FloatRep:",FloatRep)
#	print("struct.pack(",FloatFormat,", FloatNum):", FloatRep, '=>', len(FloatRep))
#	input()
	return struct.unpack(Type, FloatRep)[0]
#========================================================================
def GetNbData(TaskValues):
	"""
	return number of values in TaskValues ignoring data structures.
	"""
	NbData=0
	for V in TaskValues:
		if isinstance(V, list) or isinstance(V, tuple): 
			NbData+=GetNbData(V)
		else: NbData+=1
	return NbData

#========================================================================
def GenerateDataPath(NoCMapping, Schedule, ComNode, ComCoordinates, ComServ, OutputPath="./"):
	"""
	Return dictionary : DataPath = {Node: {TaskAddr: [(DataID, Node, Coordinates, TargetTask)] }}
	Generate a text file with scenarii of trafic.
	"""
	NbBranch=4
	DataPathFilePath=os.path.join(OutputPath, "DataPath.txt")
	
	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	
	# Inverse the Scheduling representation (Task=>Node)
	SchedDict={}
	for M,TList in Schedule.items():
		for T in TList:
			SchedDict[T]=M
	#------------------------------------------------------------------------------
	DataPath={}

	TaskMapDict={}
	for N, C in NoCMapping.items():
		Mod=N.GetModule()
		if not (Mod in Schedule): 
			logging.debug("No tasks scheduled on node '{0}': skipped.".format(N))
			continue
		DataPath[N]={}
		TaskMapDict[N]={}
#		if N==ComNode: continue
		if (N.GetName()=="CtrlDepManager") or (N.GetName()=="SelectCtrl"): continue # Ctrl Dependencies are configured in another function
		for T in Schedule[Mod]:
			if T is None or T.IsOutput(): continue
			CurTaskAddress=N.GetTaskAddress(Task=T)
			TaskMapDict[N][CurTaskAddress]=T
			TargetTasks=T.GetNextTasks(SkipBranch=True)
			#----------------------------------------------------------------------------------
#			print("Task       :", T)	
			for O in T.GetOutputs():
#				print("Output:", O)
#				print("\n>>>",O.SyntheSys__Children)
				for D, TargetTasks in O.GetConsumers(IncludeControl=True): # D==O
#					print("> D, TargetTasks:", D, TargetTasks) 
					for TargetTask in TargetTasks:
#						print("\t> TargetTask:", TargetTask) 
						# Find D in target task inputs
						if TargetTask.IsOutput():
							DataPath[N][CurTaskAddress]=[(None, ComNode, ComCoordinates, TargetTask),]
						elif isinstance(TargetTask, TestGroup):
							TG=TargetTask
							Index, TestedData=TG.GetTestedDataFrom(T)
#							print("T:", T)
#							print("TestedData:", TestedData)
							if not (TestedData is None):
								Node, Coordinates = GetNode(SchedDict[TG], NoCMapping)
		#						print("\t...Node       :", Node)
		#						print("\t...Coordinates:", Coordinates)
								TaskID=Node.GetTaskAddress(Task=TG)
								NbSwitchedData=TG.NbSwitchedData() # TODO : Set from node (all testgroups) not only this testgroup
								DataID=GenCtrlID(TaskID=TaskID, Idx=Index, NbSwitchedData=NbSwitchedData, FlitWidth=FlitWidth, Type="TEST")
		#						DataID=Node.GetDataID(CurrentTask=T, TargetTask=TG, Type="RUNNING", FlitWidth=FlitWidth)
								if CurTaskAddress in DataPath[N]:
									DataPath[N][CurTaskAddress].append((DataID, Node, Coordinates, TG))
								else:
									DataPath[N][CurTaskAddress]=[(DataID, Node, Coordinates, TG),]
						else:
#							StartIndex=0
							for Index, I in enumerate(TargetTask.GetInputs()):
#									print("I     :", I) 
								if I.DataFlow__IsData(D): # Check if it is the same data flow arc
									TargetNode, Coordinates = GetNode(SchedDict[TargetTask], NoCMapping)
#										print("T:", T, "==>", TargetNode)
#										print("\t...TargetNode       :", TargetNode)
#										print("\t...Coordinates:", Coordinates) 
									TaskID=TargetNode.GetTaskAddress(TargetTask)
#										print("TaskID:", TaskID)
#										print("Index:", Index)
#										print("FlitWidth:", FlitWidth)
#										print("NbBranch:", NbBranch)
									if isinstance(TargetTask, SelectGroup):
										Branch = TargetTask.GetBranchID(T)
										PacketID=TargetNode.GetDataID(Type="RUNNING", Branch=Branch, NbBranch=NbBranch, FlitWidth=FlitWidth, StartIndex=Index, TaskID=TaskID)
#											print("Index :", Index) 
#											print("Branch     :", Branch) 
#											print("PacketID   :", PacketID) 
#											print("TargetTask :",TargetTask)
#											input()
#										elif isinstance(TargetTask, TestGroup):
##											DataType="BRANCH_CONFIG"
##											for Position, TestedData in TargetTask.TestChain.items():
##												if I is TestedData:
##													DataType="TESTRUN"
##													Index   = Position
##													Branch  = Position # TODO: Is it good ?
##													break
#											Position, TestedData=TargetTask.GetTestedDataFrom(T)
#											PacketID=TargetNode.GetDataID(Type="BRANCH_CONFIG", Branch=Branch, NbBranch=NbBranch, FlitWidth=FlitWidth, StartIndex=Position, TaskID=TaskID)
									else:
										PacketID=TargetNode.GetDataID(Type="RUNNING", FlitWidth=FlitWidth, StartIndex=Index, TaskID=TaskID)
#										print("SourceTask:", T)
#										print("TargetTask:", TargetTask)
#										print("PacketID:", PacketID, "(hex:{0})".format(hex(PacketID)))
#										input()
#											print("\tStartIndex :", StartIndex) 
#											print("\tPacketID:", PacketID) 
									if CurTaskAddress in DataPath[N]:
										DataPath[N][CurTaskAddress].append((PacketID, TargetNode, Coordinates, TargetTask))
									else:
										DataPath[N][CurTaskAddress]=[(PacketID, TargetNode, Coordinates, TargetTask),]
									break
#									StartIndex+=1
#	input()
	#------------------------------------------------------------------------------
	# Write in a file
	HexFormat="0"+str(int(FlitWidth/4))+"X"
	with open(DataPathFilePath, "w+") as DataPathFile:
		for Node, TargetDict in DataPath.items():
			DataPathFile.write("\nNODE{0} '{1}':".format(NoCMapping[Node], Node.GetName()))
			for TaskAddr in sorted(TargetDict):
				TargetList=TargetDict[TaskAddr]
				DataPathFile.write(("\n\t# TaskAddr={0} (task: {1})").format(TaskAddr, TaskMapDict[Node][TaskAddr]))
				for (TargetDataID, TargetNode, TargetCoordinates, TargetTask) in TargetList:
					DataPathFile.write(("\n\t\t> Target X={0}, Y={1}, DataID={2}, Module={3} (task: {4})").format(TargetCoordinates[0], TargetCoordinates[1], format(TargetDataID if TargetDataID else 0, HexFormat), TargetNode.GetModule().Name, str(TargetTask).strip()))
	#-------------------------------------------------------------------------------
#	print("DataPath:", DataPath)
#	input()
	return DataPath, DataPathFilePath
	
#========================================================================
def DataPathToValues(DataPath, NoCMapping, ComServ, IncludeComNode=False, Multicast=False):
	"""
	Convert data path to values.
	DataPath : 
	"""
	#-------------------------
	ValuesDict={}
	NbTargetDict={}
	for Node, TargetDict in DataPath.items():
		if Node.GetType()=="Communication":
			if IncludeComNode is False: continue
		InfoList=[]
		NbTargetsList=[]
		# TODO : order by coordinates (farest to closest)
		for CurTaskAddress in sorted(TargetDict):
			TargetList=TargetDict[CurTaskAddress]
			(TargetDataID, TargetNode, TargetCoordinates, TargetTask) = TargetList[0]
			InfoList.append(      (TargetDataID, TargetCoordinates) )
			NbTargetsList.append( (TargetDataID, len(TargetList)) )

			for (TargetDataID, TargetNode, TargetCoordinates, TargetTask) in TargetList[1:]:
				InfoList.append(      (TargetDataID, TargetCoordinates) )
				NbTargetsList.append( (TargetDataID, 0) )

		ValuesDict[Node]   = InfoList
		NbTargetDict[Node] = NbTargetsList
		
	#-------------------------
	DataPathStimValues={}
	DataPathValues={}

	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	for Node, InfoList in ValuesDict.items():
		DataList=[]
		Coordinates=NoCMapping[Node]
#			logging.debug("Node: {0}".format(Node))
#			logging.debug("Coordinates: {0}".format(Coordinates))
		for (DataID, TCoord) in InfoList:
#				logging.debug("\tDataID: {0}".format(DataID))
#				logging.debug("\tTCoord: {0}".format(TCoord))
			if DataID is None: 
				Header=NoCFunctions.GenHeader( # TODO: fix the DataID in header
						TargetPosition=TCoord, 
						FlitWidth=FlitWidth,
						DataID=0
						)
			else:
				Header=NoCFunctions.GenHeader( # TODO: fix the DataID in header
						TargetPosition=TCoord, 
						FlitWidth=FlitWidth,
						DataID=DataID
						)
			DataList.append(Header)
#			print("DataID:", DataID, "hex:", hex(DataID))
#			print("Header:", Header, "hex:", hex(Header))
#			input()
		# HEADER CONFIGURATION
		CONFIG_ID=Node.GetDataID(Type="HEADER_CONFIG", FlitWidth=FlitWidth, StartIndex=0, TaskID=0)
#		print("CONFIG_ID:", CONFIG_ID)
		# Add Header configuration Stimuli to global stimuli
		DataList.insert(0, CONFIG_CODES.index("HEADER_CONFIG"))
		Stimuli, Vals=ComServ.GenInputStim(TaskValues=DataList, DataID=CONFIG_ID, X=Coordinates[0], Y=Coordinates[1], PayloadReceived=len(DataList))
		
		for Name, Values in Stimuli.items():
			if Name in DataPathStimValues: DataPathStimValues[Name]+=Values
			else: DataPathStimValues[Name]=Values
		
		for Name, Values in Vals.items():
			if Name in DataPathValues: DataPathValues[Name]+=Values
			else: DataPathValues[Name]=Values
		# MULTICAST CONFIGURATION
		CONFIG_ID=Node.GetDataID(Type="MULTICAST_CONFIG", FlitWidth=FlitWidth, StartIndex=0, TaskID=0)
		NbTargetsList=[]
		for (Addr, NbTargets) in NbTargetDict[Node]:
			NbTargetsList.append(NbTargets)
#				logging.debug("\tAddress {0} => Number of targets: {1}".format(Addr, NbTargets))
		NbTargetsList.insert(0, CONFIG_CODES.index("MULTICAST_CONFIG"))
		NbTargetsStimuli, NbTargetsVals=ComServ.GenInputStim(TaskValues=NbTargetsList, DataID=CONFIG_ID, X=Coordinates[0], Y=Coordinates[1], PayloadReceived=len(NbTargetsList)) 
			
		# Add multicast configuration Stimuli to global stimuli
		for Name, Values in NbTargetsStimuli.items():
			if Name in DataPathStimValues: DataPathStimValues[Name]+=Values
			else: DataPathStimValues[Name]=Values
		
		for Name, Values in NbTargetsVals.items():
			if Name in DataPathValues: DataPathValues[Name]+=Values
			else: DataPathValues[Name]=Values
#	print("DataPathValues:", DataPathValues)
#	input()
	return DataPathStimValues, DataPathValues

#========================================================================
def GenerateCtrlPath(NoCMapping, Schedule, ComNode, ComCoordinates, ComServ, OutputPath="./"):
	"""
	Return dictionary : CtrlPath = {Node: {TaskAddr: [(DataID, Node, Coordinates)] }}
	Generate a text file with scenarii of trafic.
	"""
	CtrlPathFilePath=os.path.join(OutputPath, "CtrlPath.txt")
	#------------------------------------------------------------------------------
	# Inverse the Scheduling representation (Node=>Task to Task=>Node)
	SchedDict={}
	for M,TList in Schedule.items():
		for T in TList:
			SchedDict[T]=M

	#------------------------------------------------------------------------------
	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	CtrlPath={}
	# TESTGROUP CONFIGURATION
	for N, C in NoCMapping.items():
		Mod=N.GetModule()
		if not (Mod in Schedule): 
			logging.debug("No tasks scheduled on node '{0}': skipped.".format(N))
			continue
		CtrlPath[N]={}
		if N.GetName()=="CtrlDepManager":
			for TestGroupInst in Schedule[Mod]:
				# Associate switched Data and their branch to a target header 
				#---> for each switched data and for each branch assign a Header
				TaskDict={}
				SwitchedTasks=TestGroupInst.GetSwitchedTasks() # {TestedData:[{InputData1:TargetList1},{InputData2:TargetList2},]}
				for Selector, SwitchDict in SwitchedTasks.items():
					for InputData, TargetList in SwitchDict.items():
#						print("Selector", Selector)
#						print("InputData", InputData)
#						print("TargetList:", [TG._Name for TG in TargetList])
#						input()
						if not (InputData in TaskDict): TaskDict[InputData]=[]
						for TargetTask in TargetList:
							if TargetTask is None:
								TaskDict[InputData].append( (None, ComNode, ComCoordinates) )
							else:
								if not TargetTask in SchedDict:
									logging.error("[SyntheSys.YANGO.SoCConfig.GenerateCtrlPath] Task '{0}' not scheduled. Aborted".format(TargetTask));sys.exit(1)
								TargetNode, TargetCoordinates = GetNode(SchedDict[TargetTask], NoCMapping)
								
#								if not (TargetTask is None):
#									if not (TargetTask in self._NodeTasks):
#					#					print("TargetTask:",TargetTask)
#					#					print("\nself._NodeTasks:",[T for T in self._NodeTasks])
#					#					sys.exit(1)
#										logging.error("[GetDataID] Task '{0}' not scheduled on node '{0}'".format(TargetTask, self))
#										return None
#								PreviousTasks        = TargetTask.GetPreviousTasks(SkipBranch=True)
#								print("PreviousTasks       :", [str(PT) for PT in PreviousTasks])
#								if not (CurrentTask in PreviousTasks) and not (CurrentTask is None):
#									logging.error("[GetDataID] Task '{0}' do not preceed task '{1}'.".format(CurrentTask, TargetTask))
#					#				sys.exit(1)
#									raise NameError
#								elif (CurrentTask is None): # FROM COMMUNICATION NODE
#									Index = StartIndex
#								else:
#									Index = PreviousTasks.index(CurrentTask)
								Index=TestGroupInst.GetSWDataIndex(InputSWData=InputData)
								TaskAddress=TargetNode.GetTaskAddress(TargetTask) 
								DataID=TargetNode.GetDataID(Type="RUNNING", FlitWidth=FlitWidth, StartIndex=Index, TaskID=TaskAddress)
								TaskDict[InputData].append((DataID, TargetNode, TargetCoordinates))
				CtrlPath[N][TestGroupInst]=TaskDict

		elif N.GetName()=="SelectCtrl": 
			# Pour chaque SelectGroup placé sur le Noeud SelectCtrl
			for SelectGroup in Schedule[Mod]:
				TaskDict={}
				# On récupere la sortie selectionnée
				SelectedTasks, OutputData=SelectGroup.GetSelectedTasks() # {SourceTask:[TargetTask0, TargetTask1...]}
				CurTaskAddress=N.GetTaskAddress(Task=T)
				# Pour chaque ensemble Selecteur:List de sources => une seule valeur suffit par SelectGroup
				for TestedData, SelInputList in SelectedTasks.items():
					TargetTasks = OutputData.GetConsumers() # Liste des taches de sortie
					InputData=SelInputList[0] # TODO : choose appropriate Input instead of the first
					for OutData, TargetList in TargetTasks:
						if len(TargetList)==0:
							TaskDict[InputData]=[ (None, ComNode, ComCoordinates), ]
						if not (InputData in TaskDict): TaskDict[InputData]=[]
						for TargetTask in TargetList:
							TargetNode, TargetCoordinates = GetNode(SchedDict[TargetTask], NoCMapping)
							if TargetTask.IsOutput():
								TaskDict[InputData].append( (None, ComNode, ComCoordinates) )
							else:
#									if not SourceTask in SchedDict:
#										logging.error("[SyntheSys.YANGO.SoCConfig.GenerateCtrlPath] Task '{0}' not scheduled. Aborted".format(SourceTask));sys.exit(1)
								TargetNode, TargetCoordinates = GetNode(SchedDict[TargetTask], NoCMapping)
								StartIndex=0
								TaskAddress=TargetNode.GetTaskAddress(TargetTask)
								DataID=TargetNode.GetDataID(Type="RUNNING", FlitWidth=FlitWidth, StartIndex=StartIndex, TaskID=TaskAddress)
								TaskDict[InputData].append((DataID, TargetNode, TargetCoordinates))
					break # => une seule valeur suffit par SelectGroup
				CtrlPath[N][SelectGroup]=TaskDict
		
		else: continue

	#------------------------------------------------------------------------------
	# Write in a file
	with open(CtrlPathFilePath, "w+") as CtrlPathFile:
		for Node, TaskDict in CtrlPath.items():
			for TaskGroupID, Task in enumerate(sorted(TaskDict.keys())):
				TargetDict=TaskDict[Task]
				CtrlPathFile.write("\nNODE{0} '{1}':".format(NoCMapping[Node], Node.GetName()))
				InputDataList=sorted(TargetDict.keys(), key=lambda x: x.NodeID())
				for SwitchID, InputData in enumerate(InputDataList):
					TargetList = TargetDict[InputData]
				
					CtrlPathFile.write(("\n\t# TaskGroupID={0}, SwitchID={1} (input data {2})").format(TaskGroupID, SwitchID, InputData))
					for (TargetDataID, TargetNode, TargetCoordinates) in TargetList:
						CtrlPathFile.write(("\n\t\t> Target X={0}, Y={1}, DataID={2}, Operation={3}").format(TargetCoordinates[0], TargetCoordinates[1], TargetDataID, TargetNode.GetModule().Name))
	#-------------------------------------------------------------------------------
	
	return CtrlPath, CtrlPathFilePath

#========================================================================
def CtrlPathToValues(CtrlPaths, NoCMapping, Schedule, ComServ):
	"""
	Convert data path to values.
		CtrlPaths  : {Node:{Task:{InputData:[(TargetID, TargetNode, TargetCoord), Target1, Target2]}}}
			> Tasks, InputData are sorted and indexes correspond to TaskGroupID and SwitchID respectively.
		NoCMapping : {Node:Coordinates}
	"""
	NbSwitchedData=10
	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	#-------------------------
	ValuesDict={}
	for Node, TaskDict in CtrlPaths.items():
		TaskGroupDict=collections.OrderedDict()
		# FOR EACH TASK GROUP-----------------------------------
		for TaskGroupID, Task in enumerate(sorted(TaskDict.keys())): # Task is either TestGroup or SelectGroup
			SwitchDict=collections.OrderedDict()
			TargetDict=TaskDict[Task]
			# TODO : order by coordinates (farest to closest)
			InputDataList=sorted(TargetDict.keys(), key=lambda x: x.NodeID())
			# FOR EACH SWITCHED DATA-----------------------------------
			for InputDataID, InputData in enumerate(InputDataList):
				TargetList = TargetDict[InputData]
				BranchList=[]
				# FOR EACH BRANCH-----------------------------------
				for BranchID, (TargetDataID, TargetNode, TargetCoordinates) in enumerate(TargetList):
					BranchList.append( (TargetDataID, TargetCoordinates) )
					
				if isinstance(Task, TestGroup):
					# Find coordinate of associated SelectGroup
					SelectNode=None
					for N, C in NoCMapping.items():
						if N.GetName()=="SelectCtrl":
							for SG in Schedule[N.GetModule()]:
								if SG is Task.SelectGroup:
									SelectNode=N
									break
							if SelectNode: break
					if SelectNode:
						SelectCoordinates=NoCMapping[SelectNode]
						TargetDataID = GenCtrlID(TaskID=0, Idx=0, NbSwitchedData=NbSwitchedData, FlitWidth=FlitWidth, Type="STOP")
						BranchList.append( (TargetDataID, SelectCoordinates) )
					else:
						logging.error("[SyntheSys.YANGO.SoCConfig.CtrlPathToValues] Cannot find any schedule or mapping for SelectGroup '{0}'".format(Task.SelectGroup))
						sys.exit(1)
				SwitchDict[InputDataID]=BranchList
			TaskGroupDict[TaskGroupID]=SwitchDict
			
		ValuesDict[Node] = TaskGroupDict
	#-------------------------
		
	if ComServ is None:
		logging.error("No communication service found in design: aborted.")
		sys.exit(1)
		
	CtrlPathValues={}
	CtrlPathStimValues={}
	for Node, TaskDict in ValuesDict.items():
		DataList=[]
		Coordinates=NoCMapping[Node]
#		logging.debug("Node: {0}".format(Node))
#		logging.debug("Coordinates: {0}".format(Coordinates))
#			for (DataID, TCoord) in TaskDict.items():
		for TaskGroupID, SwitchDict in TaskDict.items():
			Payload=0
			for InputDataID, BranchList in SwitchDict.items():
				for (DataID, TCoord) in BranchList:
					Payload+=1
#					logging.debug("\tDataID      : {0}".format(DataID))
#					logging.debug("\tTargetCoord : {0}".format(TCoord))
					if DataID is None: # COMMUNICATION NODE
						Header=NoCFunctions.GenHeader( # TODO: fix the DataID in header
								TargetPosition=TCoord, 
								FlitWidth=FlitWidth,
								DataID=0
								)
					else: # NORMAL/CTRL NODE
						Header=NoCFunctions.GenHeader( # TODO: fix the DataID in header
								TargetPosition=TCoord, 
								FlitWidth=FlitWidth,
								DataID=DataID
								)
					DataList.append(Header)
				
			CtrlID  = GenCtrlID(TaskID=TaskGroupID, Idx=0, NbSwitchedData=NbSwitchedData, FlitWidth=FlitWidth, Type="CONFIGURATION")
			Stimuli, Vals = ComServ.GenInputStim(TaskValues=DataList, DataID=CtrlID, X=Coordinates[0], Y=Coordinates[1], PayloadReceived=Payload) 
		
			# Add Header configuration Stimuli to global stimuli
			for Name, Values in Stimuli.items():
				if Name in CtrlPathStimValues: CtrlPathStimValues[Name]+=Values
				else: CtrlPathStimValues[Name]=Values
			
			for Name, Values in Vals.items():
				if Name in CtrlPathValues: CtrlPathValues[Name]+=Values
				else: CtrlPathValues[Name]=Values
		
	Parameters={"NbSwitchedData":NbSwitchedData,}
	return CtrlPathStimValues, CtrlPathValues, Parameters



#========================================================================
def GenMapReduceConfig(NoCMapping, Schedule, ComServ, OutputPath="./"):
	"""
	Return dictionary : CtrlPath = {Node: {TaskAddr: [(DataID, Node, Coordinates)] }}
	Generate a text file with scenarii of trafic.
	"""
	MapReduceFilePath=os.path.join(OutputPath, "MapReduceConfig.txt")
	
	FlitWidth=int(ComServ.Params["FlitWidth"].GetValue())
	#------------------------------------------------------------------------------
	# Inverse the Scheduling representation (Node=>Task to Task=>Node)
	SchedDict={}
	for M,TList in Schedule.items():
		for T in TList:
			SchedDict[T]=M
	#------------------------------------------------------------------------------
	StimValueDict={}
	ValueDict={}
	with open(MapReduceFilePath, "w+") as MapReduceFile:
		# REDUCE CONFIGURATION
		for N, C in NoCMapping.items():
			if N.GetName()=="Reduce": 
				MapReduceFile.write("\nReduce node {0} '{1}':".format(C, N))
				for ReduceTask in Schedule[N.GetModule()]:
					if ReduceTask is None : continue
					TaskValues = []
					# Get number of inputs
					NbInputs=len(ReduceTask.GetInputs())
					
#					print("ReduceTask:", ReduceTask)
					
					TaskID=N.GetTaskAddress(ReduceTask)
#					print("TaskID:", TaskID)
					MapReduceFile.write(("\n\t# Task={0}(TaskID={1}): {2} inputs").format(ReduceTask, TaskID, NbInputs))
					DataID=N.GetDataID(Type="REDUCE_INPUT_NUMBER", FlitWidth=FlitWidth, StartIndex=0, TaskID=TaskID)
				
#					print("DataID:", DataID)
					TaskValues=[CONFIG_CODES.index("REDUCE_INPUT_NUMBER"), NbInputs]
					Payload=GetNbData(TaskValues)
					Stimuli, Vals=ComServ.GenInputStim(TaskValues=TaskValues, DataID=DataID, X=C[0], Y=C[1], PayloadReceived=Payload) 
					#-------------------------------------------------
					# Add node Stimuli to global stimuli
					for Name, Values in Stimuli.items():
						if Name in StimValueDict: StimValueDict[Name]+=Values
						else: StimValueDict[Name]=Values
				
					for Name, Values in Vals.items():
						if Name in ValueDict: ValueDict[Name]+=Values
						else: ValueDict[Name]=Values
					#-------------------------------------------------

	#------------------------------------------------------------------------------
#	print("ValueDict:",ValueDict)
#	input()
	return StimValueDict, ValueDict

#======================================================================
def GenCtrlID(TaskID, Idx, NbSwitchedData, FlitWidth, Type="CONFIGURATION"):
	"""
	Return Header identifier for a ctrl path.
		Supported types: 
			"CONFIGURATION": Configuration ID
			"TEST"         : ID for a test data input
			"SWITCH"       : ID for switched data input
			"STOP"         : End of branch list ID
	"""
	IdxBitWidth    = int(NbSwitchedData-1).bit_length()
	TaskIDBitWidth = int(FlitWidth/2)-IdxBitWidth
	TypeBitWidth   = 2
	CtrlIDTemplate = "{0:0"+str(TaskIDBitWidth)+"b}{1:0"+str(IdxBitWidth)+"b}{2:0"+str(TypeBitWidth)+"b}"
	
	AcceptedTypes=["CONFIGURATION", "TEST", "SWITCH", "STOP"]
	if not Type in AcceptedTypes:
		logging.error("Given type '{0}' not as supported type ({1})".format(Type, AcceptedTypes))
	Type=AcceptedTypes.index(Type)
	DataIDString = CtrlIDTemplate.format(TaskID, Idx, Type)
#	print("IdxBitWidth    :", IdxBitWidth)
#	print("TaskIDBitWidth :", TaskIDBitWidth)
#	print("TaskID   :", TaskID)
#	print("Idx      :", Idx)
#	print("DataIDString  :", DataIDString)
#	print("DataID        :", int(DataIDString, 2))
#	input()
	return int(DataIDString, 2)
	
#======================================================================
def GetNode(Mod, NoCMapping):
	"""
	return Node and coordinates corresponding to operation O.
	"""
	for Node, Coordinates in NoCMapping.items():
		if Mod==Node.GetModule():
			return Node, Coordinates
	return None, None
	
	
	
	
	




