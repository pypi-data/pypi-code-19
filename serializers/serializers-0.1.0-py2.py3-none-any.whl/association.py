from serializers.attribute import Attribute
from itertools import starmap

class Association(Attribute):
  def __init__( self, parent, name, options = {} ):
    super(Association, self).__init__( parent, name, options )
    self.serializer = options[ 'serializer' ]

  #private

  def _dict_for( self, item):
    return self.serializer( item ).to_dict()

class HasOneAssociation(Association):

  def value_for( self, item, args ):
    # get the object to serialize      
    assoc_item = getattr( item, self.name )

    if (isinstance( assoc_item, list )):
      raise Exception("has_one associations must be applied to a single object, not a list")
    # serialize the object and get its to_dict
    return self._dict_for( assoc_item )

class HasManyAssociation(Association):

  def value_for( self, items, args ):
    # get the objects to serialize      
    assoc_items = getattr( items, self.name )

    if not ( isinstance( assoc_items, list ) ):
      raise Exception("has_many associations must be applied to a list")
    
    # serialize the objects and get their to_dict
    return [ self._dict_for( item ) for item in assoc_items ]
