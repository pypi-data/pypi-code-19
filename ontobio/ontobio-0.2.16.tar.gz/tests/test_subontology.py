from ontobio.io.gafparser import GafParser
from ontobio.io.ontol_renderers import GraphRenderer
from ontobio.assoc_factory import AssociationSetFactory

POMBASE = "tests/resources/truncated-pombase.gaf"

def test_subont():
    from ontobio.ontol_factory import OntologyFactory
    ofa = OntologyFactory()
    ont = ofa.create('go')
    f = AssociationSetFactory()
    aset = f.create(ontology=ont, file=POMBASE, fmt='gaf')

    ont = aset.subontology(minimal=False)
    
    print("ONT = {} N={}".format(ont, len(ont.nodes())))
    w = GraphRenderer.create('obo')
    print(w.render(ont))

    
