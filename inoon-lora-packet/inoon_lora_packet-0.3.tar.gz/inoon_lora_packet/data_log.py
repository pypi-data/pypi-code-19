from enum import IntEnum

from inoon_lora_packet.packet import Packet, HexConverter, InvalidPacketError


class LogPosition(IntEnum):
    start = 0,
    intermid = 1,
    finish = 2


class DataLogV2Packet(Packet):
    spec = [
        {'name': 'idx',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': None},

        {'name': 'pos',
         'bytes': 1,
         'convert': HexConverter.hex_to_uint,
         'restrict': [0, 1, 2]},
    ]

    def _field_spec(self):
        return self.spec

    def __init__(self, raw_packet):
        super(self.__class__, self).__init__(raw_packet)

        # TODO: Refactoring parse method.
        data_cnt = len(raw_packet[16:]) - 2

        if data_cnt % 2 is not 0:
            raise InvalidPacketError

        if data_cnt % 12 is not 0:
            raise InvalidPacketError

        self.x = []
        self.y = []
        self.z = []

        for start_idx in range(0, data_cnt, 12):
            parse_log = raw_packet[16:][start_idx:start_idx+12]
            self.x.append(HexConverter.hex_to_int16(parse_log[0:4]))
            self.y.append(HexConverter.hex_to_int16(parse_log[4:8]))
            self.z.append(HexConverter.hex_to_int16(parse_log[8:]))

        self.rssi = HexConverter.hex_to_int8(raw_packet[-2:])

    def __str__(self):
        msg = ''
        msg += 'LOG | '
        msg += 'ID: {} | '.format(self.idx)

        if self.pos == 0:
            msg += 'Alarm'
        elif self.pos == 1:
            msg += 'Mid.'
        elif self.pos == 2:
            msg += 'Finish'
        else:
            msg += '--'
        msg += ' | '

        msg += 'RSSI: {}'.format(self.rssi)
        return msg

    @classmethod
    def encode(self, idx, pos, data_cnt, rssi):
        enc = ''
        enc += format(idx, '02x')
        enc += format(pos, '02x')
        for i in range(0, data_cnt):
            enc += format(0, '04x')
            enc += format(0, '04x')
            enc += format(0, '04x')
        enc += HexConverter.int_to_hex(rssi, 1, True)

        return enc.lower()
