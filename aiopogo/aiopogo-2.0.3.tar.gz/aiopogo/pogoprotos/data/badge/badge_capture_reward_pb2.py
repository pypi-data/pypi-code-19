# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/data/badge/badge_capture_reward.proto

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
  name='pogoprotos/data/badge/badge_capture_reward.proto',
  package='pogoprotos.data.badge',
  syntax='proto3',
  serialized_pb=_b('\n0pogoprotos/data/badge/badge_capture_reward.proto\x12\x15pogoprotos.data.badge\"T\n\x12\x42\x61\x64geCaptureReward\x12!\n\x19\x63\x61pture_reward_multiplier\x18\x01 \x01(\x02\x12\x1b\n\x13\x61vatar_template_ids\x18\x02 \x03(\tb\x06proto3')
)




_BADGECAPTUREREWARD = _descriptor.Descriptor(
  name='BadgeCaptureReward',
  full_name='pogoprotos.data.badge.BadgeCaptureReward',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='capture_reward_multiplier', full_name='pogoprotos.data.badge.BadgeCaptureReward.capture_reward_multiplier', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar_template_ids', full_name='pogoprotos.data.badge.BadgeCaptureReward.avatar_template_ids', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=75,
  serialized_end=159,
)

DESCRIPTOR.message_types_by_name['BadgeCaptureReward'] = _BADGECAPTUREREWARD
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

BadgeCaptureReward = _reflection.GeneratedProtocolMessageType('BadgeCaptureReward', (_message.Message,), dict(
  DESCRIPTOR = _BADGECAPTUREREWARD,
  __module__ = 'pogoprotos.data.badge.badge_capture_reward_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.data.badge.BadgeCaptureReward)
  ))
_sym_db.RegisterMessage(BadgeCaptureReward)


# @@protoc_insertion_point(module_scope)
