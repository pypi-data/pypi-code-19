from ontobio.ontol_factory import OntologyFactory
from ontobio.lexmap import LexicalMapEngine
import logging

def test_lexmap():
    """
    Text lexical mapping
    """
    factory = OntologyFactory()
    print("Creating ont")
    ont = factory.create('tests/resources/lexmap_test.json')
    lexmap = LexicalMapEngine()

    lexmap.index_ontology(ont)

    print(lexmap.lmap)
    print(ont.all_synonyms())
    g = lexmap.get_xref_graph()
    for x,y,d in g.edges_iter(data=True):
        print("{}<->{} :: {}".format(x,y,d))
    for x in g.nodes():
        print("{} --> {}".format(x,lexmap.grouped_mappings(x)))
    assert g.has_edge('Z:2','ZZ:2') # roman numerals
    assert g.has_edge('Z:2','D:2')  # case insensitivity
    assert g.has_edge('A:1','B:1')  # synonyms
    
