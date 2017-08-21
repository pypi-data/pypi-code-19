from ontobio.assoc_factory import AssociationSetFactory
from ontobio.io.gafparser import GafParser


def test_remote():
    afa = AssociationSetFactory()
    group = 'pseudocap'
    url = "http://geneontology.org/gene-associations/gene_association.{}.gz".format(group)
    p = GafParser()
    assocs = p.parse(url)
    for m in p.report.messages:
        print(m)
    print(p.report.to_report_json())
    assert len(assocs) > 0
