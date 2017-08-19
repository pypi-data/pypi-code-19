from rdyn.alg.RDyn_v2 import RDynV2
import scipy.stats as stats
import numpy as np
import math
import networkx as nx

rdb = RDynV2(size=1000, iterations=100, max_evts=2)
rdb.execute(simplified=False)

exit()

####
s=[]

print(s)

print(nx.is_valid_degree_sequence(s), sum(s))

exit()

minx = float(15) / (2 ** (1 / (3 - 1)))
print(minx)
maxi = 1000
while True:
    exp_deg_dist = truncated_power_law(3, maxi, math.ceil(minx))
    print(type(exp_deg_dist))
    degs = list(exp_deg_dist.rvs(size=1000))
    if nx.is_valid_degree_sequence(degs):
        print(degs, int(minx))
        break
    else:
        print("NO")
        break
exit()
