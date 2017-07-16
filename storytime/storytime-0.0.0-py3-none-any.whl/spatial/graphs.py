#!/Anaconda3/python
# storytime

"""
description
"""

import numpy as np

from enum import Enum
from copy import deepcopy
from collections import OrderedDict

from ..meta import equality_of
from ..meta import prepare_ndarray
from ..meta import prepare_object
from ..meta import append



#----------------------------------------------------------------------#
# Discrete Spatial data


#----------------------------------------------------------------------#

class EdgeColorBase( Enum ) :
    pass


class __EdgeColor(EdgeColorBase):
    RED = 0
    GREEN = 1
    BLUE = 2


class Symmetry(Enum): # Unused
    NONE = 0
    POSITIVE = 1
    NEGATIVE = -1

#####################

class Edge :
    """
    source and destination are indices into the hosting Network's node array
    color can be used to define overlapping subnetworks
    symmetry =  0  - directed      [a->b]
    symmetry =  1  - symmetric     [a<>b]
    symmetry = -1  - antisymmetric [a><b]
    antisymmetric graphs are useful for representing forces/potentials
    """

    def __init__( self,
                  source: int,
                  destination: int,
                  weight: float = 1.0,
                  color = None,
                  symmetry = 0,
                  index = None
                  ) :
        self.source         = source
        self.destination    = destination
        self.weight         = weight
        self.color          = color

        assert symmetry in (-1, 0, 1) and isinstance( symmetry, int )
        self.symmetry       = symmetry
        self.index          = index


    def __str__( self ) :
        string = "<Edge"

        string += " [" + str( self.source ) + " "
        if self.symmetry == 0:
            string += "->"
        elif self.symmetry == 1 :
                string += "<>"
        elif self.symmetry == -1 :
            string += "><"
        else:
            raise ValueError("Edge.symmetry must be in (0, -1, 1)", self.symmetry)
        string += " "+ str( self.destination ) + "]"

        if self.weight != 1.0:
            string += " w="+str( self.weight )

        if self.color is not None :
            string += " " + str( self.color )

        string += ">"
        return string


#----------------------------------------------------------------------#

class Node :
    """A Network node with a value that can be used to store the entity_id"""

    def __init__( self,
                  index: int = None,
                  value = None,
                  edges: list = None
                  ) :
        self.index = index
        self.value = value
        self.edges = prepare_ndarray( edges ) # ToDo: store edge.index instead


    ###
    def __str__( self ) :
        string = "<Node " + str( self.index )
        string += " [" + str( self.value ) + "]"
        if len(self.edges) > 0:
            string += " x" + str( len( self.edges ))
        string += ">"
        return string


    def add_edge( self, edge ) :
        """record list of edges for quick lookup by node"""

        new_edge = deepcopy( edge )
        new_edge.index = len( self.edges )
        self.edges = append( self.edges, new_edge )


#----------------------------------------------------------------------#

