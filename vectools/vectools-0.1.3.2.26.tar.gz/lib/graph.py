"""
https://github.com/networkx/networkx/

https://workshape.github.io/visual-graph-algorithms/

This library will store graph related functions.

These links will provide ideas.
http://www.boost.org/doc/libs/1_60_0/libs/graph/doc/index.html

https://graph-tool.skewed.de/

http://igraph.org/python/doc/tutorial/tutorial.html

http://www.python-course.eu/graphs_python.php


GMT format - a graph format for gene function enrichment analysis.

Infer a network from parital information of a (synthetic)
Clark et al. BMC Systems Biology 2012, 6:89

Algorithms:

Density Peak
Rodriguez, Alex, and Alessandro Laio. "Clustering by fast search and find of density peaks." Science 344.6191 (2014): 1492-1496.

Link Community
Ahn, Yong-Yeol, James P. Bagrow, and Sune Lehmann.
"Link communities reveal multiscale complexity in networks."
Nature 466.7307 (2010): 761-764.

Infomap
Rosvall, Martin, and Carl T. Bergstrom.
"Multilevel compression of random walks on networks reveals hierarchical organization in large integrated systems."
PloS one 6.4 (2011): e18209.

Fast Unfolding
Blondel, Vincent D., et al.
"Fast unfolding of communities in large networks."
Journal of Statistical Mechanics: Theory and Experiment 2008.10 (2008): P10008.

Newman Method
Newman, Mark EJ.
"Finding community structure in networks using the eigenvectors of matrices."
Physical review E 74.3 (2006): 036104.

Soft Clustering
Futschik, Matthias E., and Bronwyn Carlisle.
"Noise-robust soft clustering of gene expression time-course data."
Journal of bioinformatics and computational biology 3.04 (2005): 965-988.

"""

from lib.inputoutput import ParseVectors, _shared_params, _slice_list
import networkx as nx
import numpy as np


def _graphcommandlineargs(parser):
    """
    G=nx.Graph()
    G=nx.DiGraph()
    G=nx.MultiGraph()
    G=nx.MultiDiGraph()
    :return:
    """
    graph_types = ["GRAPH", "DIRECTED"]

    parser.add_argument('-j', '--graph-type',
                        type=str,
                        required=False,
                        choices=graph_types,
                        default=graph_types[0],
                        help='The type of graph.')


