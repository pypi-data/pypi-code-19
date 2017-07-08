# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/map/pokemon/motivated_pokemon.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pogoprotos.data import food_value_pb2 as pogoprotos_dot_data_dot_food__value__pb2
from pogoprotos.data import pokemon_data_pb2 as pogoprotos_dot_data_dot_pokemon__data__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/map/pokemon/motivated_pokemon.proto',
  package='pogoprotos.map.pokemon',
  syntax='proto3',
  serialized_pb=_b('\n.pogoprotos/map/pokemon/motivated_pokemon.proto\x12\x16pogoprotos.map.pokemon\x1a pogoprotos/data/food_value.proto\x1a\"pogoprotos/data/pokemon_data.proto\"\x82\x02\n\x10MotivatedPokemon\x12-\n\x07pokemon\x18\x01 \x01(\x0b\x32\x1c.pogoprotos.data.PokemonData\x12\x11\n\tdeploy_ms\x18\x02 \x01(\x03\x12\x18\n\x10\x63p_when_deployed\x18\x03 \x01(\x05\x12\x16\n\x0emotivation_now\x18\x04 \x01(\x01\x12\x0e\n\x06\x63p_now\x18\x05 \x01(\x05\x12\x13\n\x0b\x62\x65rry_value\x18\x06 \x01(\x02\x12%\n\x1d\x66\x65\x65\x64_cooldown_duration_millis\x18\x07 \x01(\x03\x12.\n\nfood_value\x18\x08 \x03(\x0b\x32\x1a.pogoprotos.data.FoodValueb\x06proto3')
  ,
  dependencies=[pogoprotos_dot_data_dot_food__value__pb2.DESCRIPTOR,pogoprotos_dot_data_dot_pokemon__data__pb2.DESCRIPTOR,])




_MOTIVATEDPOKEMON = _descriptor.Descriptor(
  name='MotivatedPokemon',
  full_name='pogoprotos.map.pokemon.MotivatedPokemon',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pokemon', full_name='pogoprotos.map.pokemon.MotivatedPokemon.pokemon', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='deploy_ms', full_name='pogoprotos.map.pokemon.MotivatedPokemon.deploy_ms', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cp_when_deployed', full_name='pogoprotos.map.pokemon.MotivatedPokemon.cp_when_deployed', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='motivation_now', full_name='pogoprotos.map.pokemon.MotivatedPokemon.motivation_now', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cp_now', full_name='pogoprotos.map.pokemon.MotivatedPokemon.cp_now', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='berry_value', full_name='pogoprotos.map.pokemon.MotivatedPokemon.berry_value', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='feed_cooldown_duration_millis', full_name='pogoprotos.map.pokemon.MotivatedPokemon.feed_cooldown_duration_millis', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='food_value', full_name='pogoprotos.map.pokemon.MotivatedPokemon.food_value', index=7,
      number=8, type=11, cpp_type=10, label=3,
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
  serialized_start=145,
  serialized_end=403,
)

_MOTIVATEDPOKEMON.fields_by_name['pokemon'].message_type = pogoprotos_dot_data_dot_pokemon__data__pb2._POKEMONDATA
_MOTIVATEDPOKEMON.fields_by_name['food_value'].message_type = pogoprotos_dot_data_dot_food__value__pb2._FOODVALUE
DESCRIPTOR.message_types_by_name['MotivatedPokemon'] = _MOTIVATEDPOKEMON
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

MotivatedPokemon = _reflection.GeneratedProtocolMessageType('MotivatedPokemon', (_message.Message,), dict(
  DESCRIPTOR = _MOTIVATEDPOKEMON,
  __module__ = 'pogoprotos.map.pokemon.motivated_pokemon_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.map.pokemon.MotivatedPokemon)
  ))
_sym_db.RegisterMessage(MotivatedPokemon)


# @@protoc_insertion_point(module_scope)
