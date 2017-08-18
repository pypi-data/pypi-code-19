from rdyn.alg.RDyn import RDyn
import scipy.stats as stats
import numpy as np
import math
import networkx as nx


def truncated_power_law(alpha, maxv, minv=1):
    """

    :param maxv:
    :param minv:
    :param alpha:
    :return:
    :rtype: object
    """
    x = np.arange(1, maxv + 1, dtype='float')
    pmf = 1 / x ** alpha
    pmf /= pmf.sum()
    ds = stats.rv_discrete(values=(list(range(minv, maxv + 1)), pmf))

    return ds

####
s=[]
maxi = 1000
s = list(map(int, nx.utils.powerlaw_sequence(maxi, 3)))
print(s)

print((nx.is_valid_degree_sequence(s), sum(s)))

exit()

minx = float(15) / (2 ** (1 / (3 - 1)))
print(minx)
maxi = 1000
while True:
    exp_deg_dist = truncated_power_law(3, maxi, math.ceil(minx))
    print((type(exp_deg_dist)))
    degs = list(exp_deg_dist.rvs(size=1000))
    if nx.is_valid_degree_sequence(degs):
        print((degs, int(minx)))
        break
    else:
        print("NO")
        break
exit()

rdb = RDyn()
rdb.execute(simplified=True)