import pyswmm
#pyswmm.lib.use("_____REAL___swmm5")


from pyswmm import Simulation, Nodes, Links, Subcatchments

with Simulation('TestModel1_weirSetting.inp') as sim:
    J1 = Nodes(sim)["J1"]
    #flow_route = FlowRouting(sim)
    #runoff_route = RunoffRouting(sim)
    _links = Links(sim)
    
    for link in _links:
        print link.linkid
    for subc in Subcatchments(sim):
        print subc.subcatchmentid

    #print 1/0    
    sim.step_advance(300)
    print(sim.start_time)
    for step in sim:
        J1.generated_inflow(20)
        #print sim.current_time, J1.flooding, runoff_route.rainfall
        #print sim._model.node_statistics("J1", 0)
        #print sim._model.node_statistics("J1", 1)
        #print sim._model.node_statistics("J1", 2)
        #print sim._model.node_statistics("J1", 3)
        #print sim._model.node_statistics("J1", 4)
        
        #print sim._model.link_statistics("C1:C2", 0)
        #print sim._model.link_statistics("C1:C2", 1)
        #print sim._model.link_statistics("C1:C2", 2)

        #print sim._model.subcatch_statistics("S2", 0)
        #print sim._model.subcatch_statistics("S2", 1)

        #print sim._model.system_statistics(0)
        #print sim._model.system_statistics(1)    


