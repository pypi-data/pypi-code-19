#Calculates the mixed search number of a graph G
import networkx as nx
from bruteForce import linearWidth

def pendantNodes(G):
    '''
    Given a graph G, finds it's pendant nodes and
    the edge connecting them to another node.

    INPUT
    G: A networkx graph

    OUTPUT
    pendant: A list of the format [[vertex, edge] ... ]
    '''
    nodes = G.nodes()
    
    pendant = []
    
    #Find vertices with degree 1
    for node in nodes:

        if G.degree(node) == 1:
            pendant.append([node, G.edges(node)[0]])
   
    return pendant

def subdivide(G, pendant):
    '''
    Given a graph with a list of pendant nodes (and their edges),
    subdivides each of the pendant edges.

    INPUT
    G: A networkx graph
    pendant: A list of the form [[vertex, edge] ...] where
    vertex is pendant and edge is the only edge incident to
    vertex

    OUTPUT
    Gh: The subdivision of G
    '''
    Gh = G.copy()
    
    #Perform the subdivision for each pendant vertex
    for pendantEdge in pendant:
        
        vertex = pendantEdge[0]
        edge = pendantEdge[1]

        #Remove the old edge, add a new vertex, and two edges
        Gh.remove_edge(*edge)
        Gh.add_node(str(edge))
        Gh.add_edge(edge[0], str(edge))
        Gh.add_edge(edge[1], str(edge))

    return Gh

def ms(G):
    '''
    Given a graph G, calculates it's mixed search number
    using the linear width graph parameter. ms(G) = lw(G^h),
    where G^h is the graph of G with all of it's pendant edges subdivided.

    INPUT
    G: A networkx graph

    OUTPUT
    msG: The mixed search number of G
    '''

    #We first subdivide the pendant edges of G
    pendant = pendantNodes(G)
    Gh = subdivide(G, pendant)

    msG = linearWidth(Gh)
    return msG

