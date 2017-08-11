'''
This module contains all the visualization-related functionalities. These 
functions compute nothing per themselves (except trivial stuffs) and rely on 
core to do the heavy lifting.
'''

import os
import shutil 
import math
import random
import igraph

import pandas as pd

from os.path                import abspath, join 
from wordcloud              import WordCloud 
from pynusmv_community      import core, mining, dump
from igraph.drawing.colors  import known_colors#, color_to_html_format
#from scipy.sparse.linalg.isolve.iterative import cg

colors = list(known_colors.values())
random.shuffle(colors)

        
def vig(model, bound, clusters, graph):
    '''
    Saves an image representing the VIG of the sat problem.
    '''
    os.makedirs("{}/vig/".format(model), exist_ok=True)
    
    igraph.plot(clusters, 
                layout  = graph.layout("large_graph"),
                bbox    = (0, 0, 2400, 2400),
                target  = "{}/vig/{:03d}.png".format(model, bound))


def cluster_graph(model, bound, clusters, graph):
    '''
    Saves an image representing the structure of the sat problem derived from
    `model` unrolled `bound` times and classified in `clusters`
    '''
    os.makedirs("{}/structure/".format(model), exist_ok=True)
    
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
    
    smallest_v   = min(cg.vs['size'])
    normalize_v  = lambda x: x / smallest_v
    
    visual_style = {
        'vertex_size' : [ int(round(normalize_v(x))) for x in cg.vs['size'] ],
        'vertex_color': [ colors[v.index % len(colors)] for v in cg.vs ],
        
        'edge_width'  : [ int(1+round(math.log(x))) for x in cg.es['weight'] ],
        'edge_color'  : [ colors[e.source % len(colors)] for e in cg.es ],
        #'edge_curved' : True,
        'auto_curve' : True,
        
        'target'      : "{}/structure/{:03d}.svg".format(model, bound),
        'layout'      : cg.layout("fr"),#cg.layout("rt_circular"),
        'bbox'        : (0, 0, 3200, 3200),
        'margin'      : 250,
        #'background'  : (0,0,0,0)
        
        'vertex_label': [ 'commu-{:03d}'.format(c) for c in cg.vs['community'] ],
        'shape'       : 'circle'
    }
    
    #cg.write_svg(
    #    fname  = "{}/structure/{:03d}.svg".format(model, bound),
    #    labels = 'community',
    #    #**visual_style
    # )
        
    igraph.plot(cg, **visual_style)

def clouds(model, bound, clusters, graph):
    '''
    Saves the wordclouds for the communities stored in the `clusters` of the 
    `graph` derived from `bound` unrolling of the time for `model`
    '''
    os.makedirs("{}/clouds/{:03d}".format(model, bound), exist_ok=True)
    s_cluster = [ [core.vertex_repr(graph, v) for v in c ] for c in clusters ]
    
    counter = 0
    for s in s_cluster:
        counter += 1
        
        # curated info
        text = " ".join(sorted(filter(lambda x: x!="???", s)))
        cloud= WordCloud(stopwords={},regexp=r'\w[\.\[\]\{\}\w]+').generate(text)
        cloud.to_file("{}/clouds/{:03d}/{:03d}.png".format(model, bound, counter))

def statistics(model, data):
    '''
    Aggregates and produces machine processable statistics from the `frames` 
    obtained from `model`.
    '''
    os.makedirs("{}/stats/".format(model), exist_ok=True)

    chart   = lambda z: data[['bound', z]].plot(x='bound', y=z, kind="scatter")
    commu   = chart('#communities').get_figure()
    modul   = chart("modularity").get_figure()
    
    commu.savefig('{}/stats/comunities.png'.format(model))
    modul.savefig('{}/stats/modularity.png'.format(model))
    
def d3_visualisation(model, bound, clusters, graph):
    '''
    Generates a d3 graph based visualisation of the problem.
    This mainly helps in visualizing the cluster graph (rather than the VIG).
    
    .. note::
        This feature is *experimental* and I found it not very helpful to 
        understand the meaning of the communities.
    '''
    target_dir = "{}/d3_graph_vis/{:03d}".format(model, bound)
    source_dir = abspath(join(__file__, '../data/graph_vis'))
    
    shutil.rmtree(target_dir, ignore_errors=True)
    shutil.copytree(source_dir, target_dir)
    os.makedirs(join(target_dir, './data/'), exist_ok=True)
    
    mining.dump_frequent_sequences(model, bound, clusters, graph)
    dump.json_cluster_graph(model, bound, clusters, graph)
    
    shutil.copy("{}/mining/{:03d}/sequences.csv".format(model, bound), 
                "{}/d3_graph_vis/{:03d}/data/sequences.csv".format(model, bound))
    
    shutil.copy("{}/json/{:03d}/cluster_graph.json".format(model, bound), 
                "{}/d3_graph_vis/{:03d}/data/cluster_graph.json".format(model, bound))
    

def table_visualisation(model, bound, clusters, graph):
    '''
    Generates a d3 table based visualisation of the problem.
    This helps in plotting what is part of each community and get a sense of
    the temporal (and semantic) information hidden in the various communities. 
    '''
    ########### PREPPING THE OUTPUT ##########################################
    target_dir = "{}/table_vis/{:03d}".format(model, bound)
    source_dir = abspath(join(__file__, '../data/table_vis'))
    
    shutil.rmtree(target_dir, ignore_errors=True)
    shutil.copytree(source_dir, target_dir)
    os.makedirs(join(target_dir, './data/'), exist_ok=True)
    
    ########### ACTUALLY START GENERATING THE DATA ###########################
    ## Note: this could be moved to dump module
    ####
    semantic_vars = core.semantic_vars(graph)
    time_frames   = range(-1, bound+1)
    
    dataframe     = pd.DataFrame(index  = pd.Series( semantic_vars ), 
                                 columns= pd.Series(time_frames))
    
    for v in semantic_vars: 
        for f in time_frames:
            dataframe.loc[v][f] = set()
    
    counter = 0
    for community in clusters:
        counter += 1
        
        for vertex in community:
            variable = core.vertex_repr(graph, vertex)
            
            if( variable != '???' ):
                var_info = variable.split("*")
                var_name = var_info[0]
                var_block= int( var_info[-1].split("_")[-1] )
                
                dataframe.loc[var_name][var_block].add(counter)
    
    
    with open(join(target_dir, './data/test.json'), "w") as f:
        print('''
            {{
            "model" : "{}",
            "bound" : {},
            "communities": {},
            "data": {} 
            }}
            '''.format(
                model, 
                bound, 
                list( range(1, len(clusters)+1) ), 
                dataframe.to_json(orient='index')
            ),   
            file=f
        )
        
    return dataframe