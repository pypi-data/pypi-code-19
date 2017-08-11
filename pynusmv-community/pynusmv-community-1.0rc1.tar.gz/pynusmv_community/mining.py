'''
This module contains all the mining-related functionalities. These 
functions compute nothing per themselves (except trivial stuffs) and rely on 
core to do the heavy lifting.
'''

import os
import pandas

from pynusmv_community import core

def mine_frequent_patterns(clusters, graph):
    '''
    Mines the most frequent patterns in each of the `clusters` of the `graph`
    (based on their semantic value in the problem defined by `model` unrolled
    `bound` times) and returns a pandas Dataframe representing the mined 
    information
    
    .. note::
        Mining the patterns is somewhat weaker than mining the sequences. You
        might want to call that instead.
    '''
    import re
    import pymining.itemmining as _mine
    
    # represent a vertex
    reprs= lambda v: core.vertex_repr(graph, v)
    #  curate the communities
    curat= lambda c: [ reprs(v) for v in c if reprs(v) != '???' ]
    # represent a community as a set of transactions
    trans= lambda c: [ re.split('[\.\*]+', v) for v in curat(c) ]
    
    # mine the patterns of a community
    def _do_mine(community):
        # returns a dictionary {frozenset} -> {count}
        relim_in = _mine.get_relim_input(trans(community))
        patterns = _mine.relim(relim_in)
        return patterns
    
    def _mine_by_frequence(x):
        return sorted(_do_mine(x).items(), reverse=True, key=lambda t: t[1])
    
    counter= 0
    frames = []
    for community in clusters:
        counter += 1
        for items,cnt in _mine_by_frequence(community):
            text = ' '.join(items)
            frames.append(pandas.DataFrame.from_dict({
                'CommunityNo' : [counter], 
                'Count'       : [cnt],
                'Pattern'     : [text]
            }))
    
    return pandas.concat(frames)

def mine_frequent_sequences(clusters, graph):
    '''
    Mines the most frequent sequences in each of the `clusters` of the `graph`
    (based on their semantic value in the problem defined by `model` unrolled
    `bound` times) and returns a pandas DataFrame
    '''
    import re
    import pymining.seqmining as _mine
    
    
    # represent a vertex
    reprs= lambda v: core.vertex_repr(graph, v)
    #  curate the communities
    curat= lambda c: [ reprs(v) for v in c if reprs(v) != '???' ]
    # represent a community as a set of transactions
    trans= lambda c: [ re.split('[\.\*]+', v) for v in curat(c) ]
    
    # symbol table -> one integer represent one symbol
    def symbolic(transactions_list):
        sym_2_id = dict()
        id_2_sym = dict()
        counter  = 0
        
        # memoize tokens and ids
        for transaction in transactions_list:
            for token in transaction:
                if token not in sym_2_id:
                    counter         += 1
                    sym_2_id[token]  = counter
                    id_2_sym[counter]= token
        
        # convert tokens to id
        converted = [[sym_2_id[tok] for tok in transaction] for transaction in transactions_list ]
        
        return (converted, id_2_sym)
    
    # define what can be mined
    minable = lambda c: symbolic(trans(c))
    
    counter= 0
    frames = []
    for community in clusters:
        counter += 1
        seqs, conv = minable(community)
        freq_seqs  = _mine.freq_seq_enum(seqs, 2)
        freq_seqs  = sorted(freq_seqs, reverse=True, key=lambda x: (x[1], len(x[0])))
            
        for seq,cnt in freq_seqs:
            items= [conv[i] for i in seq]
            text = '.'.join(items)
            frames.append(pandas.DataFrame.from_dict({
                'CommunityNo' : [counter], 
                'Count'       : [cnt],
                'Sequence'    : [text]
            }))
    
    return pandas.concat(frames)


def dump_frequent_patterns(model, bound, clusters, graph):
    '''
    Mines the most frequent patterns in each of the `clusters` of the `graph`
    (based on their semantic value in the problem defined by `model` unrolled
    `bound` times) and dumps them to CSV file
    
    .. note::
        Mining the patterns is somewhat weaker than mining the sequences. You
        might want to call that instead.
    '''
    os.makedirs("{}/mining/{:03d}".format(model, bound), exist_ok=True)
    
    data = mine_frequent_patterns(clusters, graph)
    data.to_csv("{}/mining/{:03d}/patterns.csv".format(model, bound))


def dump_frequent_sequences(model, bound, clusters, graph):
    '''
    Mines the most frequent sequences in each of the `clusters` of the `graph`
    (based on their semantic value in the problem defined by `model` unrolled
    `bound` times) and dump them to a CSV file.
    '''
    os.makedirs("{}/mining/{:03d}".format(model, bound), exist_ok=True)
    
    data = mine_frequent_sequences(clusters, graph)
    data.to_csv("{}/mining/{:03d}/sequences.csv".format(model, bound))

def mine_concept(model, bound, clusters, graph):
    '''
    Applies formal concept analysis to reveal the concepts hidden in the
    various communities.
    '''
    c = core.graph_to_fca_context(graph)
    
    for i in range( len(clusters) ):
        named    = [str(vertex) for vertex in clusters[i] if core.vertex_repr(graph, vertex) != '???' ]
        print("{:3d} | {} ".format( i, c.intension( named ) ))
    
    
    #print(c)
    c.lattice.graphviz(view=True)
    return c
    