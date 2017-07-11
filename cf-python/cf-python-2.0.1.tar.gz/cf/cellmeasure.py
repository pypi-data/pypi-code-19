from .variable import Variable

# ====================================================================
#
# CellMeasure object
#
# ====================================================================

class CellMeasure(Variable):
    '''
    
A CF cell measure construct containing information that is needed
about the size, shape or location of the field's cells.

It is a variable which contains a data array and metadata comprising
properties to describe the physical nature of the data.


**Attributes**

==========  =======  =================================================
Attribute   Type     Description
==========  =======  =================================================
`!measure`  ``str``  The spatial measure being represented. Either
                     ``'area'`` or ``'volume'`` are allowed by the CF
                     conventions.
==========  =======  =================================================

'''   
    @property
    def ismeasure(self): 
        '''

Always True.

.. seealso:: `isauxiliary`, `isdimension`

:Examples: 

>>> c.ismeasure
True

'''
        return True
    #--- End: def

    def dump(self, display=True, omit=(), field=None, key=None,
             _level=0, _title=None):
        '''

Return a string containing a full description of the cell measure.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

''' 
        if _title is None:  
            if hasattr(self, 'measure'):
                _title = 'Cell Measure: ' + str(self.measure)
            elif hasattr(self.Units, 'units'):
                _title = 'Cell Measure: ' + str(self.units)
            else:
                _title = 'Cell Measure: ' + self.name(default='')

        return super(CellMeasure, self).dump(
            display=display, omit=omit, field=field, key=key,
             _level=_level, _title=_title)

#        indent1 = '    ' * _level
#        indent2 = '    ' * (_level+1)
#
#        if hasattr(self, 'measure'):
#            string = ['{0}Cell measure: {1}'.format(indent1, self.measure)]
#        elif hasattr(self.Units, 'units'):
#            string = ['{0}Cell measure: {1}'.format(indent1, self.units)]
#        else:
#            string = ['{0}Cell measure: {1}'.format(indent1, self.name(default=''))]
#
#        if self._hasData:
#            if field is not None:
#                x = ['{0}({1})'.format(field.axis_name(axis), field.axis_size(axis))
#                     for axis in field.item_axes(key)]
#                string.append('{0}Data({1}) = {2}'.format(indent2, ', '.join(x), str(self.Data)))
#            else:
#                x = [str(s) for s in self.shape]
#                string.append('{0}Data({1}) = {2}'.format(indent2, ', '.join(x), str(self.Data)))
#        #--- End: if
#
#        if self._simple_properties():
#            string.append(self._dump_simple_properties(_level=_level+1))
#          
#        string = '\n'.join(string)
#       
#        if display:
#            print string
#        else:
#            return string
    #--- End: def

    def identity(self, default=None, relaxed_identity=None):
        '''

Return the cell measure's identity.

The identity is first found of:

* The `!measure` attribute.

* The `standard_name` CF property.

* The `!id` attribute.

* The value of the *default* parameter.

:Parameters:

    default : optional
        If none of `measure`, `standard_name` and `!id` exist then
        return *default*. By default, *default* is None.

:Returns:

    out :
        The identity.

:Examples:

'''
        n = getattr(self, 'measure', None)
        if n is not None:
            return n
        
        return super(CellMeasure, self).identity(default, relaxed_identity=relaxed_identity)
    #--- End: def

    def name(self, default=None, identity=False, ncvar=False, relaxed_identity=None):
        '''Return a name for the cell measure.

By default the name is the first found of the following:

  1. The `!measure` attribute.
  
  2. The `standard_name` CF property.
  
  3. The `!id` attribute.

  4. The `long_name` CF property, preceeded by the string
     ``'long_name:'``.

  5. The `!ncvar` attribute, preceeded by the string ``'ncvar:'``.

  6. The value of the *default* parameter.

Note that ``c.name(identity=True)`` is equivalent to ``c.identity()``.

.. seealso:: `identity`

:Parameters:

    default : *optional*
        If no name can be found then return the value of the *default*
        parameter. By default the default is None.

    identity : bool, optional
        If True then 3. and 4. are not considered as possible names.

    ncvar : bool, optional
        If True then 1., 2., 3. and 4. are not considered as possible
        names.

:Returns:

    out : str
        A  name for the cell measure.

:Examples:

>>> f.standard_name = 'air_temperature'
>>> f.long_name = 'temperature of the air'
>>> f.ncvar = 'tas'
>>> f.name()
'air_temperature'
>>> del f.standard_name
>>> f.name()
'long_name:temperature of the air'
>>> del f.long_name
>>> f.name()
'ncvar:tas'
>>> del f.ncvar
>>> f.name()
None
>>> f.name('no_name')
'no_name'
>>> f.standard_name = 'air_temperature'
>>> f.name('no_name')
'air_temperature'

        '''      
#        if ncvar:
#            if identity:
#                raise ValueError(
#"Can't find name: ncvar and identity parameters can't both be True")
#
#            n = getattr(self, 'ncvar', None)
#            if n is not None:
#                return 'ncvar%%%s' % n
#            
#            return default
#        #--- End: if

        if not ncvar:
            n = getattr(self, 'measure', None)
            if n is not None:
                return n

        return super(CellMeasure, self).name(default,
                                             identity=identity, ncvar=ncvar,
                                             relaxed_identity=relaxed_identity)
    #--- End: def

#--- End: class
