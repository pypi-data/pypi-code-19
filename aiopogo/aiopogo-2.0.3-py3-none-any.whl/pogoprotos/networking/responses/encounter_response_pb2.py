# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/networking/responses/encounter_response.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pogoprotos.data.capture import capture_probability_pb2 as pogoprotos_dot_data_dot_capture_dot_capture__probability__pb2
from pogoprotos.inventory.item import item_id_pb2 as pogoprotos_dot_inventory_dot_item_dot_item__id__pb2
from pogoprotos.map.pokemon import wild_pokemon_pb2 as pogoprotos_dot_map_dot_pokemon_dot_wild__pokemon__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/networking/responses/encounter_response.proto',
  package='pogoprotos.networking.responses',
  syntax='proto3',
  serialized_pb=_b('\n8pogoprotos/networking/responses/encounter_response.proto\x12\x1fpogoprotos.networking.responses\x1a\x31pogoprotos/data/capture/capture_probability.proto\x1a\'pogoprotos/inventory/item/item_id.proto\x1a)pogoprotos/map/pokemon/wild_pokemon.proto\"\xec\x04\n\x11\x45ncounterResponse\x12\x39\n\x0cwild_pokemon\x18\x01 \x01(\x0b\x32#.pogoprotos.map.pokemon.WildPokemon\x12Q\n\nbackground\x18\x02 \x01(\x0e\x32=.pogoprotos.networking.responses.EncounterResponse.Background\x12I\n\x06status\x18\x03 \x01(\x0e\x32\x39.pogoprotos.networking.responses.EncounterResponse.Status\x12H\n\x13\x63\x61pture_probability\x18\x04 \x01(\x0b\x32+.pogoprotos.data.capture.CaptureProbability\x12\x36\n\x0b\x61\x63tive_item\x18\x05 \x01(\x0e\x32!.pogoprotos.inventory.item.ItemId\"\"\n\nBackground\x12\x08\n\x04PARK\x10\x00\x12\n\n\x06\x44\x45SERT\x10\x01\"\xd7\x01\n\x06Status\x12\x13\n\x0f\x45NCOUNTER_ERROR\x10\x00\x12\x15\n\x11\x45NCOUNTER_SUCCESS\x10\x01\x12\x17\n\x13\x45NCOUNTER_NOT_FOUND\x10\x02\x12\x14\n\x10\x45NCOUNTER_CLOSED\x10\x03\x12\x1a\n\x16\x45NCOUNTER_POKEMON_FLED\x10\x04\x12\x1a\n\x16\x45NCOUNTER_NOT_IN_RANGE\x10\x05\x12\x1e\n\x1a\x45NCOUNTER_ALREADY_HAPPENED\x10\x06\x12\x1a\n\x16POKEMON_INVENTORY_FULL\x10\x07\x62\x06proto3')
  ,
  dependencies=[pogoprotos_dot_data_dot_capture_dot_capture__probability__pb2.DESCRIPTOR,pogoprotos_dot_inventory_dot_item_dot_item__id__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_pokemon_dot_wild__pokemon__pb2.DESCRIPTOR,])



_ENCOUNTERRESPONSE_BACKGROUND = _descriptor.EnumDescriptor(
  name='Background',
  full_name='pogoprotos.networking.responses.EncounterResponse.Background',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PARK', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DESERT', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=597,
  serialized_end=631,
)
_sym_db.RegisterEnumDescriptor(_ENCOUNTERRESPONSE_BACKGROUND)

_ENCOUNTERRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='pogoprotos.networking.responses.EncounterResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_ERROR', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_SUCCESS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_NOT_FOUND', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_CLOSED', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_POKEMON_FLED', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_NOT_IN_RANGE', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENCOUNTER_ALREADY_HAPPENED', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='POKEMON_INVENTORY_FULL', index=7, number=7,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=634,
  serialized_end=849,
)
_sym_db.RegisterEnumDescriptor(_ENCOUNTERRESPONSE_STATUS)


_ENCOUNTERRESPONSE = _descriptor.Descriptor(
  name='EncounterResponse',
  full_name='pogoprotos.networking.responses.EncounterResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='wild_pokemon', full_name='pogoprotos.networking.responses.EncounterResponse.wild_pokemon', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='background', full_name='pogoprotos.networking.responses.EncounterResponse.background', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='pogoprotos.networking.responses.EncounterResponse.status', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='capture_probability', full_name='pogoprotos.networking.responses.EncounterResponse.capture_probability', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='active_item', full_name='pogoprotos.networking.responses.EncounterResponse.active_item', index=4,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _ENCOUNTERRESPONSE_BACKGROUND,
    _ENCOUNTERRESPONSE_STATUS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=229,
  serialized_end=849,
)

_ENCOUNTERRESPONSE.fields_by_name['wild_pokemon'].message_type = pogoprotos_dot_map_dot_pokemon_dot_wild__pokemon__pb2._WILDPOKEMON
_ENCOUNTERRESPONSE.fields_by_name['background'].enum_type = _ENCOUNTERRESPONSE_BACKGROUND
_ENCOUNTERRESPONSE.fields_by_name['status'].enum_type = _ENCOUNTERRESPONSE_STATUS
_ENCOUNTERRESPONSE.fields_by_name['capture_probability'].message_type = pogoprotos_dot_data_dot_capture_dot_capture__probability__pb2._CAPTUREPROBABILITY
_ENCOUNTERRESPONSE.fields_by_name['active_item'].enum_type = pogoprotos_dot_inventory_dot_item_dot_item__id__pb2._ITEMID
_ENCOUNTERRESPONSE_BACKGROUND.containing_type = _ENCOUNTERRESPONSE
_ENCOUNTERRESPONSE_STATUS.containing_type = _ENCOUNTERRESPONSE
DESCRIPTOR.message_types_by_name['EncounterResponse'] = _ENCOUNTERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

EncounterResponse = _reflection.GeneratedProtocolMessageType('EncounterResponse', (_message.Message,), dict(
  DESCRIPTOR = _ENCOUNTERRESPONSE,
  __module__ = 'pogoprotos.networking.responses.encounter_response_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.networking.responses.EncounterResponse)
  ))
_sym_db.RegisterMessage(EncounterResponse)


# @@protoc_insertion_point(module_scope)
