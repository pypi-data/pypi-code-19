# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/networking/requests/messages/download_item_templates_message.proto

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
  name='pogoprotos/networking/requests/messages/download_item_templates_message.proto',
  package='pogoprotos.networking.requests.messages',
  syntax='proto3',
  serialized_pb=_b('\nMpogoprotos/networking/requests/messages/download_item_templates_message.proto\x12\'pogoprotos.networking.requests.messages\"]\n\x1c\x44ownloadItemTemplatesMessage\x12\x10\n\x08paginate\x18\x01 \x01(\x08\x12\x13\n\x0bpage_offset\x18\x02 \x01(\x05\x12\x16\n\x0epage_timestamp\x18\x03 \x01(\x04\x62\x06proto3')
)




_DOWNLOADITEMTEMPLATESMESSAGE = _descriptor.Descriptor(
  name='DownloadItemTemplatesMessage',
  full_name='pogoprotos.networking.requests.messages.DownloadItemTemplatesMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='paginate', full_name='pogoprotos.networking.requests.messages.DownloadItemTemplatesMessage.paginate', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='page_offset', full_name='pogoprotos.networking.requests.messages.DownloadItemTemplatesMessage.page_offset', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='page_timestamp', full_name='pogoprotos.networking.requests.messages.DownloadItemTemplatesMessage.page_timestamp', index=2,
      number=3, type=4, cpp_type=4, label=1,
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
  serialized_start=122,
  serialized_end=215,
)

DESCRIPTOR.message_types_by_name['DownloadItemTemplatesMessage'] = _DOWNLOADITEMTEMPLATESMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DownloadItemTemplatesMessage = _reflection.GeneratedProtocolMessageType('DownloadItemTemplatesMessage', (_message.Message,), dict(
  DESCRIPTOR = _DOWNLOADITEMTEMPLATESMESSAGE,
  __module__ = 'pogoprotos.networking.requests.messages.download_item_templates_message_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.networking.requests.messages.DownloadItemTemplatesMessage)
  ))
_sym_db.RegisterMessage(DownloadItemTemplatesMessage)


# @@protoc_insertion_point(module_scope)
