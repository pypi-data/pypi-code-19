import networkx as nx
import pandas as pd
import scipy.stats as stats


def node_neighbor_average_degree_xy(G, x='out', y='in', weight=None, nodes=None):
    if nodes is None:
        nodes = set(G)
    else:
        nodes = set(nodes)
    xdeg = G.degree
    ydeg = G.degree
    for start_node_ID in xdeg(nodes):
        neighbors = (nbr for _,nbr in G.edges(start_node_ID) if nbr in nodes)
        for end_node_ID in neighbors:
            nbrdeg_start = G.degree(G[start_node_ID])
            nbrdeg_end = G.degree(G[end_node_ID])
            
            nbrdeg_start.pop(end_node_ID)
            nbrdeg_end.pop(start_node_ID)
            a = []
            b = []
            for n in nbrdeg_start:                
                a.append(nbrdeg_start[n])
            if a:
                degu = (sum(a) / float(len(a))) - 1
            else:
                degu = 1
            for m in nbrdeg_end:
                b.append(nbrdeg_end[m])
            if b:
                degv = (sum(b) / float(len(b))) - 1
            else:
                degv = 1
            
            yield degu,degv         

def secord_order_average_degree(G):
    xy=node_neighbor_average_degree_xy(G)
    x,y=zip(*xy)
    return stats.pearsonr(x,y)[0]