from enum import IntEnum

from inoon_lora_packet.packet import Packet, HexConverter


class AckType(IntEnum):
    ext_mgmt = 0x00,
    dev_reset = 0x80,
    per_change = 0x81,
    immediate = 0x82


class AckV2Packet(Packet):
    def _field_spec(self):
        return [
            {'name': 'ack_type',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [AckType[k] for k in AckType._member_map_]},

            {'name': 'rssi',
             'bytes': 1,
             'convert': HexConverter.hex_to_int8,
             'restrict': None},
        ]

    @classmethod
    def encode(cls, ack_type, rssi):
        enc = ''
        enc += format(ack_type, '02x')
        enc += HexConverter.int_to_hex(rssi, 1, True)
        return enc
