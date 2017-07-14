import pyswmm
#pyswmm.lib.use("_____REAL___swmm5")


from pyswmm import Simulation, FlowRouting, Nodes, RunoffRouting

with Simulation('TestModel1_weirSetting.inp') as sim:
    J1 = Nodes(sim)["J1"]
    flow_route = FlowRouting(sim)
    runoff_route = RunoffRouting(sim)
    
    sim.step_advance(300)
    print(sim.start_time)
    for step in sim:
        J1.generated_inflow(20)
        print sim.current_time, J1.flooding, runoff_route.rainfall

    


