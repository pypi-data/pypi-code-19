
import logging, os
import networkx as nx

from SyntheSys.Analysis.Operation import Operation
from SyntheSys.Analysis.TestGroup import TestGroup

#==========================================
def BuildTaskGraph(Mod):
	"""
	Build a Task graph 
		Nodes  = Operation objects
		Arc    = Data transfert
		Weight = Number of Data
	"""
	#----------------------
	TaskColorDict={}
	Colors=["aliceblue", "antiquewhite", "antiquewhite1", "antiquewhite2", "antiquewhite3", "antiquewhite4", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "black", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4"]
	#----------------------
	TaskGraph=nx.DiGraph()
	
	InputTask  = Operation(Name="INPUT", InputList=[], ExtraArg={})
	OutputTask = Operation(Name="OUTPUT", InputList=[], ExtraArg={})
	TaskGraph.add_node(InputTask, color="black", style='filled', fillcolor="green", shape='component') #, width=1.2

	for Task in Operation.Instances:
		if Task.IsSwitch(): 
			Task=Task.TestGroup
		elif Task.IsSelect(): 
			Task=Task.SelectGroup
		TaskName=Task.GetName()
		#----------------------
		if not TaskName in TaskColorDict:
			try: TaskColorDict[TaskName]=Colors.pop(0)
			except: 
				logging.warning("No more colors available for Task graph display. Keep it white")
				TaskColorDict[TaskName]="white"
		#----------------------
		if TaskName in ["__setitem__",]: continue
		TaskGraph.add_node(Task, color="black", style='filled', fillcolor=TaskColorDict[TaskName], shape='component') # , width=1.2 shape='tripleoctagon')
		
		# Look for outputs
		TaskOutputs=Task.GetOutputs()
		
		W=GetOutputWeigth(TaskOutputs)
		if len(TaskOutputs)>0:
			NextTasks=Task.GetNextTasks(SkipBranch=False)
			if len(NextTasks)==0:
				ToOutput=True
				# Check if no testgroup use output as test
				for TG in TestGroup.Instances:
					for TD in TG.TestChain.values():
						for TO in TaskOutputs: 
							if TD is TO:
								ToOutput=False
								TaskGraph.add_edge(Task, TG, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
								break
				if ToOutput is True:
					TaskGraph.add_edge(Task, OutputTask, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
					for O in Task.GetOutputs():
						Add=True
						for I in OutputTask.GetInputs():
							if O is I: Add=False
						if Add is True: OutputTask.GetInputs().append(O)
						O.SyntheSys__Children[OutputTask]=[]
				continue
			for NT in NextTasks:
#				InputTask.AddNextTask(NT)
				if isinstance(Task, TestGroup):
					W=len(NT.GetInputs())
					W+=1 # For SELECT Sync
#				else: 
#					W=len(Task.GetOutputs())
				TaskGraph.add_edge(Task, NT, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
		elif len(TaskOutputs)==0:
			if Task is InputTask:
				for T in Operation.Instances:
					W=GetOutputWeigth(T.GetOutputs())
					if (T is OutputTask) or (T is InputTask): continue
					if T.IsSwitch(): T=T.TestGroup
					elif T.IsSelect(): continue
					PrevTasks=T.GetPreviousTasks(SkipBranch=True)
#					print("PrevTasks:",PrevTasks)
					if len(PrevTasks)==0:
#						print("INPUT>", T, "| prev:", "\n\t".join([str(N) for N in PrevTasks]))
#						W=len(T.GetInputs())
						W=sum([GetOutputWeigth([i,]) for i in T.GetInputs()])
						TaskGraph.add_edge(InputTask, T, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
						for I in T.GetInputs():
							Add=True
							for O in InputTask.GetOutputs():
								if I is O: Add=False
							if Add is True: InputTask.Outputs.append(I)

			else:
				if not (Task is OutputTask):
					TaskGraph.add_edge(Task, OutputTask, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
					for O in Task.GetOutputs():
						Add=True
						for I in OutputTask.GetInputs():
							if O is I: Add=False
						if Add is True: OutputTask.GetInputs().append(O)
						O.SyntheSys__Children[OutputTask]=[]
		else:
			raise TypeError("[SyntheSys.Analysis.TaskGraph.BuildTaskGraph] Negative number of outputs !")
			
	#----------------------
	for TG in TestGroup.Instances:
		DataList=[]
		# Selectors inputs
		Selectors=TG.GetSelectors()
	#			W=list(Selectors)
		W=1
		for S in Selectors:
			Skip=False
			for D in DataList:
				if D is S.InputData:
					Skip=True
					break
			if Skip: continue
			DataList.append(S.InputData)
			if S.InputData.SyntheSys__Producer is None:
#				print("EdgeData:", TaskGraph.get_edge_data(InputTask, TG, default={'weight':0}))
				W+=TaskGraph.get_edge_data(InputTask, TG, default={'weight':0})["weight"]
				TaskGraph.add_edge(InputTask, TG, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
#				for I in TG.GetInputs():# Uncomment in the future
#					Add=True
#					for O in InputTask.Outputs:
#						if I is O: Add=False
#					if Add is True: InputTask.Outputs.append(I)
			else:
				TaskGraph.add_edge(S.InputData.SyntheSys__Producer, TG, weight=W, NegativeWeight=-W, label="{0}".format(W), arrowhead="open")
			
	Mod.SetTaskGraph(TaskGraph)			
#	print("Nodes:", [T.GetName() for T in TaskGraph.nodes()])
#	input()
	return TaskGraph
		
#==========================================
def ToPNG(TaskGraph, OutputPath="./"):
	"""
	Generate an image (png) file from networkx graph.
	"""
	Mapping={}
	for N in TaskGraph.nodes():
		Mapping[N]=str(N)
	GraphCopy=nx.relabel_nodes(TaskGraph, Mapping, copy=True)
	A = nx.nx_agraph.to_agraph(GraphCopy)
#	try: pass
#	except: 
#		logging.error("Unable to draw TaskGraph graph (pygraphviz installation or python3 incompatibility may be the cause)")
#		return False
#	A.node_attr.update(color='red') # ??
	A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8 -Efontsize=8')
	A.draw(os.path.join(OutputPath, 'TaskGraph.png'))
	return True
	
#==========================================
def GetOutputWeigth(TaskOutputs):
	"""
	return the number of data as task outputs.
	"""
	W=0
	for TO in TaskOutputs:
#		print("  >TO", str(TO))
#		print("      > TO.SyntheSys__Container:",TO.SyntheSys__Container)
#		print("      > TO.SyntheSys__PythonVar:",TO.SyntheSys__PythonVar)
		if TO.SyntheSys__Container is None : W=max(W,1)
		else: W=max(W, len(TO.SyntheSys__PythonVar))
#	print("W:", W)
#	input()
	return W
	
	