def listedges(parser):
    """ List the edges of a node or graph.

    This function list the edges with respect to a given node, or if not specified, an entire graph.

    cat examples/graph/ring_graph.vec
    ids     A       B       C       D
    A       0       1       0       1
    B       1       0       1       0
    C       0       1       0       1
    D       1       0       1       0

    vectools listedges -cr --use-node-names examples/graph/ring_graph.vec

    A       B
    A       D
    B       C
    C       D

    vectools listedges -cr  -n 1 examples/graph/ring_graph.vec
    1       0
    1       2

    vectools listedges -cr --use-node-names -n 1 examples/graph/ring_graph.vec
    B       A
    B       C
    """

    # @TODO: If columns are row are added, use dict to store node names instead of integer names.
    # http://stackoverflow.com/questions/29572623/plot-networkx-graph-from-adjacency-matrix-in-csv-file

    parser.add_argument(
        '-n', '--node-position',
        type=int,
        #required=True,
        default=None,
        help='.')

    parser.add_argument(
        'input_graphs',
        metavar='input_graphs',
        type=str,
        nargs='+',
        help='Files to join, the first is treated as the base and following files the append matrices.')

    parser.add_argument(
        '-u', "--use-node-names",
        action="store_true",
        help='')

    _shared_params(parser)
    _graphcommandlineargs(parser)
    args = parser.parse_args()

    out_matrix_obj = ParseVectors(
        file_name="",
        has_col_names=False,  #args.column_titles,
        has_row_names=False,  # args.row_titles,  # Row titles should just be treated as normal columns.
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # Iterate over the graphs.
    for input_graph in args.input_graphs:
        # This needs to be reset in case of multiple append matrices, the length of the base matrix will change.

        # Create a parsing object.
        parsevecs_obj = ParseVectors(
            file_name=input_graph,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            only_apply_on_columns=None  #args.only_apply_on
        )

        # In this case we need to parse the entire matrix before doing operations.
        matrix = parsevecs_obj.parse()

        nx_graph_obj = nx.from_numpy_matrix(matrix)

        if args.node_position:
            edges = nx_graph_obj.edges([args.node_position])
        else:
            edges = nx_graph_obj.edges()

        # Output results. We can output as we find them.
        for el in edges:
            el_1, el_2 = el

            if args.use_node_names and args.column_titles and args.row_titles:
                node_1 = parsevecs_obj.col_titles[el_1+1]
                assert node_1 == parsevecs_obj.row_titles[el_1], "Error: Node names must match, %s != %s" % (
                    node_1, parsevecs_obj.row_titles[el_1])

                node_2 = parsevecs_obj.col_titles[el_2+1]
                assert node_2 == parsevecs_obj.row_titles[el_2], "Error: Node names must match, %s != %s" % (
                    node_2, parsevecs_obj.row_titles[el_2])

            else:
                node_1 = el_1
                node_2 = el_2

            out_matrix_obj.iterative_out(
                row_title=None,  # input_graph,
                vector=np.array([node_1, node_2]),
                column_titles=out_matrix_obj.getcolumntitles(),
            )


def addedge():
    """ Add edges to a graph and output vector representation.
    - Should be a 2-D vector, CLI argument to determine if undirected or directed.
        - Should be able to handle title names or column indexes.
    - Should be able to handle output from list edges.
    :return:
    """
    # G.add_edge(2, 3, weight=0.9)
    # G.add_weighted_edges_from(elist)
    pass


def addnode():
    """ Add nodes to a graph and output vector representation.
    - Add a row and then a column or vise-versa
        - Add same new row and column name? If numbers append to ends?

    :return:
    """
    # >>> G.add_node(math.cos) # any hashable can be a node
    # weighted nodes?
    pass


def listpaths(parser):
    """ List the shortest, all, etc. paths between two vertices. (default: shortest path)

    cat examples/graph/ring_graph.vec
    ids     A       B       C       D
    A       0       1       0       1
    B       1       0       1       0
    C       0       1       0       1
    D       1       0       1       0

    vectools path -cr --use-node-names examples/graph/ring_graph.vec

    A       B
    A       D
    B       C
    C       D

    vectools path -cr  -n 1 examples/graph/ring_graph.vec
    1       0
    1       2

    vectools path -cr --use-node-names -n 1 examples/graph/ring_graph.vec
    B       A
    B       C
    """

    parser.add_argument(
        '-n1', '--source-node',
        type=int,
        #required=True,
        default=None,
        help='Find the path from this node (node 1) to another node (node 2). \
         If both arguments are absent all paths are printed.')

    parser.add_argument(
        '-n2', '--target-node',
        type=int,
        #required=True,
        default=None,
        help='Find the path from a node (node 1) to this node (node 2). \
         If both arguments are absent all paths are printed.')

    parser.add_argument(
        '-u', "--use-node-names",
        action="store_true",
        help='')

    #parser.add_argument(
    #    '-a', "--all",
    #    action="store_true",
    #    help='')

    parser.add_argument(
        '-w', "--weighted",
        action="store_true",
        help='')

    parser.add_argument(
        '-s', "--shortest",
        action="store_true",
        help='')

    parser.add_argument(
        '-l', "--length",
        action="store_true",
        help='')

    parser.add_argument(
        'input_graphs',
        metavar='input_graphs',
        type=str,
        nargs='+',
        help='Files to join, the first is treated as the base and following files the append matrices.')

    _shared_params(parser)

    _graphcommandlineargs(parser)

    args = parser.parse_args()

    out_matrix_obj = ParseVectors(
        file_name="",
        has_col_names=False,  # args.column_titles,
        has_row_names=False,  # args.row_titles,  # Row titles should just be treated as normal columns.
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # Iterate over the graphs.
    for input_graph in args.input_graphs:

        # Create a parsing object.
        parsevecs_obj = ParseVectors(
            file_name=input_graph,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            only_apply_on_columns=None  #args.only_apply_on
        )

        # In this case we need to parse the entire matrix before doing operations.
        matrix = parsevecs_obj.parse()

        nx_graph_obj = nx.from_numpy_matrix(matrix)
        # print(nx_graph_obj.__dict__)


        if args.source_node and args.target_node:
            source_node = args.source_node
            target_node = args.target_node

            # Return True if G has a path from source to target, False otherwise.
            if nx.has_path(nx_graph_obj, source=source_node, target=target_node):

                if args.weighted:
                    pass
                    """
                    Shortest path algorithms for weighed graphs.
                    dijkstra_path(G, source, target[, weight]) 	Returns the shortest path from source to target in a weighted graph G.
                    dijkstra_path_length(G, source, target[, weight]) 	Returns the shortest path length from source to target in a weighted graph.
                    single_source_dijkstra_path(G, source[, ...]) 	Compute shortest path between source and all other reachable nodes for a weighted graph.
                    single_source_dijkstra_path_length(G, source) 	Compute the shortest path length between source and all other reachable nodes for a weighted graph.
                    all_pairs_dijkstra_path(G[, cutoff, weight]) 	Compute shortest paths between all nodes in a weighted graph.
                    all_pairs_dijkstra_path_length(G[, cutoff, ...]) 	Compute shortest path lengths between all nodes in a weighted graph.
                    single_source_dijkstra(G, source[, target, ...]) 	Compute shortest paths and lengths in a weighted graph G.
                    bidirectional_dijkstra(G, source, target[, ...]) 	Dijkstra's algorithm for shortest paths using bidirectional search.
                    dijkstra_predecessor_and_distance(G, source) 	Compute shortest path length and predecessors on shortest paths in weighted graphs.
                    bellman_ford(G, source[, weight]) 	Compute shortest path lengths and predecessors on shortest paths in weighted graphs.
                    negative_edge_cycle(G[, weight]) 	Return True if there exists a negative edge cycle anywhere in G.
                    johnson(G[, weight]) 	Compute shortest paths between all nodes in a weighted graph using Johnson's algorithm.



                    Dense Graphs
                    Floyd-Warshall algorithm for shortest paths.
                    floyd_warshall(G[, weight]) 	Find all-pairs shortest path lengths using Floyd's algorithm.
                    floyd_warshall_predecessor_and_distance(G[, ...]) 	Find all-pairs shortest path lengths using Floyd's algorithm.
                    floyd_warshall_numpy(G[, nodelist, weight]) 	Find all-pairs shortest path lengths using Floyd's algorithm.
                    A* Algorithm
                    Shortest paths and path lengths using A* ("A star") algorithm.
                    astar_path(G, source, target[, heuristic, ...]) 	Return a list of nodes in a shortest path between source and target using the A* ("A-star") algorithm.
                    astar_path_length(G, source, target[, ...]) 	Return the length of the shortest path between source and target using the A* ("A-star") algorithm.
                    """
                else:
                    """
                    Shortest path algorithms for unweighted graphs.
                    predecessor(G, source[, target, cutoff, ...]) 	Returns dictionary of predecessors for the path from source to all nodes in G.
                    These algorithms work with undirected and directed graphs.
                    shortest_path_length(G[, source, target, weight]) 	Compute shortest path lengths in the graph.
                    average_shortest_path_length(G[, weight]) 	Return the average shortest path length.

                    Advanced Interface
                    """

                    if args.shortest:
                        # Print all paths
                        # Print shortest paths.
                        #  all_shortest_paths(G, source, target[, weight]) 	Compute all shortest paths in the graph.
                        if args.length:
                            # Compute shortest path lengths in the graph.
                            paths = nx.shortest_path_length(nx_graph_obj, source=source_node, target=target_node)
                        else:
                            paths = nx.all_shortest_paths(nx_graph_obj, source=source_node, target=target_node)
                        # all_shortest_paths(G, source, target[, weight])  Compute all shortest paths in the graph.
                    else:
                        # Print all paths.
                        paths = nx.all_simple_paths(nx_graph_obj, source=source_node, target=target_node)
                        #   shortest_path(G[, source, target, weight]) 	Compute shortest paths in the graph.

                # print(paths)
                # shortest_path_length
                # https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.shortest_paths.generic.average_shortest_path_length.html
                # average_shortest_path_length
                try:
                    for path in paths:
                        print(path)
                except:
                    """
                    out_matrix_obj.iterative_out(
                        row_title=None,  # input_graph,
                        vector=np.array([node_1, node_2]),
                        column_titles=out_matrix_obj.getcolumntitles(),
                    )
                    """
                    print(paths)

            else:
                print(False)
            """
            # average_shortest_path_length(G[, weight]) 	Return the average shortest path length.
            """
        else:
            if args.shortest:
                if args.length:
                    #  Computes the shortest path lengths between all nodes in G.
                    paths = nx.all_pairs_shortest_path_length(nx_graph_obj)
                else:
                    #  Compute shortest paths between all nodes.
                    paths = nx.all_pairs_shortest_path(nx_graph_obj)
            else:
                pass



# This needs to be reset in case of multiple append matrices, the length of the base matrix will change.
# all_simple_paths(G, source, target[, cutoff]) 	Generate all simple paths in the graph G from source to target.
# shortest_simple_paths(G, source, target[, ...]) 	Generate all simple paths in the graph G from source to target, starting from shortest ones.
#

def graphformat(parser):
    """ Convert a matrix to dot format or vise-versa.
    The dot language is commonly used by graph formatting languages.

    :param parser:
    :return:
    """
    pass


def clusteringcoeffient():
    pass




        # http://networkx.readthedocs.io/en/stable/reference/algorithms.html
# http://networkx.readthedocs.io/en/stable/reference/linalg.html#module-networkx.linalg.attrmatrix
# http://networkx.readthedocs.io/en/stable/reference/functions.html