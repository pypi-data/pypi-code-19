from uscensus.index import Index

def Index_test():
    index = Index()
    data = [
        ('id1', 'title one', 'description of api one', ['var1_1', 'var1_2'],
         [], [], ['key', 'key1'], ['tag', 'tag1'], '2015'),
        ('id2', 'title two', 'description of api two', ['var2_1', 'var2_2'],
         [], [], ['key', 'key2'], ['tag', 'tag2'], '2015'),
    ]
    index.add(data)
    assert index.query('one') == ['title one']
    assert index.query('two') == ['title two']
    assert sorted(index.query('title')) == ['title one', 'title two']
    assert index.query('title:one') == ['title one']
    assert index.query('title:two') == ['title two']

    assert index.query('description:one') == ['title one']
    assert index.query('description:two') == ['title two']

    assert index.query('keywords:key1') == ['title one']
    assert index.query('keywords:key2') == ['title two']
    assert sorted(index.query('keywords:tag')) == ['title one', 'title two']
    assert index.query('tags:tag1') == ['title one']
    assert index.query('tags:tag2') == ['title two']
    assert sorted(index.query('tags:tag')) == ['title one', 'title two']
    
    
    
    assert False
