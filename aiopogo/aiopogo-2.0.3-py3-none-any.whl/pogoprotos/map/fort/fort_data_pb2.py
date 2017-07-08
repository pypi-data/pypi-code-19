# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/map/fort/fort_data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pogoprotos.data import pokemon_display_pb2 as pogoprotos_dot_data_dot_pokemon__display__pb2
from pogoprotos.data.raid import raid_info_pb2 as pogoprotos_dot_data_dot_raid_dot_raid__info__pb2
from pogoprotos.enums import pokemon_id_pb2 as pogoprotos_dot_enums_dot_pokemon__id__pb2
from pogoprotos.enums import team_color_pb2 as pogoprotos_dot_enums_dot_team__color__pb2
from pogoprotos.inventory.item import item_id_pb2 as pogoprotos_dot_inventory_dot_item_dot_item__id__pb2
from pogoprotos.map.fort import gym_display_pb2 as pogoprotos_dot_map_dot_fort_dot_gym__display__pb2
from pogoprotos.map.fort import fort_type_pb2 as pogoprotos_dot_map_dot_fort_dot_fort__type__pb2
from pogoprotos.map.fort import fort_sponsor_pb2 as pogoprotos_dot_map_dot_fort_dot_fort__sponsor__pb2
from pogoprotos.map.fort import fort_rendering_type_pb2 as pogoprotos_dot_map_dot_fort_dot_fort__rendering__type__pb2
from pogoprotos.map.fort import fort_lure_info_pb2 as pogoprotos_dot_map_dot_fort_dot_fort__lure__info__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/map/fort/fort_data.proto',
  package='pogoprotos.map.fort',
  syntax='proto3',
  serialized_pb=_b('\n#pogoprotos/map/fort/fort_data.proto\x12\x13pogoprotos.map.fort\x1a%pogoprotos/data/pokemon_display.proto\x1a$pogoprotos/data/raid/raid_info.proto\x1a!pogoprotos/enums/pokemon_id.proto\x1a!pogoprotos/enums/team_color.proto\x1a\'pogoprotos/inventory/item/item_id.proto\x1a%pogoprotos/map/fort/gym_display.proto\x1a#pogoprotos/map/fort/fort_type.proto\x1a&pogoprotos/map/fort/fort_sponsor.proto\x1a-pogoprotos/map/fort/fort_rendering_type.proto\x1a(pogoprotos/map/fort/fort_lure_info.proto\"\x9a\x07\n\x08\x46ortData\x12\n\n\x02id\x18\x01 \x01(\t\x12\"\n\x1alast_modified_timestamp_ms\x18\x02 \x01(\x03\x12\x10\n\x08latitude\x18\x03 \x01(\x01\x12\x11\n\tlongitude\x18\x04 \x01(\x01\x12\x32\n\rowned_by_team\x18\x05 \x01(\x0e\x32\x1b.pogoprotos.enums.TeamColor\x12\x35\n\x10guard_pokemon_id\x18\x06 \x01(\x0e\x32\x1b.pogoprotos.enums.PokemonId\x12\x18\n\x10guard_pokemon_cp\x18\x07 \x01(\x05\x12\x0f\n\x07\x65nabled\x18\x08 \x01(\x08\x12+\n\x04type\x18\t \x01(\x0e\x32\x1d.pogoprotos.map.fort.FortType\x12\x12\n\ngym_points\x18\n \x01(\x03\x12\x14\n\x0cis_in_battle\x18\x0b \x01(\x08\x12?\n\x14\x61\x63tive_fort_modifier\x18\x0c \x03(\x0e\x32!.pogoprotos.inventory.item.ItemId\x12\x34\n\tlure_info\x18\r \x01(\x0b\x32!.pogoprotos.map.fort.FortLureInfo\x12&\n\x1e\x63ooldown_complete_timestamp_ms\x18\x0e \x01(\x03\x12\x31\n\x07sponsor\x18\x0f \x01(\x0e\x32 .pogoprotos.map.fort.FortSponsor\x12>\n\x0erendering_type\x18\x10 \x01(\x0e\x32&.pogoprotos.map.fort.FortRenderingType\x12\x1d\n\x15\x64\x65ploy_lockout_end_ms\x18\x11 \x01(\x03\x12>\n\x15guard_pokemon_display\x18\x12 \x01(\x0b\x32\x1f.pogoprotos.data.PokemonDisplay\x12\x0e\n\x06\x63losed\x18\x13 \x01(\x08\x12\x31\n\traid_info\x18\x14 \x01(\x0b\x32\x1e.pogoprotos.data.raid.RaidInfo\x12\x34\n\x0bgym_display\x18\x15 \x01(\x0b\x32\x1f.pogoprotos.map.fort.GymDisplay\x12\x0f\n\x07visited\x18\x16 \x01(\x08\x12\'\n\x1fsame_team_deploy_lockout_end_ms\x18\x17 \x01(\x03\x12\x15\n\rallow_checkin\x18\x18 \x01(\x08\x12\x11\n\timage_url\x18\x19 \x01(\tb\x06proto3')
  ,
  dependencies=[pogoprotos_dot_data_dot_pokemon__display__pb2.DESCRIPTOR,pogoprotos_dot_data_dot_raid_dot_raid__info__pb2.DESCRIPTOR,pogoprotos_dot_enums_dot_pokemon__id__pb2.DESCRIPTOR,pogoprotos_dot_enums_dot_team__color__pb2.DESCRIPTOR,pogoprotos_dot_inventory_dot_item_dot_item__id__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_fort_dot_gym__display__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_fort_dot_fort__type__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_fort_dot_fort__sponsor__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_fort_dot_fort__rendering__type__pb2.DESCRIPTOR,pogoprotos_dot_map_dot_fort_dot_fort__lure__info__pb2.DESCRIPTOR,])




