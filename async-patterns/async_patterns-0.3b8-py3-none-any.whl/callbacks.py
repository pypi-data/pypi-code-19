import asyncio

__all__ = ['Callbacks']

class Callbacks:
    """
    Accepts callables objects and stores them in a list, then calls them all
    when something interesting happens
    """
    def __init__(self):
        self.__callbacks = []
    
    def add_callback(self, callable_):
        """
        Add **callable_** to the list of callbacks.
        When this class's :py:func:`Callbacks.__call__` function is called, **callable_**
        will be called with the same arguments passed to that function.
        
        :param callable_: a callable object
        """
        self.__callbacks.append(callable_)

    def __call__(self, *args):
        """
        Trigger a call to each callback, pass **args** to each.
        """
        for callable_ in self.__callbacks:
            callable_(*args)
    
    async def acall(self, *args):
        """
        This is a coroutine.
        Trigger a call to each callback and assume each is a coroutine, pass **args** to each.
        """
        for callable_ in self.__callbacks:
            await callable_(*args)

