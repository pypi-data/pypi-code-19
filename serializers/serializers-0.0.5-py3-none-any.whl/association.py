from serializers.attribute import Attribute
from itertools import starmap

class Association(Attribute):
  def __init__( self, parent, name, options = {} ):
    super().__init__( parent, name, options )
    self.serializer = options[ 'serializer' ]

  #private

  def _dict_for( self, object ):
    return self.serializer( object ).to_dict()

class HasOneAssociation(Association):

  def value_for( self, object, args ):
    # get the object to serialize      
    assoc = getattr( object, self.name )

    if (isinstance( assoc, list )):
      raise Exception("has_one associations must be applied to a single object, not a list")
    # serialize the object and get its to_dict
    return self._dict_for( assoc )

class HasManyAssociation(Association):

  def value_for( self, objects, args ):
    # get the objects to serialize      
    assocs = getattr( objects, self.name )

    if not ( isinstance( assocs, list ) ):
      raise Exception("has_many associations must be applied to a list")
    
    # serialize the objects and get their to_dict
    return [ self._dict_for( obj ) for obj in assocs ]
