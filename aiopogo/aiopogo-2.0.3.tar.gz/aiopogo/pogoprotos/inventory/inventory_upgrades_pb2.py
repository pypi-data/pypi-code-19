# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/inventory/inventory_upgrades.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from pogoprotos.inventory import inventory_upgrade_pb2 as pogoprotos_dot_inventory_dot_inventory__upgrade__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/inventory/inventory_upgrades.proto',
  package='pogoprotos.inventory',
  syntax='proto3',
  serialized_pb=_b('\n-pogoprotos/inventory/inventory_upgrades.proto\x12\x14pogoprotos.inventory\x1a,pogoprotos/inventory/inventory_upgrade.proto\"W\n\x11InventoryUpgrades\x12\x42\n\x12inventory_upgrades\x18\x01 \x03(\x0b\x32&.pogoprotos.inventory.InventoryUpgradeb\x06proto3')
  ,
  dependencies=[pogoprotos_dot_inventory_dot_inventory__upgrade__pb2.DESCRIPTOR,])




_INVENTORYUPGRADES = _descriptor.Descriptor(
  name='InventoryUpgrades',
  full_name='pogoprotos.inventory.InventoryUpgrades',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='inventory_upgrades', full_name='pogoprotos.inventory.InventoryUpgrades.inventory_upgrades', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=117,
  serialized_end=204,
)

_INVENTORYUPGRADES.fields_by_name['inventory_upgrades'].message_type = pogoprotos_dot_inventory_dot_inventory__upgrade__pb2._INVENTORYUPGRADE
DESCRIPTOR.message_types_by_name['InventoryUpgrades'] = _INVENTORYUPGRADES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

InventoryUpgrades = _reflection.GeneratedProtocolMessageType('InventoryUpgrades', (_message.Message,), dict(
  DESCRIPTOR = _INVENTORYUPGRADES,
  __module__ = 'pogoprotos.inventory.inventory_upgrades_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.inventory.InventoryUpgrades)
  ))
_sym_db.RegisterMessage(InventoryUpgrades)


# @@protoc_insertion_point(module_scope)