Network = None # used by __add__
class Network :
    """Node-graph with weighted and colored edges. Optional root node and symmetric edges"""

    def __init__( self,
                  nodes: list = None,
                  edges: list = None,
                  root: int = None,
                  symmetry:int = 0
                  ):

        self._nodes = prepare_ndarray( nodes )
        self._edges = prepare_ndarray( edges )

        assert symmetry in (-1, 0, 1) and isinstance(symmetry, int)
        self.symmetry = symmetry
        self.root = root


    ###
    def __str__( self ) :
        string = "<Network:"

        string += " " + str( len( self._nodes ) ) + " | "
        if self.symmetry == 1 :
            string += "s"
        elif self.symmetry == -1 :
            string += "a"
        else:
            string += "d"
        string += str( len( self._edges ) )

        if self.root is not None :
            string += " r=" + str(self.root)

        string += ">"
        return string

    @property
    def __dprint__( self ) :
        string = str(self)
        for node in self._nodes:
            string += "\n" + str(node)
        for edge in self._edges :
            string += "\n" + str( edge )
        return string


    def __add__(self, other_network:Network):
        """produce the union of two disjoint networks"""
        # ToDo: NotImplemented

        offset = len( self._nodes )
        return self + other_network


    ###
    def add_node(self, value ) -> int :
        """Create new node containing value with no edges"""

        new_node = Node( len( self._nodes ), value )
        self._nodes = append( self._nodes, new_node )
        return new_node.index


    def count_nodes( self ) :
        return len( self._nodes )


    def nodes(self):
        for node in self._nodes:
            yield node


    def node( self, node_id: int ) :
        return self._nodes[node_id]


    ###
    def add_edge( self, edge:Edge ) -> int :
        """Add an new_edge between two existing nodes"""

        new_edge = deepcopy( edge )
        new_edge.symmetry = self.symmetry

        # add to self
        new_edge.index=len( self._edges )
        self._edges = deepcopy( append( self._edges, new_edge ) )

        # add to nodes
        if self.symmetry != 0 and (new_edge.source != new_edge.destination) :
            new_edge.symmetry = 0 # edges keep track of symmetry only when used by networks
            self.node(new_edge.destination).add_edge( new_edge )
        self.node(new_edge.source).add_edge( new_edge )

        return new_edge.index


    def count_edges( self, *colors:[EdgeColorBase] ) :
        return len( list( self.edges( *colors ) ) )


    def edges( self, *colors:[EdgeColorBase] ):
        for edge in self._edges:
            if edge.color in colors \
            or edge.color is None and len(colors) == 0 :
                yield edge


    ###
    def to_csr_matrix(self, colors: [EdgeColorBase] ):
        if colors is None: # all edges
            return _edges_to_csr_matrix( self._edges, len( self._nodes ) )
        else:   # filter edges to matching colors. [None] matches color==None
            return _edges_to_csr_matrix( self.edges( *colors ), len( self._nodes ) )


#----------------------------------------------------------------------#

from scipy.sparse import csr_matrix

def addition(a,b): return a+b
def multiplication( a, b ) : return a*b

def _edges_to_csr_matrix( edges:[Edge],
                          node_count:int,
                          stacking_operator = addition,
                          allow_zero = False
                          ) -> (csr_matrix, bool):
    """
    Used to produce the csr_matrix from an arbitrary list of edges
    stacking_operator determines the function for combining two edges with the same position
    if negative distances cause 0 weight on a node, remove the entire connection
    has_negative is used by GraphMatrix to pick a distance algorithm
    """

    row = []
    col = []
    data = []
    has_negative = False

    edge_dict = OrderedDict()

    for edge in edges:
        position = (edge.source, edge.destination)
        edge_dict[position] = stacking_operator( edge_dict.get( position, 0 ), edge.weight )

        if edge.symmetry != 0:  # add (anti)symmetric partner
            coposition = (edge.destination, edge.source)
            new_weight = edge.weight * edge.symmetry
            edge_dict[coposition] = stacking_operator( edge_dict.get( coposition, 0 ), new_weight )

    for ((source, destination), weight) in edge_dict.items():
        if weight < 0:
            has_negative = True
        elif allow_zero is False and weight == 0:
            continue

        row.append( source )
        col.append( destination )
        data.append( weight )

    # print( "row", row )
    # print( "col", col )
    # print( "data", data )

    matrix = csr_matrix( (data, (row, col)), shape=(node_count, node_count) )
    return matrix, has_negative


#----------------------------------------------------------------------#

from scipy.sparse.csgraph import connected_components
from scipy.sparse.csgraph import dijkstra
from scipy.sparse.csgraph import bellman_ford
from scipy.sparse import find

