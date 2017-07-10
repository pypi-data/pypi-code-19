
#import myhdl
import logging, os
import networkx as nx
from SyntheSys.Analysis.Data import Data
from SyntheSys.Analysis.TestGroup import TestGroup
from SyntheSys.Analysis.Select import SelectOperation

#=========================================================
def ToPNG(DFG, ShowID=False, OutputPath="./"):
	"""
	Call to matplotlib for networkx graph plot as tree.
	"""
	Mapping={}
	for N in DFG.nodes():
		Mapping[N]=N#.NodeID(ShowID)	
	DFGCopy=nx.relabel_nodes(DFG, Mapping, copy=True)
	A = nx.nx_agraph.to_agraph(DFGCopy)
#	try: pass 
#	except: 
#		logging.error("Unable to draw graph (pygraphviz installation or python3 incompatibility may be the cause)")
#		return False
#	A.node_attr.update(color='red') # ??
	A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8')
	if not os.path.isdir(OutputPath):
		os.makedirs(OutputPath)
	A.draw(os.path.join(OutputPath, 'DFG.png'))
	return True
		
#=========================================================
def NewCDFG(ArgDict={}, ReturnList=[]):
	"""
	Receive a networkx graph as argument.
	If has parent: links parents to item node.
	"""	
	DFG=nx.DiGraph()
	Args      = [x.LastAssignment() for x in list(ArgDict.values())]
#	ArgIDs    = map(lambda x: x.NodeID(ShowID), Args)
	Returns   = [x.LastAssignment() for x in ReturnList]
#	ReturnIDs = map(lambda x: x.NodeID(ShowID), Returns)

	ShowID=False
	for i,Arg in enumerate(Args):
#		Dir=Input.GetDirection()
		#----------------------
		Color = "chartreuse"
		DFG.add_node(Arg.NodeID(ShowID), color=Color, style='filled', fillcolor=Color, shape='tripleoctagon')
		
	for i,Returned in enumerate(Returns):
#		Dir=Input.GetDirection()
		#----------------------
		Color = "cadetblue2"
		DFG.add_node(Returned.NodeID(ShowID), color=Color, style='filled', fillcolor=Color, shape='tripleoctagon')
		#--------------------------------------------------------
