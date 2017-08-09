from ontobio.io.gafparser import GafParser
from ontobio.assoc_factory import AssociationSetFactory

URL = "ftp://ftp.rgd.mcw.edu/pub/ontology/annotated_rgd_objects_by_ontology/homo_genes_pw"

def test_skim():
    p = GafParser()
    results = p.skim(URL)
    print(str(results))

    
def test_parse():
    p = GafParser()
    results = p.parse(URL)
    for r in results:
        print(str(r))
    
