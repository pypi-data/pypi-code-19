def inject_kwargs(kwargs, function):
    _blank = object()            
    
    state = {k:function.__globals__.get(k, _blank) for k in kwargs}
    function.__globals__.update(kwargs)

    return (_blank, state)


def restore_function(function, _blank, state):
    for k, v in state.items():
        if v == _blank:
            del function.__globals__[k]
        else:
            function.__globals__[k] = v