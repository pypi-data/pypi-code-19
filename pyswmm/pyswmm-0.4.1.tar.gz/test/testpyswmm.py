from pyswmm import Simulation, Subcatchments, Nodes, Links
from datetime import datetime

#with Simulation('TestModel1_weirSetting.inp') as sim:
with Simulation('model_storage_pump.inp') as sim:
    #sim.start_time = datetime(2011,1,1,0,0,0)
    #sim.end_time = datetime(2011,1,2,0,0,0)

    node = Nodes(sim)["J3"]
    link = Links(sim)["C2"]
    
    sim.step_advance(10)
    for step in sim:
        print sim.current_time
        print(link.conduit_statistics)
        #print(node.cumulative_inflow)
    sim.report()

