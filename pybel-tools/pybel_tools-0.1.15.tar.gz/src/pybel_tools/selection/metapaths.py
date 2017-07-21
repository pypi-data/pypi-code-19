# -*- coding: utf-8 -*-

"""

A metapath can be defined with two levels of granularity:

- Low: A list of BEL functions representing the types of entities in a given path
- High: An alternating list of BEL functions and BEL relations representing the types of entities in a given path and
  their relations

"""

from pybel.constants import FUNCTION


def convert_path_to_metapath(graph, nodes):
    """Converts a list of nodes to their corresponding functions

    :param list[tuple] nodes: A list of BEL node tuples
    :rtype: list[str]
    """
    return [
        graph.node[node][FUNCTION]
        for node in nodes
    ]


def get_walks_exhaustive(graph, node, length):
    """Gets all walks under a given length starting at a given node

    :param networkx.Graph graph: A graph
    :param node: Starting node
    :param int length: The length of walks to get
    :return: A list of paths
    """
    if 0 == length:
        return (node,),

    return [
        (node, key) + path
        for neighbor in graph.edge[node]
        for path in get_walks_exhaustive(graph, neighbor, length - 1)
        if node not in path
        for key, data in graph.edge[node][neighbor].items()
    ]


def match_simple_metapath(graph, node, metapath):
    """Matches a simple metapath starting at the given node

    :param graph: A BEL graph
    :param node: A BEL node
    :param metapath: A list of BEL Functions
    :return: An iterable over paths from the node matching the metapath
    """
    if 0 == len(metapath):
        yield node,

    else:
        for neighbor in graph.edge[node]:
            if graph.node[node][FUNCTION] == metapath[0]:
                for path in match_simple_metapath(graph, neighbor, metapath[1:]):
                    if node not in path:
                        yield (node,) + path
