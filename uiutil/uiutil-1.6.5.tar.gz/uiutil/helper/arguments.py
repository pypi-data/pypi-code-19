

def pop_mandatory_kwarg(kwargs,
                        key):
    try:
        return kwargs.pop(key)
    except KeyError:
        raise ValueError(u'Missing mandatory parameter "{key}"'.format(key=key))


def pop_kwarg(kwargs,
              key,
              default=None):
    try:
        return kwargs.pop(key)
    except KeyError:
        return default


def raise_on_positional_args(caller, args):
    if args:
        raise ValueError(u'positional arguments are not accepted by {c}'.format(c=caller.__class__))


def kwargs_only(f):
    def new_f(**kwargs):
        return f(**kwargs)
    return new_f