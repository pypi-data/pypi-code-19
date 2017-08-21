from ontobio.ontol_factory import OntologyFactory
from ontobio.assoc_factory import AssociationSetFactory
from ontobio.assocmodel import AssociationSet
from ontobio.io.gafparser import GafParser
import logging
import random

NUCLEUS = 'GO:0005634'
CYTOPLASM = 'GO:0005737'
MITO = 'GO:0005739'
MOUSE = 'NCBITaxon:10090'
TRANSCRIPTION_FACTOR = 'GO:0003700'
TRANSPORTER = 'GO:0005215'
PART_OF = 'BFO:0000050'


HUMAN='NCBITaxon:9606'
PD = 'DOID:14330'

def test_sparse():
    """
    factory test
    """
    ofactory = OntologyFactory()
    afactory = AssociationSetFactory()
    ont = ofactory.create('hp')
    aset = afactory.create(ontology=ont,
                           subject_category='disease',
                           object_category='phenotype',
                           taxon=HUMAN)
    
    logging.info("Querying")
    rs = aset.query_associations([PD])
    print("Gene Assocs to PD: {} {}".format(rs, len(rs)))

    logging.info("Converting to DF")
    df = aset.as_dataframe(fillna=False)
    print('SIZE={}'.format(df.size))
    print('DF={}'.format(df[0:3]))
    logging.info("Converting to Sparse")
    sdf = df.to_sparse()
    print('DENSITY={}'.format(sdf.density))
    assert sdf.density < 0.01

