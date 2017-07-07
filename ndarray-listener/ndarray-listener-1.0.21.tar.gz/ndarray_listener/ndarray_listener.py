# pylint: disable=R0903,W0212,W0201
from numpy import asarray, ndarray


class ndarray_listener(ndarray):
    def __new__(cls, input_array):
        obj = asarray(input_array).view(cls)
        obj._listeners = []
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._listeners = getattr(obj, '_listeners', [])

    def __setitem__(self, *args, **kwargs):
        super(ndarray_listener, self).__setitem__(*args, **kwargs)
        self.__notify()

    def __setattr__(self, *args, **kwargs):
        super(ndarray_listener, self).__setattr__(*args, **kwargs)
        self.__notify()

    def __getitem__(self, *args, **kwargs):
        v = super(ndarray_listener, self).__getitem__(*args, **kwargs)
        return ndarray_listener(v)

    def talk_to(self, me):
        self._listeners.append(me)

    def __notify(self):
        for l in self._listeners:
            l(super(ndarray_listener, self))
