'''
See "Representation Models for Text Classification" for further information
'''
from ngramgraphs.graph import common_edges, get_edge_weight


# FIXME: test this shit!
def containment_similarity(graph1, graph2):
    mu = lambda e, g: 1 if g.contains_edge(e) else 0
    dividend = sum(mu(e, graph2) for e in graph1.edges())
    divisor = min(len(graph1), len(graph2))
    return dividend / divisor


def size_similarity(graph1, graph2):
    dividend = min(len(graph1), len(graph2))
    divisor = max(len(graph1), len(graph2))
    return dividend / divisor


def value_ratio(edge1, edge2):
    min_ = get_edge_weight(min(edge1, edge2, key=get_edge_weight))
    max_ = get_edge_weight(max(edge1, edge2, key=get_edge_weight))
    return min_ / max_


def value_similarity(graph1, graph2):
    edges = common_edges(graph1, graph2)
    value_ratios = sum(value_ratio(e1, e2) for (e1, e2) in edges)
    divisor = max(len(graph1), len(graph2))
    return value_ratios / divisor


def normalized_value_similarity(graph1, graph2):
    return value_similarity(graph1, graph2) / size_similarity(graph1, graph2)
