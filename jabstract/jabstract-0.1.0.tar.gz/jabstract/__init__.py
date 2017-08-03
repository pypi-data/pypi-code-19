def apply_kwargs(kwargs, default_kwargs):
    for k, v in kwargs.items():
        if isinstance(v, dict):
            default_kwargs[k] = apply_kwargs(v, default_kwargs[k])
        else:
            default_kwargs[k] = v
    return default_kwargs


def jabstract(payload):
    def p(**kwargs):
        return apply_kwargs(kwargs, payload)
    return p
