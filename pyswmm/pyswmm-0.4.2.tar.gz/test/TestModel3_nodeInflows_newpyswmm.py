'''
PySWMM Test 2: Pump Setting and Simulation Results Streaming

Author: Bryant E. McDonnell (EmNet LLC)
Date: 11/15/2016

'''



import os
import sys

import random

from pyswmm import Simulation, Links, Nodes


with Simulation('./TestModel3_nodeInflows.inp') as sim:
    LinkC2 = Links(sim)['C2']
    NodeJ1 = Nodes(sim)['J1']
    
    for ind, step in enumerate(sim):
        print sim.current_time
        if ind > 15:
            NodeJ1.generated_inflow(10)
        #print ind, LinkC2.flow, NodeJ1.total_inflow

    
   
