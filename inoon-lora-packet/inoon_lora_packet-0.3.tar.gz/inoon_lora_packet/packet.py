import abc
from enum import IntEnum


class InvalidPacketError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__('Invalid RAW Packet.')


class NotSupportedPacketError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__('Not Supported packet')


class RestrictedValueError(Exception):
    def __init__(self):
        super(self.__class__, self).__init__('Restricted Value Occured')


class HexConverter():
    # TODO: Convert bugs..
    @classmethod
    def _hex_to_sint(cls, hexstr, size):
        value = int(hexstr[-2*size:], 16)
        if value & (0x1 << (size * 8 - 1)):
            bit_mask = 0
            for _ in range(0, size):
                bit_mask = (bit_mask << 8) | 0xFF

            absolute = (value ^ bit_mask) + 1
            convert_value = -absolute
        else:
            convert_value = value
        return convert_value

    @classmethod
    def hex_to_int8(cls, hexstr):
        return HexConverter._hex_to_sint(hexstr, 1)

    @classmethod
    def hex_to_int16(cls, hexstr):
        return HexConverter._hex_to_sint(hexstr, 2)

    @classmethod
    def hex_to_uint(cls, hexstr):
        return int(hexstr, 16)

    @classmethod
    def int_to_hex(cls, value, byte_len, is_signed):
        mask = 0
        for _ in range(0, byte_len):
            mask = (mask << 8) | 0xFF

        if is_signed is True and value < 0:
            hex_val = ((abs(value) ^ mask) & mask) + 1
        else:
            hex_val = value

        result_len = byte_len * 2
        hex_str = '{:X}'.format(hex_val)
        remain_len = result_len - len(hex_str)

        padding = ''
        for _ in range(0, remain_len):
            padding += '0'

        return padding + hex_str


class BitField():
    pass


class DeviceType(IntEnum):
    mgi = 2


class PacketType(IntEnum):
    alive = 1
    event = 2
    error = 3
    ack = 4
    notice = 5
    data_log = 6


class RequestType(IntEnum):
    none = 0
    sync = 1
    config = 2


class Packet(abc.ABC):
    def __init__(self, raw_packet):
        self.raw_packet = raw_packet
        self._parse(raw_packet)

    @abc.abstractmethod
    def _field_spec(self):
        pass

    def _parse(self, raw_packet):
        last_idx = 0
        for i, spec in enumerate(self._field_spec()):
            start = last_idx * 2

            length = int(spec['bytes'])
            end = start + 2*length

            raw_value = raw_packet[start:end]

            # TODO: Simplify code.
            if 'bit_fields' in spec:
                setattr(self, spec['name'], BitField())
                new_attr = getattr(self, spec['name'])

                bits = 8
                for i, bit_spec in enumerate(spec['bit_fields']):
                    bit_mask = 0
                    for i in range(0, bit_spec['bits']):
                        bit_mask = bit_mask << 1
                        bit_mask |= 0x1

                    bit_mask = bit_mask << (bits - bit_spec['bits'])
                    bit_value = (int(raw_value, 16) & bit_mask)
                    bit_value = bit_value >> (bits - bit_spec['bits'])

                    self._valid_restrict(bit_spec['restrict'], bit_value)

                    setattr(new_attr, bit_spec['name'], bit_value)

                    bits -= bit_spec['bits']
            else:
                try:
                    convert_val = spec['convert'](raw_value)
                except ValueError:
                    raise InvalidPacketError

                self._valid_restrict(spec['restrict'], convert_val)
                setattr(self, spec['name'], convert_val)

            last_idx += length

    def _valid_restrict(self, restrict, value):
        if restrict is not None and value not in restrict:
            raise RestrictedValueError


class PacketHeader(Packet):
    def _field_spec(self):
        return [
            {'name': 'ver',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': [2]},

            {'name': 'resv',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'id',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': None},

            {'name': 'dev',
             'bytes': 2,
             'convert': HexConverter.hex_to_uint,
             'restrict': [1, 2]},

            {'name': 'packet',
             'bytes': 1,
             'bit_fields': [
                 {'name': 'type', 'bits': 4, 'restrict': [1, 2, 3, 4, 5, 6]},
                 {'name': 'req', 'bits': 4, 'restrict': [0, 1, 2]},
             ]},

            {'name': 'battery',
             'bytes': 1,
             'convert': HexConverter.hex_to_uint,
             'restrict': range(0, 101)},

            {'name': 'temperature',
             'bytes': 1,
             'convert': HexConverter.hex_to_int8,
             'restrict': range(-30, 80)},
        ]

    def __init__(self, raw_packet):
        super(self.__class__, self).__init__(raw_packet)

    @classmethod
    def encode(cls, ver, id, dev_type, packet_type, req_type, bat, temp):
        enc = ''
        enc += format(ver, '02x')
        enc += '00'
        enc += format(id, '02x')
        enc += format(dev_type, '04x')
        enc += format(packet_type, 'x')
        enc += format(req_type, 'x')
        enc += format(bat, '02x')
        enc += HexConverter.int_to_hex(temp, 1, True)
        return enc.lower()
