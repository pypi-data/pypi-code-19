from orderedobject import orderedobject
import gc

def test_orderedobj():
    gc.collect()
    o = orderedobject()
    o.a = 100
    o.b = 200
    o.o = o
    del o
    gc.collect()

def test_pickle():
    import pickle
    o = orderedobject()
    o.a = 100
    o.b = 200
    s = pickle.dumps(o)
    o2 = pickle.loads(s)
    assert o2.a == o.a
    assert o2.b == o.b
