from inspect import getfullargspec

__all__ = ['CurriedFunction', 'curry']

class CurriedFunction:
    # TODO: full especification
    def __init__(self, func, **kwargs):
        argspec = getfullargspec(func)
        self._nargs = kwargs.pop('nargs', len(argspec.args))
        if self._nargs == 0:
            raise TypeError("Curried functions must have at least 1 argument")
        
        self.args = kwargs.pop('args', ())
        self.func = func
    
    def compose(self, other):
        cfunc = compose(self, other)
        return CurriedFunction(cfunc, nargs=1)
    
    def __repr__(self):
        return '<curried_function {}.{}>'.format(self.func.__module__, self.func.__name__)
    
    def __call__(self, *args):
        new_args = self.args + args
        arglen = len(new_args)
        
        if arglen > self._nargs: # test
            raise TypeError("{}() takes at most {} arguments ({} given)"
                                .format(self.func.func_name, self._nargs, arglen))
        
        if self._nargs == len(new_args):
            return self.func(*new_args)
    
        return CurriedFunction(self.func, args=new_args, nargs=self._nargs)
    
    def __floordiv__(self, other):
        # g(f(x)) -> g // f(x)
        return self(other)
    
    # function composition
    # f @ g (x) = f(g(x))
    __matmul__ = compose
    
    # function application:
    # f << x := f(x)
    # x >> f := f(x)
    __lshift__ = __rrshift__ = __call__

def curry(func):
    return CurriedFunction(func)
