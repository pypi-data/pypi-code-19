from orderedobject import orderedobject
from orderedobject import ordereddict
from orderedobject import OrderedClass
import sys

import pytest

import gc
from weakref import proxy

class O(object):
    pass

def make_removable(name, list, weakholder):
    obj = O()

    def callback(ref, name=name, list=list):
        list.append(name)

    weakholder.append(proxy(obj, callback))
    return obj

def test_orderedobject():
    gc.collect()

    o = orderedobject()

    l = []
    w = []
    o.b = make_removable('b', l, w)
    o.a = make_removable('a', l, w)

    print("Before deleting", l)
    del o # trigger deletion
    print("After deleting", l)
    gc.collect() # forcefully with GC.
    print("After gc", l)

    # assert reversed order.
    assert l[0] == 'a'
    assert l[1] == 'b'

def test_pickle():
    import pickle
    o = orderedobject()
    o.a = 100
    o.b = 200
    s = pickle.dumps(o)
    o2 = pickle.loads(s)
    assert o2.a == o.a
    assert o2.b == o.b

def test_ordereddict():
    gc.collect()

    o = ordereddict()

    l = []
    w = []
    o['b'] = make_removable('b', l, w)
    o['a'] = make_removable('a', l, w)

    print("Before deleting", l)
    del o # trigger deletion
    print("After deleting", l)
    gc.collect() # forcefully with GC.
    print("After gc", l)

    # assert reversed order.
    assert l[0] == 'a'
    assert l[1] == 'b'

@pytest.mark.xfail(reason="See https://github.com/cython/cython/issues/1821")
@pytest.mark.xskip(sys.version_info < (3, 0), reason="metaclass syntax only works in Python 3")
def test_orderedclass():
    gc.collect() # forcefully with GC.

    l = []
    w = []

    # the awkward stuff is to avoid an error Python 2.7 trying to parse this code.

    d = dict(locals())
    G = dict(globals())
    G.update(d)
    exec(
"""
class A(metaclass=OrderedClass):
    b = make_removable('b', l, w)
    a = make_removable('a', l, w)
""", G, d)
    A = d['A']
    del d
    del G

    print("Before deleting", l)
    print(A.__dict__.__order__)
    del A

    print("After deleting", l)
    gc.collect() # forcefully with GC.
    print("After gc", l)

    # assert reversed order.
    assert l[0] == 'a'
    assert l[1] == 'b'
