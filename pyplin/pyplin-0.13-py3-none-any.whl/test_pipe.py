from .pipe import pipe
from math import sqrt, fsum

def sq(n):
    return n * n


def diff(a, b):
    return tuple(ea - eb for ea, eb in zip(a, b))


def test_dist():
    v1 = (1, 1)
    v2 = (4, 5)

    d = diff(v1, v2)

    r = pipe(d) | sq | sum | sqrt
    assert r.value == 5.0



def test_dist2():
    v0 = (0, 0, 0)
    v1 = (2, 2, 1)

    d = diff(v1, v0)
    print(d)
    r = pipe(d) | sq | fsum | sqrt
    assert r.value == 3.0


def test_sort():
    rnd = [6, 9, 1, 3, 4]
    ans = sorted(rnd)

    sort = pipe(rnd) | sorted
    assert sort.value == ans


def test_lambda():
    x = 2
    y = pipe(x) | sq
    z = pipe(x) | (lambda x: x * x)

    assert y.value == z.value


def test_composite_bad_way():
    def norm2(v):
        p = pipe(v) | sq | fsum | sqrt
        return p.value

    v1 = (1, 1)
    v2 = (4, 5)

    d = diff(v1, v2)

    r = pipe(d) | norm2
    assert r.value == 5.0

#
# def test_composite_good_way():
#     norm2 = sq | fsum | sqrt
#     # how to make this work? even for built-in functions whose | must not be overloaded
#
#     v1 = (1, 1)
#     v2 = (4, 5)
#
#     d = diff(v1, v2)
#
#     r = pipe(d) | norm2
#     assert r.value == 5.0


def test_generator():
    x = range(10)
    y = pipe(x) | sq
    yy = [sq(e) for e in x]

    for a, b in zip(y.value, yy):
        assert a == b