#		print "Test if in args/returns"
#		if Args.count(ItemNode) or Returns.count(ItemNode):
#			print "add node"
#			DFG.add_node(ItemNode, style='filled', fillcolor=MethodsDict[Item.SyntheSys__CallingMethod])
	#----------------------
	MethodsDict={}
	Colors=["aliceblue", "antiquewhite", "antiquewhite1", "antiquewhite2", "antiquewhite3", "antiquewhite4", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "black", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4"]
	SelectOutputs=[]
	for Item in Data.Instances:
		ItemNode=Item.NodeID(ShowID)#.NodeID(ShowID)
#		-----------------Save methods color---------------------
		if Item.SyntheSys__CallingMethod not in MethodsDict:
			try: MethodsDict[Item.SyntheSys__CallingMethod]=Colors.pop(0)
			except: 
				logging.error("No more colors available for graph display. Keep it white")
				MethodsDict[Item.SyntheSys__CallingMethod]="white"
		#--------------------------------------------------------
#		for D, OpList in Item.GetConsumers(IncludeControl=False):
#			print("OpList:", [str(i) for i in OpList])
#			input()
#			for Op in OpList:
#				if isinstance(Op, SelectOperation):
#					Label=str(False)
#					for SelVal, V in Op.Select.items():
#						if V is Item:
#							Label=str(SelVal)
#					CtrlOutput=Op.TestedData.NodeID(ShowID)
#	#				if not (CtrlOutput in SelectOutputs):
#	#					SelectOutputs.append(CtrlOutput)
#	#				else: continue
#					DFG.add_node(str(Op), style='filled', shape='rectangle', fillcolor=MethodsDict[Item.SyntheSys__CallingMethod])
#					# Link the control output to the SELECT in itself
#					DFG.add_edge(CtrlOutput, str(Op), color='red', arrowhead="dot", style="dashed", label="", labelfontcolor="red")
#					# Link the consummed Data to the SELECT in itself
#					DFG.add_edge(ItemNode, str(Op), color='blue', arrowhead="open", style="dashed", label=Label, labelfontcolor="red")
#					# Link the SELECT in itself to the Selected produced Data
#					DFG.add_edge(str(Op), Op.GetSelectOutput().NodeID(), color='black', arrowhead="open", style="solid", label="", labelfontcolor="red")

	for Item in Data.Instances:
		ItemNode=Item.NodeID(ShowID) # .NodeID(ShowID)

		# Only for vectors----------------------------
		if Item.SyntheSys__Container is None: pass
		else:
			for Key, DataItem in Item.SyntheSys__Container.items():
				Successors=list(DataItem.GetFollowingTracers())
				if len(Successors)==0: continue
				DFG.add_edge(ItemNode, DataItem.NodeID(ShowID), color='black', arrowhead="open", style="solid", label="")
		#---------------------------------------------

		if Item.SyntheSys__Producer is None: pass
		#---------------------------------------------
		elif Item.SyntheSys__Producer.IsSelect():
			Label=str(False)
			for SelVal, V in Item.SyntheSys__Producer.Select.items():
				if V is Item:
					Label=str(SelVal)
			CtrlOutput=Item.SyntheSys__Producer.TestedData.NodeID(ShowID)
			DFG.add_node(str(Item.SyntheSys__Producer), style='filled', shape='rectangle', fillcolor=MethodsDict[Item.SyntheSys__CallingMethod])
			# Link the control output to the SELECT in itself
			DFG.add_edge(CtrlOutput, str(Item.SyntheSys__Producer), color='red', arrowhead="dot", style="dashed", label="", labelfontcolor="red")
			# Link the SELECT in itself to the Selected produced Data
			DFG.add_edge(str(Item.SyntheSys__Producer), Item.SyntheSys__Producer.GetSelectOutput().NodeID(), color='black', arrowhead="open", style="solid", label="", labelfontcolor="red")
			for InputData in Item.SyntheSys__Producer.GetInputs():
				# Link the consumed Data to the very SELECT 
				DFG.add_edge(InputData.NodeID(), str(Item.SyntheSys__Producer), color='blue', arrowhead="open", style="dashed", label=Label, labelfontcolor="red")
				
		#---------------------------------------------
		elif Item.SyntheSys__Producer.IsSwitch():
			Sel=Item.SyntheSys__Producer
			DFG.add_node(str(Sel), style='filled', shape='rectangle', fillcolor=MethodsDict[Item.SyntheSys__CallingMethod])
			DFG.add_edge(Sel.Selector.NodeID(ShowID), str(Sel), color='red', arrowhead="dot", style="dashed", label="", labelfontcolor="red")
			if not (Sel.InputData.SyntheSys__Producer is None):
				if not Sel.InputData.SyntheSys__Producer.IsSwitch():
					DFG.add_edge(Sel.InputData.NodeID(ShowID), str(Sel), color='black', arrowhead="open", style="solid", label="", labelfontcolor="red")
			else:
				DFG.add_edge(Sel.InputData.NodeID(ShowID), str(Sel), color='black', arrowhead="open", style="solid", label="", labelfontcolor="red")
			Label="?"
			for Selection, D in Sel.Outputs.items():
				if D is Item:
					Label=str(Selection)
			Target=ItemNode
			for T in Item.GetFollowingTracers():
				LinkSel(DFG, Sel, T, Label)
			
			continue
		#---------------------------------------------
		for P in Item.GetParents(IgnoreCtrl=True):
#			print("Producer =>", P.SyntheSys__Producer)
#			if not (P.SyntheSys__Producer is None) : 
#				if P.SyntheSys__Producer.IsSwitch(): continue
#				elif P.SyntheSys__Producer.IsSelect(): continue
			PID=P.NodeID(ShowID)
			DFG.add_edge(PID, ItemNode, color='black', arrowhead="open", style="solid", label="")
#			logging.debug("Link: {0} and {1}".format(repr(P), repr(ItemNode)))
		#----------------------
#	input()
	#-------------------------------------------
	# Link dependencies between tests
	for TG in TestGroup.Instances:
		Predecessor=None
		for Position in sorted(TG.TestChain.keys()):
			TestedData=TG.TestChain[Position]
#			print("Predecessor:",Predecessor)
#			print("TestedData:", TestedData)
			if Predecessor is None:
				Predecessor=TestedData
				continue
			DFG.add_edge(Predecessor.NodeID(ShowID), TestedData.NodeID(ShowID), color='red', arrowhead="dot", style="solid", label="Control", labelfontcolor="yellow")
			Predecessor=TestedData
	#-------------------------------------------
		
#	input()
		
	return DFG
		
#------------------------------------------------
def LinkSel(DFG, Sel, T, Label):
	
	if isinstance(T, Data):
		if T.SyntheSys__Producer.IsSwitch():
			LinkSel(DFG, Sel, T.SyntheSys__Producer, Label)
			return
		DFG.add_edge(str(Sel), T.NodeID(), color='blue', arrowhead="open", style="dashed", label=Label, labelfontcolor="blue")
	else:
		DFG.add_edge(str(Sel), str(T), color='blue', arrowhead="open", style="dashed", label=Label, labelfontcolor="blue")
	
	return
		
		
		
		
		
