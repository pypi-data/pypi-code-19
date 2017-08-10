import networkx as nx
import pandas as pd
from networkx.algorithms.assortativity.mixing import mixing_dict
from networkx.utils import dict_to_numpy_array
from networkx.utils import accumulate
import scipy.stats as stats
import numpy as np  
import matplotlib.pyplot as plt 
import math
import powerlaw
import matplotlib

def degree_rich_club_coefficient(G):
    deg = G.degree()
    rich_club = []
    rich_club_coefficient = 0.0
    for x in range(1,200):
        a  = dict((k, v) for k, v in deg.items() if v > x)
        N = len(a)
        if N == 1:
            break
        nodes = set(a)
        edges = 0
        for start_id, end_id in G.edges(nodes):
            if start_id in nodes:
                if end_id in nodes:
                    edges = edges + 1
        if rich_club_coefficient != edges/((N*(N-1))/2):
            rich_club_coefficient = edges/((N*(N-1))/2) 
            if rich_club_coefficient != 0:
                rich_club.append((x,rich_club_coefficient))
    return rich_club



