# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/data/player/currency.proto

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
  name='pogoprotos/data/player/currency.proto',
  package='pogoprotos.data.player',
  syntax='proto3',
  serialized_pb=_b('\n%pogoprotos/data/player/currency.proto\x12\x16pogoprotos.data.player\"(\n\x08\x43urrency\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06\x61mount\x18\x02 \x01(\x05\x62\x06proto3')
)




_CURRENCY = _descriptor.Descriptor(
  name='Currency',
  full_name='pogoprotos.data.player.Currency',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='pogoprotos.data.player.Currency.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='amount', full_name='pogoprotos.data.player.Currency.amount', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=65,
  serialized_end=105,
)

DESCRIPTOR.message_types_by_name['Currency'] = _CURRENCY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Currency = _reflection.GeneratedProtocolMessageType('Currency', (_message.Message,), dict(
  DESCRIPTOR = _CURRENCY,
  __module__ = 'pogoprotos.data.player.currency_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.data.player.Currency)
  ))
_sym_db.RegisterMessage(Currency)


# @@protoc_insertion_point(module_scope)
