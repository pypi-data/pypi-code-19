from .boundedvariable import BoundedVariable

class DomainAncillary(BoundedVariable):
    '''A CF domain ancillary construct.

    '''
    def __init__(self, properties={}, attributes={}, data=None,
                 bounds=None, source=None, copy=True):
        '''
        '''
        super(DomainAncillary, self).__init__(properties=properties,
                                              attributes=attributes,
                                              data=data,
                                              source=source,
                                              copy=copy)
        
        if self.hasdata and not self.ndim:
            # Turn a scalar object into 1-d
            self.expand_dims(0, i=True)
    #--- End: def

    @property
    def isdomainancillary(self):
        '''True, denoting that the variable is a domain ancillary object.

.. versionadded:: 2.0

.. seealso:: `isauxiliary`, `isdimension`, `isfieldancillary`,
             `ismeasure`

:Examples:

>>> f.isdomainancillary
True
        '''
        return True
    #--- End: def
    
    def dump(self, display=True, omit=(), field=None, key=None,
             _level=0, _title=None):
        '''Return a string containing a full description of the domain
ancillary object.

:Parameters:

    display: `bool`, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``f.dump()`` is equivalent to
        ``print f.dump(display=False)``.

    field: `cf.Field`, optional

    key: `str`, optional

:Returns:

    out: `None` or `str`
        A string containing the description.

:Examples:

        '''
        if _title is None:
            _title = 'Domain Ancillary: ' + self.name(default='')

        return super(DomainAncillary, self).dump(
            display=display, omit=omit, field=field, key=key, _level=_level,
            _title=_title)
    #--- End: def

#--- End: class
