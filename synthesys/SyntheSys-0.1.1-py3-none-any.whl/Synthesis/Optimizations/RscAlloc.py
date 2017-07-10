
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

from SyntheSys.Synthesis.Optimizations import Scheduling

#=======================================================================
def AllocAndSchedule(TaskGraph, Constraints=None, FpgaDesign=None):
	"""
	Reduce TaskGraph graph to fit HW model resources constraints.
	Return a APCG.
	"""
	#----------------PE SHARING------------------
	# Now reduce the APCG according to FPGA constraints
#	APCG=ResourceSharing.FitAPCG(APCG, HwModel)
	APCG, Sched, TSMax=Scheduling.HardwareOrientedIterativeModuloExploration(
					TaskGraph=TaskGraph, 
					Constraints=Constraints, 
					FpgaDesign=FpgaDesign
					)
	if APCG is None:
		logging.error("Scheduling failed.")
		return None, {}, -1
					
	for Node, Neighbor, Data in APCG.edges(nbunch=None, data=True):
#		print("[MapTask] Node '{0}'.".format(Node))
		Data["BitVolume"]=Node.GetOutputVolume()*int(Data["weight"])
#		print("[MapTask] Node '{0}' BitVolume: {1}.".format(Node, Data["BitVolume"]))
	
	return APCG, Sched, TSMax

#=======================================================================
#def TaskMappingSchedule(TaskGraph, NoCMapping, Constraints=None):
#	"""
#	Reduce TaskGraph graph to fit HW model resources constraints.
#	Return a APCG.
#	"""
#	#----------------PE SHARING------------------
#	# Now reduce the APCG according to FPGA constraints
##	APCG=ResourceSharing.FitAPCG(APCG, HwModel)
#	APCG, Sched, TSMax=Scheduling.HardwareOrientedIterativeModuloExploration(
#					TaskGraph=TaskGraph, 
#					Constraints=Constraints
#					)
#	if APCG is None:
#		logging.error("Scheduling failed.")
#		return None, {}, -1
#					
#	for Node, Neighbor, Data in APCG.edges(nbunch=None, data=True):
##		print("[MapTask] Node '{0}'.".format(Node))
#		Data["BitVolume"]=Node.GetOutputVolume()*int(Data["weight"])
##		print("[MapTask] Node '{0}' BitVolume: {1}.".format(Node, Data["BitVolume"]))
#	
#	return APCG, Sched, TSMax
		
#==========================================
def ToPNG(APCG, OutputPath="./"):
	"""
	Generate an image (png) file from networkx graph.
	"""
	A = nx.nx_agraph.to_agraph(APCG)
#	A.node_attr.update(color='red') # ??
	A.layout('dot', args='-Nfontsize=10 -Nwidth=".2" -Nheight=".2" -Nmargin=0 -Gfontsize=8 -Efontsize=8')
	A.draw(os.path.join(OutputPath, 'APCG.png'))
	return True



