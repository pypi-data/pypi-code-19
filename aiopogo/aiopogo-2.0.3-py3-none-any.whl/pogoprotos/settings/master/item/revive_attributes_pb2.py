# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/settings/master/item/revive_attributes.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/settings/master/item/revive_attributes.proto',
  package='pogoprotos.settings.master.item',
  syntax='proto3',
  serialized_pb=_b('\n7pogoprotos/settings/master/item/revive_attributes.proto\x12\x1fpogoprotos.settings.master.item\"\'\n\x10ReviveAttributes\x12\x13\n\x0bsta_percent\x18\x01 \x01(\x02\x62\x06proto3')
)




_REVIVEATTRIBUTES = _descriptor.Descriptor(
  name='ReviveAttributes',
  full_name='pogoprotos.settings.master.item.ReviveAttributes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sta_percent', full_name='pogoprotos.settings.master.item.ReviveAttributes.sta_percent', index=0,
      number=1, type=2, cpp_type=6, label=1,
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
  serialized_start=92,
  serialized_end=131,
)

DESCRIPTOR.message_types_by_name['ReviveAttributes'] = _REVIVEATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ReviveAttributes = _reflection.GeneratedProtocolMessageType('ReviveAttributes', (_message.Message,), dict(
  DESCRIPTOR = _REVIVEATTRIBUTES,
  __module__ = 'pogoprotos.settings.master.item.revive_attributes_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.settings.master.item.ReviveAttributes)
  ))
_sym_db.RegisterMessage(ReviveAttributes)


# @@protoc_insertion_point(module_scope)