class GraphMatrix :
    """
    GraphMatrix( )                          - empty 0x0 matrix
    GraphMatrix( Network )                  - combine all edges
    GraphMatrix( Network, [EdgeColorBase] ) - filter to listed colors, [None] for color==None
    GraphMatrix( [Edge], int )              - list of edges, node_count
    GraphMatrix( csr_matrix, bool )         - assign as-is
    """

    def __init__( self, arg1=None, arg2=None ) :

        self._connected_components   = { 'value' : None, 'args' : None, 'kwargs' : None }
        self._distance_matrix        = { 'value' : None, 'args' : None, 'kwargs' : None }

        self._has_negative           = False
        self._matrix                = None
        if arg2 is None:
            if arg1 is None:  # ()
                self._matrix = csr_matrix( [] )

            elif isinstance( arg1, Network ) :  # (network)
                (self._matrix, self._has_negative) = arg1.to_csr_matrix( None )

            else:
                raise TypeError( "Invalid arguments: " + str( arg1 ) + ", " + str( arg2 ) )

        elif isinstance( arg1, Network ) :  # (network, [colors])
            (self._matrix, self._has_negative) = arg1.to_csr_matrix( arg2 )

        elif hasattr( arg1, "__iter__" ) : # ([edges], node_count)
            (self._matrix, self._has_negative) = _edges_to_csr_matrix( arg1, arg2 )

        elif isinstance( arg1, csr_matrix ) :  # (matrix, has_negative)
            self._matrix = arg1
            self._has_negative = arg2

        else:
            raise TypeError("Invalid arguments: " +str(arg1)+", "+ str(arg2))


    def __str__(self):
        string = str( self._matrix )
        return string

    @property
    def __dprint__(self):
        string = ""
        for (i, j, v) in self.edges( ) :
            string += "edge: [" + str( i ) + ", " + str( j ) + "] " + str( v ) +"\n"
        return string


    def toarray(self, *args, **kwargs) -> np.ndarray:
        return self._matrix.toarray( *args, **kwargs )


    def edges( self ) -> [(int, int, int)]:
        """sparse list of non-zero edges -> [(row, col, weight),...]"""

        (row, col, data) = find( self._matrix )
        for i in range(0, len(data)) :
            yield ( row[i], col[i], data[i] )


    ###
    def connected_components(self,*args,**kwargs):
        """compute connectedness, cache results"""

        if self._connected_components['value']  is None  \
        or self._connected_components['args']   != args \
        or self._connected_components['kwargs'] != kwargs :
            self._connected_components['args']   = args
            self._connected_components['kwargs'] = kwargs
            self._connected_components['value'] = connected_components( self._matrix, *args, **kwargs )
        return self._connected_components['value']


    def distance_matrix(self,*args,**kwargs):
        """compute distance matrix using an appropriate algorithm, cache results"""

        if self._distance_matrix['value'] is None \
        or self._distance_matrix['args']   != args \
        or self._distance_matrix['kwargs'] != kwargs :
            self._distance_matrix['args']   = args
            self._distance_matrix['kwargs'] = kwargs
            if self._has_negative :
                self._distance_matrix['value'] = bellman_ford( self._matrix, *args, **kwargs )
            else:
                self._distance_matrix['value'] = dijkstra( self._matrix, *args, **kwargs )
        return self._distance_matrix['value']


    def distance(self, source:int, destination:int):
        return self.distance_matrix(source, destination)


#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

from collections import deque
class BKTree :
    """
    http://signal-to-noise.xyz/post/bk-tree/
    """
    def __init__( self, metric ) :
        self._root = None
        self._metric = metric

    def add( self, node ) :
        if self._root is None :
            self._root = (node, { })
            return

        current, children = self._root
        while True :
            dist = self._metric( node, current )
            target = children.get( dist )
            if target is None :
                children[dist] = (node, { })
                break
            current, children = target

    def search( self, node, radius ) :
        if self._root is None :
            return []

        candidates = deque( [self._root] )
        result = []
        while candidates :
            candidate, children = candidates.popleft( )
            dist = self._metric( node, candidate )
            if dist <= radius :
                result.append( (dist, candidate) )

            low, high = dist - radius, dist + radius
            candidates.extend( c for d, c in children.items( )
                               if low <= d <= high )
        return result


#----------------------------------------------------------------------#
