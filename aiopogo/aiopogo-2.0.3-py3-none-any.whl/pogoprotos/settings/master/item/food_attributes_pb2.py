# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/settings/master/item/food_attributes.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pogoprotos.enums import item_effect_pb2 as pogoprotos_dot_enums_dot_item__effect__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/settings/master/item/food_attributes.proto',
  package='pogoprotos.settings.master.item',
  syntax='proto3',
  serialized_pb=_b('\n5pogoprotos/settings/master/item/food_attributes.proto\x12\x1fpogoprotos.settings.master.item\x1a\"pogoprotos/enums/item_effect.proto\"\x92\x01\n\x0e\x46oodAttributes\x12\x31\n\x0bitem_effect\x18\x01 \x03(\x0e\x32\x1c.pogoprotos.enums.ItemEffect\x12\x1b\n\x13item_effect_percent\x18\x02 \x03(\x02\x12\x16\n\x0egrowth_percent\x18\x03 \x01(\x02\x12\x18\n\x10\x62\x65rry_multiplier\x18\x04 \x01(\x02\x62\x06proto3')
  ,
  dependencies=[pogoprotos_dot_enums_dot_item__effect__pb2.DESCRIPTOR,])




_FOODATTRIBUTES = _descriptor.Descriptor(
  name='FoodAttributes',
  full_name='pogoprotos.settings.master.item.FoodAttributes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='item_effect', full_name='pogoprotos.settings.master.item.FoodAttributes.item_effect', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='item_effect_percent', full_name='pogoprotos.settings.master.item.FoodAttributes.item_effect_percent', index=1,
      number=2, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='growth_percent', full_name='pogoprotos.settings.master.item.FoodAttributes.growth_percent', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='berry_multiplier', full_name='pogoprotos.settings.master.item.FoodAttributes.berry_multiplier', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=127,
  serialized_end=273,
)

_FOODATTRIBUTES.fields_by_name['item_effect'].enum_type = pogoprotos_dot_enums_dot_item__effect__pb2._ITEMEFFECT
DESCRIPTOR.message_types_by_name['FoodAttributes'] = _FOODATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FoodAttributes = _reflection.GeneratedProtocolMessageType('FoodAttributes', (_message.Message,), dict(
  DESCRIPTOR = _FOODATTRIBUTES,
  __module__ = 'pogoprotos.settings.master.item.food_attributes_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.settings.master.item.FoodAttributes)
  ))
_sym_db.RegisterMessage(FoodAttributes)


# @@protoc_insertion_point(module_scope)
