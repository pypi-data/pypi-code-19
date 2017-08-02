from serializers.attribute import ValueAttribute
from serializers.association import HasOneAssociation, HasManyAssociation

import json

class Serializer(object):

  __attributes = {}

  def __init__( self, object, args = {} ):
    self.object = object
    self.args = args

  def __init_subclass__(cls, **kwargs):
      cls.__attributes = {}

  def to_dict( self ):
    blob = {}
    for attribute in self.__class__.__attributes.values( ):
      blob[ attribute.key( ) ] = attribute.value_for( self.object, self.args )

    return blob

  def to_json( self ):
    return json.dumps( self.to_dict(), sort_keys=True )

  # class methods

  @classmethod
  def attribute( cls, name, options = {} ):
    cls.__add_attribute( name, options )
    
    return cls

  @classmethod
  def attributes( cls, *attrs ):
    for attr in attrs:
      cls.__add_attribute( attr )
    
    return cls

  @classmethod
  def has_one( cls, name, options = {} ):
    if options.get( 'serializer', None ) == None:
      raise Exception(f"You must specify a serializer for {cls}.{name}")

    cls.__add_association( HasOneAssociation, name, options )

  @classmethod
  def has_many( cls, name, options = {} ):
    if options.get( 'serializer', None ) == None:
      raise Exception(f"You must specify a serializer for {cls}.{name}")

    cls.__add_association( HasManyAssociation, name, options )

  # private

  @classmethod
  def __add_attribute( cls, name, options = {} ):
    cls.__attributes[ name ] = ValueAttribute( cls, name, options )

  @classmethod
  def __add_association( cls, association, name, options = {} ):
    cls.__attributes[ name ] = association( cls, name, options )