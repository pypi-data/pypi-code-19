from functools import reduce


class Chain(list):
    def __call__(self, req, res, nxt, *args, **kwargs):
        reduce(lambda nxt, f: (
            lambda *args, **kwargs: f(req, res, nxt, *args, **kwargs)
        ), reversed(self), nxt)(*args, **kwargs)
