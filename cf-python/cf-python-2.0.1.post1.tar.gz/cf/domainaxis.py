from .functions import inspect as cf_inspect

class DomainAxis(object):
    '''
    '''
    def __init__(self, size=None):
        '''
**Initialization**

:Parameters:

    size: `int`, optional

'''

        self.size = size
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Called by the `copy.deepcopy` standard library function.

'''
        return self.copy()
    #--- End: def

    def __repr__(self):
        '''
Called by the `repr` built-in function.

x.__repr__() <==> repr(x)

'''
        return '<CF DomainAxis: {0}>'.format(self)
    #--- End: def

    def __str__(self):
        '''

Called by the `str` built-in function.

x.__str__() <==> str(x)
'''
        return str(self.size)
    #--- End: def

    def __eq__(self, other):
        '''
'''
        return self.size == int(other)
    #--- End: def

    def __ne__(self, other):
        '''
'''
        return self.size != int(other)
    #--- End: def

    def __gt__(self, other):
        '''
'''
        return self.size > int(other)
    #--- End: def

    def __ge__(self, other):
        '''
'''
        return self.size >= int(other)
    #--- End: def

    def __lt__(self, other):
        '''
'''
        return self.size < int(other)
    #--- End: def

    def __le__(self, other):
        '''
'''
        return self.size <= int(other)
    #--- End: def

    def __add__(self, other):
        '''
        '''
        new = self.copy()
        self.size += int(other)
        return new

    def __radd__(self, other):
        '''
        '''
        return self + other

    def __iadd__(self, other):
        '''
        '''
        self.size += int(other)
        return self

    def __sub__(self, other):
        '''
        '''
        new = self.copy()
        self.size -= int(other)
        return new

    def __isub__(self, other):
        '''
        '''
        self.size -= int(other)
        return self

    def __int__(self):
        '''
x.__int__() <==> int(x)
'''
        return self.size

    def copy(self):
        '''

Return a deep copy.

``d.copy()`` is equivalent to ``copy.deepcopy(d)``.

:Returns:

    out: 
        The deep copy.

:Examples:

>>> e = d.copy()

'''
        X = type(self)
        new = X.__new__(X)

        # This is OK, for now, because values of self.__dict__ are
        # immutable
        new.__dict__ = self.__dict__.copy()

        return new
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False,
               ignore=(), _set=False):
        '''
:Parameters:

    other : object
        The object to compare for equality.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        domain axes differ.

    atol : *optional*
        Ignored.

    rtol : *optional*
        Ignored.

    ignore : *optional*
        Ignored.

    ignore_fill_value : *optional*
        Ignored.

:Returns: 
  
    out : bool
        Whether or not the two domain axes are equal.
        '''
        # Check for object identity
        if self is other:
            return True

        # Check that each instance is of the same type
        if not isinstance(other, self.__class__):
            if traceback:
                print("{0}: Incompatible types: {0}, {1}".format(
			self.__class__.__name__,
			other.__class__.__name__))
	    return False
        #--- End: if

        # Check that each axis has the same size
        if not self.size == other.size:
            if traceback:
                print("{0}: Different axis sizes: {1} != {2}".format(
			self.__class__.__name__, self.size, other.size))
	    return False
        #--- End: if

        return True
    #--- End: def

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

:Examples:

>>> f.inspect()

'''
        print cf_inspect(self)
    #--- End: def

#--- End: class