_FORTDATA = _descriptor.Descriptor(
  name='FortData',
  full_name='pogoprotos.map.fort.FortData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='pogoprotos.map.fort.FortData.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='last_modified_timestamp_ms', full_name='pogoprotos.map.fort.FortData.last_modified_timestamp_ms', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='latitude', full_name='pogoprotos.map.fort.FortData.latitude', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='longitude', full_name='pogoprotos.map.fort.FortData.longitude', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='owned_by_team', full_name='pogoprotos.map.fort.FortData.owned_by_team', index=4,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='guard_pokemon_id', full_name='pogoprotos.map.fort.FortData.guard_pokemon_id', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='guard_pokemon_cp', full_name='pogoprotos.map.fort.FortData.guard_pokemon_cp', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enabled', full_name='pogoprotos.map.fort.FortData.enabled', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='pogoprotos.map.fort.FortData.type', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gym_points', full_name='pogoprotos.map.fort.FortData.gym_points', index=9,
      number=10, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_in_battle', full_name='pogoprotos.map.fort.FortData.is_in_battle', index=10,
      number=11, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='active_fort_modifier', full_name='pogoprotos.map.fort.FortData.active_fort_modifier', index=11,
      number=12, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lure_info', full_name='pogoprotos.map.fort.FortData.lure_info', index=12,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cooldown_complete_timestamp_ms', full_name='pogoprotos.map.fort.FortData.cooldown_complete_timestamp_ms', index=13,
      number=14, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sponsor', full_name='pogoprotos.map.fort.FortData.sponsor', index=14,
      number=15, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rendering_type', full_name='pogoprotos.map.fort.FortData.rendering_type', index=15,
      number=16, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='deploy_lockout_end_ms', full_name='pogoprotos.map.fort.FortData.deploy_lockout_end_ms', index=16,
      number=17, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='guard_pokemon_display', full_name='pogoprotos.map.fort.FortData.guard_pokemon_display', index=17,
      number=18, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='closed', full_name='pogoprotos.map.fort.FortData.closed', index=18,
      number=19, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='raid_info', full_name='pogoprotos.map.fort.FortData.raid_info', index=19,
      number=20, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gym_display', full_name='pogoprotos.map.fort.FortData.gym_display', index=20,
      number=21, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='visited', full_name='pogoprotos.map.fort.FortData.visited', index=21,
      number=22, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='same_team_deploy_lockout_end_ms', full_name='pogoprotos.map.fort.FortData.same_team_deploy_lockout_end_ms', index=22,
      number=23, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allow_checkin', full_name='pogoprotos.map.fort.FortData.allow_checkin', index=23,
      number=24, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='image_url', full_name='pogoprotos.map.fort.FortData.image_url', index=24,
      number=25, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=454,
  serialized_end=1376,
)

_FORTDATA.fields_by_name['owned_by_team'].enum_type = pogoprotos_dot_enums_dot_team__color__pb2._TEAMCOLOR
_FORTDATA.fields_by_name['guard_pokemon_id'].enum_type = pogoprotos_dot_enums_dot_pokemon__id__pb2._POKEMONID
_FORTDATA.fields_by_name['type'].enum_type = pogoprotos_dot_map_dot_fort_dot_fort__type__pb2._FORTTYPE
_FORTDATA.fields_by_name['active_fort_modifier'].enum_type = pogoprotos_dot_inventory_dot_item_dot_item__id__pb2._ITEMID
_FORTDATA.fields_by_name['lure_info'].message_type = pogoprotos_dot_map_dot_fort_dot_fort__lure__info__pb2._FORTLUREINFO
_FORTDATA.fields_by_name['sponsor'].enum_type = pogoprotos_dot_map_dot_fort_dot_fort__sponsor__pb2._FORTSPONSOR
_FORTDATA.fields_by_name['rendering_type'].enum_type = pogoprotos_dot_map_dot_fort_dot_fort__rendering__type__pb2._FORTRENDERINGTYPE
_FORTDATA.fields_by_name['guard_pokemon_display'].message_type = pogoprotos_dot_data_dot_pokemon__display__pb2._POKEMONDISPLAY
_FORTDATA.fields_by_name['raid_info'].message_type = pogoprotos_dot_data_dot_raid_dot_raid__info__pb2._RAIDINFO
_FORTDATA.fields_by_name['gym_display'].message_type = pogoprotos_dot_map_dot_fort_dot_gym__display__pb2._GYMDISPLAY
DESCRIPTOR.message_types_by_name['FortData'] = _FORTDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FortData = _reflection.GeneratedProtocolMessageType('FortData', (_message.Message,), dict(
  DESCRIPTOR = _FORTDATA,
  __module__ = 'pogoprotos.map.fort.fort_data_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.map.fort.FortData)
  ))
_sym_db.RegisterMessage(FortData)


# @@protoc_insertion_point(module_scope)
