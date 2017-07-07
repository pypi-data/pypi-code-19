from numpy import array
from numpy.testing import assert_array_almost_equal, assert_equal

from ndarray_listener import ndarray_listener


def test_operations():
    a = array([-0.5, 0.1, 1.1])
    b = ndarray_listener(a)
    c = ndarray_listener(array([-0.5, 0.1, 1.1]))

    assert_array_almost_equal(a - b, [0, 0, 0])
    assert_array_almost_equal(a, b)
    assert_array_almost_equal(a, c)
    assert_array_almost_equal(b - c, [0, 0, 0])


def test_notification():
    a = array([-0.5, 0.1, 1.1])
    b = ndarray_listener(a)
    c = ndarray_listener(array([-0.5, 0.1, 1.1]))

    class Watcher(object):  # pylint: disable=R0903
        def __init__(self):
            self.called_me = False

        def __call__(self, _):
            self.called_me = True

    w = Watcher()
    b.talk_to(w)

    assert_equal(w.called_me, False)
    b[0] = 1.2
    assert_equal(w.called_me, True)

    w = Watcher()
    b.talk_to(w)

    assert_equal(w.called_me, False)
    b[:] = 1
    assert_equal(w.called_me, True)

    w = Watcher()
    c.talk_to(w)

    assert_equal(w.called_me, False)
    c[:] = c + c
    assert_equal(w.called_me, True)


def test_iterator():
    a = ndarray_listener([-0.5, 0.1, 1.1])
    assert isinstance(next(iter(a)), ndarray_listener)


def test_printing(capsys):
    a = ndarray_listener(array([-0.5, 0.1, 1.1]))

    print(a)
    out, _ = capsys.readouterr()
    assert out == "[-0.5  0.1  1.1]\n"
    print([a])
    out, _ = capsys.readouterr()
    assert out == "[ndarray_listener([-0.5,  0.1,  1.1])]\n"
