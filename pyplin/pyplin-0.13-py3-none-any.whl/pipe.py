class pipe:
    """
    pipe object
    wrapping object so to overload operator |
    unwrap it by invoking property value
    """

    def __init__(self, value):
        self._v = value

    @property
    def value(self):
        return self._v

    def __or__(self, func):
        vv = self._v
        try:
            i = iter(vv)
            o = tuple(func(v) for v in vv)
        except TypeError:
            o = func(vv)
        except:
            raise

        return pipe(o)

