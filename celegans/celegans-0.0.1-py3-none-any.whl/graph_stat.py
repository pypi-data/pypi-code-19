import networkx as nx
import numpy as np
import pickle
import sys

from time import time

def graph_order(graph):
    return len(graph.nodes())

def graph_size(graph):
    return len(graph.edges())

def graph_density(graph):
    return nx.density(graph)

def graph_largest_cc_diameter(graph):
    largest_cc = max(
            nx.weakly_connected_component_subgraphs(graph),
            key=len)
    return nx.diameter(largest_cc.to_undirected())

stat_list = [
        graph_order,
        graph_size,
        graph_density,
        graph_largest_cc_diameter,
        ]

def run_graph_stat(graph_list):
    n_graphs = len(graph_list)
    n_stats = len(stat_list)
    gs_array = np.empty((n_graphs, n_stats))
    for graph_ix in range(n_graphs):
        graph = graph_list[graph_ix]
        print(len(graph))
        for stat_ix in range(n_stats):
            stat = stat_list[stat_ix]
            start = time()
            gs_array[graph_ix, stat_ix] = stat(graph)
            end = time()
            print('{} seconds elapsed'.format(end-start))
    return gs_array

def get_graph(graph_name):
    graph_file = open(graph_name, 'rb')
    graph = pickle.load(graph_file)
    graph_file.close()
    return graph

if __name__ == '__main__':
    graph_list = []
    for graph_name in sys.argv[1:]:
        graph_list.append(get_graph(graph_name))
    print(run_graph_stat(graph_list))

