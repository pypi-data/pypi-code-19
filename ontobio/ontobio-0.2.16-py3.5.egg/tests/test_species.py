from ontobio.golr.golr_associations import top_species
 
def test_species_facet():
    tups = top_species(object_category='function',
                       #url='http://localhost:8983/solr/golr'
    )
    for k,v in tups:
        print("  {:5d}: {}".format(v,k))
   
    
