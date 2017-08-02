class Attribute(object):

  def __init__( self, parent, name, options = {} ):
    self.name = name
    self.options = options
    self.parent = parent

  def key( self ):
    return self.options.get('key', self.name)

class ValueAttribute(Attribute):

  def value_for( self, object, args = {} ):
    if hasattr( object, self.name ):
      val = getattr( object, self.name )
      if callable( val ):
        val = val()
      return val 
    else:
      return getattr( self.parent, self.name )( object, args )
