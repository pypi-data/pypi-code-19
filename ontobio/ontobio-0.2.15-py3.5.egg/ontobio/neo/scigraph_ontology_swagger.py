"""
Classes for representing ontologies backed by SciGraph endpoint

E.g.
https://scigraph-ontology.monarchinitiative.org/scigraph/docs/#!/graph/getNeighbors
"""

import networkx as nx
import logging
import ontobio.ontol
import requests
from ontobio.ontol import Ontology
import scigraph

class RemoteScigraphOntology(Ontology):
    """
    ontology backed by SciGraph endpoint
    """

    def __init__(self,
                 url=None,
                 config=None,
                 api_client=None):
        if api_client is None:
            if url is None:
                url = 'https://scigraph-ontology.monarchinitiative.org/scigraph'
            api_client = scigraph.ApiClient(host=url)
        self.api = scigraph.apis.annotations_api.GraphApi(api_client)
        return

    def ancestors(self, node, relations=None, reflexive=False):
        if relations is not None:
            relstr = "|".join(relations)
        else:
            relstr = None
        g = self.api.neighbors(node,
                               direction='OUTGOING',
                               relationshipType=relstr)
        return [v.id for v in g.vertices]
    
    def neighbors(self, id=None, **params):
        """
        Get neighbors of a node

        parameters are directly passed through to SciGraph: e.g. depth, relationshipType
        """
        response = self.get_response("graph/neighbors", id, "json", **params)
        # TODO: should return ids?
        return response.json()
    
    def extract_subset(self, subset):
        pass
    
    def resolve_names(self, names, is_remote=False, **args):
        ## TODO
        return names
    
    def subgraph(self, nodes=[]):
        return self.get_graph().subgraph(nodes)

    
