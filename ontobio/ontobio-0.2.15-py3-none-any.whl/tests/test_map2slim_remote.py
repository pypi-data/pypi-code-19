from ontobio import OntologyFactory

def test_map2slim_remote():
    ont = OntologyFactory().create('go')
    relations=['subClassOf', 'BFO:0000050']
    m = ont.create_slim_mapping(subset='goslim_generic', relations=relations)

    assert 'GO:0008150' not in m['GO:0016577']
    assert 'GO:0008150' not in m['GO:0006681']
    # show the first 20 GO terms plus their mappings
    for n in ont.nodes()[0:30]:
        if n.startswith('GO:'):
            print('{} {}'.format(n, ont.label(n)))
            for x in m[n]:
                print('  --> {} {}'.format(x, ont.label(x)))
