'''
This module contains all the DUMP-related functionalities. These functions
compute nothing per themselves (except trivial stuffs) and rely on core to 
do the heavy lifting.
'''

import os 
from pynusmv_community import core

def dimacs(model, bound, cnf):
    '''
    Saves the DIMACS output for the given `cnf` formula derived from `model`
    unrolled `bound` times
    '''
    os.makedirs("{}/instances/".format(model), exist_ok=True)
    with open("{}/instances/{:03d}.cnf".format(model, bound), 'w') as f:
        f.write(core.to_dimacs(cnf))
        
def mapping(model, bound, cnf):
    '''
    Dumps a CSV file containing a mapping CNF -> SMV variables
    '''
    os.makedirs("{}/mapping/".format(model), exist_ok=True)
    with open("{}/mapping/{:03d}.csv".format(model, bound), 'w') as f:
        
        visited = set()
        for clause in cnf.clauses_list:
            for literal in clause:
                if literal in visited:
                    pass
                else:
                    visited.add(literal)
                    variable = core.cnf_to_be_var(literal)
                    repres   = core.short_var_repr(variable)
                    
                    print("{:3d} ; {}".format(literal, repres), file=f)
                
def communities_raw(model, bound, clusters, graph):
    '''
    Saves text file dumps for the communities stored in the `clusters` of the 
    `graph` derived from `bound` unrolling of the time for `model`. This dump
    contains nothing but the cnf identifiers of the variables
    '''
    os.makedirs("{}/communities/{:03d}".format(model, bound), exist_ok=True)
    l_cluster = [ [core.vertex_to_lit(graph, v) for v in c ] for c in clusters ]
    
    with open("{}/communities/{:03d}/raw.txt".format(model, bound), 'w') as f:
        counter = 0
        for l in l_cluster:
            counter += 1
            # raw information
            text = " ".join([str(x) for x in sorted(l)])
            print( "{:03d} -> {}\n".format(counter, text) , file=f )


def communities_semantic(model, bound, clusters, graph):
    '''
    Saves text file dumps for the communities stored in the `clusters` of the 
    `graph` derived from `bound` unrolling of the time for `model`. This dump
    contains nothing all identifiers. including the ??? for tseitin auxilliary
    variables.
    '''
    os.makedirs("{}/communities/{:03d}".format(model, bound), exist_ok=True)
    s_cluster = [ [core.vertex_repr(graph, v) for v in c ] for c in clusters ]
    
    with open("{}/communities/{:03d}/sem.txt".format(model, bound), 'w') as f:
        counter = 0
        for s in s_cluster:
            counter += 1
            # not-curated info
            text = " ".join(sorted(s))
            print( "{:03d} -> {}\n".format(counter, text) , file=f )
            
def communities_curated(model, bound, clusters, graph):
    '''
    Saves text file dumps for the communities stored in the `clusters` of the 
    `graph` derived from `bound` unrolling of the time for `model`. This dump
    contains nothing all identifiers. except the ??? corresponding to tseitin 
    auxilliary variables.
    '''
    os.makedirs("{}/communities/{:03d}".format(model, bound), exist_ok=True)
    s_cluster = [ [core.vertex_repr(graph, v) for v in c ] for c in clusters ]
    
    with open("{}/communities/{:03d}/curated.txt".format(model, bound), 'w') as f:
        counter = 0
        for s in s_cluster:
            counter += 1
            # not-curated info
            text = " ".join(sorted(filter(lambda x: x!="???", s)))
            print( "{:03d} -> {}\n".format(counter, text) , file=f )

def statistics(model, data):
    '''
    Aggregates and produces machine processable statistics from the `frames` 
    obtained from `model`.
    '''
    os.makedirs("{}/stats/".format(model), exist_ok=True)
    
    data.to_csv("{}/stats/data.csv".format(model), sep=';')

def json_cluster_graph(model, bound, clusters, graph):
    '''
    Dumps a json file containing information to visualize the cluster graph.
    
    .. note:: 
        This is thightly connected to the `d3_visualisation` feature present
        in the visualisation module.
    '''
    os.makedirs("{}/json/{:03d}/".format(model, bound), exist_ok=True)
    
    # set cluster size and id on all vs
    counter = 0
    for cluster in clusters:
        counter += 1
        size     = len(cluster)
        for vertex in cluster:
            graph.vs[vertex]['size'] = size
            graph.vs[vertex]['community'] = counter;
    # set equal weight for all connections so that it becomes visible in
    # the output diagram
    graph.es['weight'] = [ 1 for _ in graph.es]
    
    cg = clusters.cluster_graph(combine_vertices={'size': 'first', 'community': 'first'},
                                combine_edges={'weight': 'sum'})
    
    with open("{}/json/{:03d}/cluster_graph.json".format(model, bound), 'w') as f: 
        print(core.graph_to_json(cg), file=f)