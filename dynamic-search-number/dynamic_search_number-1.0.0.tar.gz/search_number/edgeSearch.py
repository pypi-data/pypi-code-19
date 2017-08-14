#Returns the edge search number of a graph
import networkx as nx
from mixedSearch import ms
import time

def subdivideEdge(G):
    '''
    Given a graph G, returns a graph in which the
    edges of G are subdivided.

    INPUT
    G: A networkx graph

    OUTPUT
    Ge: The edge subdivision of G
    '''
    Ge = G.copy()

    edges = G.edges()
    
    #Go through every edge, remove it, make a new node, and make two edge
    for edge in edges:
        Ge.remove_edge(*edge)
        Ge.add_node(str(edge))
        Ge.add_edge(edge[0], str(edge))
        Ge.add_edge(edge[1], str(edge))

    return Ge
        

def es(G):
    '''
    Given a graph, returns it's edge search number. Works
    on the principle that es(G) = ms(G^e), where G^e is G
    with all of it's edges subdivided.

    INPUT
    G: A networkx graph

    OUTPUT
    esG: The edge search number of G
    '''
    
    #Subdivide the edges of G
    Ge = subdivideEdge(G)
    esG = ms(Ge)

    return esG

