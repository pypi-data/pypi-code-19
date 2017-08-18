from asyncio.futures import Future


class NaType:
    """Type representing an unavailable value.

    There is only one instance of ``NaType``, ``NA``.

    ``NA`` is semantically similar to ``None``, but unlike None it is
    designed to propagate through a program that isn't expecting it,
    without ever causing an exception to be thrown. ``NA`` can be
    treated like a boolean, string, container or numeric value.

    ``NA`` is falsy, unequal to anything including itself, and compares
    less than anything including negative infinity. It returns itself on
    function calls, attribute and item access, or when used on either
    side of any operator. It can be formatted by ``str.format()`` or in
    a f-string with any format spec. Setting or deleting attributes or
    items is a no-op. When used as a context manager it returns itself,
    suppressing exceptions on exit. When iterated over, iteration stops
    immediately (as if it is empty).

    It is awaitable (returning itself), and acts as an asynchronous
    context manager and iterator (behaving identically to the
    synchronous versions).
    """
    # Representation and Type Conversion

    def __repr__(self):
        return "NA"

    def __str__(self):
        return "NA"

    def __bytes__(self):
        return b"NA"

    def __format__(self, format_spec):
        return "NA"

    def __bool__(self):
        return False

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __complex__(self):
        return 0 + 0j

    def __round__(self, n=None):
        return 0.0

    def __index__(self):
        return 0

    # Attributes and Function Calls
    # note: the combination of __getattr__ and __call__ will cause
    # NA.method(args) to return NA for any method/arg combination

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        pass

    def __delattr__(self, name):
        pass

    def __dir__(self):
        return ()

    # Ordering

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __hash__(self):
        return 0

    # Container type emulation

    def __len__(self):
        return 0

    def __getitem__(self, name):
        return self

    def __setitem__(self, name, value):
        pass

    def __delitem__(self, name):
        pass

    def __iter__(self):
        return iter(())

    def __reversed__(self):
        return iter(())

    def __contains__(self, item):
        return False

    # Operator overrides
    # Note: The augmented assignment operators (e.g. __iadd__) shouldn't be
    # necessary here, since they fall back to the regular ones.

    def __add__(self, other):
        return self

    def __radd__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __rsub__(self, other):
        return self

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __matmul__(self, other):
        return self

    def __rmatmul__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __rtruediv__(self, other):
        return self

    def __floordiv__(self, other):
        return self

    def __rfloordiv__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __rmod__(self, other):
        return self

    def __divmod__(self, other):
        return (self, self)

    def __rdivmod__(self, other):
        return (self, self)

    def __pow__(self, other, modulo=None):
        return self

    def __rpow__(self, other):
        return self

    def __lshift__(self, other):
        return self

    def __rlshift__(self, other):
        return self

    def __rshift__(self, other):
        return self

    def __rrshift__(self, other):
        return self

    def __and__(self, other):
        return self

    def __rand__(self, other):
        return self

    def __xor__(self, other):
        return self

    def __rxor__(self, other):
        return self

    def __or__(self, other):
        return self

    def __ror__(self, other):
        return self

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __abs__(self):
        return self

    def __invert__(self):
        return self

    # Context manager emulation

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True

    # Async methods

    def __await__(self):
        f = Future()
        f.set_result(self)
        return f.__await__()

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return True


NA = NaType()

__all__ = ["NA"]
