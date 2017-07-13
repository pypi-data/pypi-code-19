import asyncio
import struct

from binascii import hexlify
from typing import Any
from uuid import UUID

from Crypto.Cipher import AES

from .beacon import Beacon


class PacketType:
    """Enum emulation class."""

    KEEPALIVE = 0
    DATA = 1
    SECURE = 2


HEADER_LENGTH = 3
BEACONS = {}  # type: Dict[bytes, Beacon]


class SecBeaconProtocol(object):
    callback = None

    def __init__(self):
        self._rx_buf = bytearray()
        self.transport = None

    def connection_made(self,
                        transport: Any) -> None:
        self.transport = transport
        self.peername = transport.get_extra_info('peername')[0]
        print("{} has connected".format(self.peername))

    def eof_received(self):
        print("{} has disconnected".format(self.peername))

    def data_received(self, data: bytes) -> None:
        if 0x7e not in data:
            self._rx_buf.extend(data)
        else:
            escape = False
            for byte in data:
                if byte == 0x7e:
                    if len(self._rx_buf) > 0:
                        asyncio.async(self.process_packet(self._rx_buf))
                        self._rx_buf = bytearray()
                    continue
                elif byte == 0x7d:
                    escape = True
                    continue
                else:
                    if escape:
                        byte = byte | (1 << 5)
                        escape = False
                    self._rx_buf.append(byte)

    async def process_packet(self, packet):
        # Header Parsing
        if len(packet) <= HEADER_LENGTH:
            self.transport.write(b'NACK')
            print("Bad packet from: {}".format(self.peername))
            return
        header, record_length, l_id_len = struct.unpack(
            "BBB", packet[:HEADER_LENGTH])
        # version = header >> 4  # Protocol version information unused
        packet_type = header & 0x0f
        l_id = packet[HEADER_LENGTH:HEADER_LENGTH + l_id_len]
        msg = {"peer": self.peername}
        if not l_id:
            self.transport.write(b'NACK')
            msg["type"] = "listener_error"
            msg["data"] = "Invalid or missing listener id"
            if self.callback:
                await self.callback(msg)
            else:
                print(msg)
            return
        if l_id_len == 6:
            try:
                l_id = hexlify(l_id)
            except ValueError:
                # By convention, 6 byte listener IDs will be a MAC
                # address transmitted in binary, but not always... So
                # we try to decode them into something human readable
                pass
        msg["l_id"] = l_id.decode()
        # Report Processing
        data = packet[HEADER_LENGTH + l_id_len:]
        if packet_type == PacketType.DATA:
            msg["type"] = "ibeacon"
            data_l = []
            m_data = {}
            m_data["num_reports"] = num_reports = len(data) // record_length
            for idx in range(num_reports):
                m_data = {}
                rpt = data[idx * record_length:(idx + 1) * record_length]
                (uuid, m_data["major"], m_data["minor"], m_data["count"],
                 distance_cm,
                 variance_cm) = struct.unpack(
                     "!16sHHHHH", rpt)
                m_data["distance"] = distance_cm / 100.0
                m_data["variance"] = variance_cm / 100.0
                m_data["uuid"] = str(UUID(bytes=uuid))
                data_l.append(m_data)
            msg["data"] = data_l

        elif packet_type == PacketType.SECURE:
            # if not len(data) == 39:
            #     print(data)
            #     return
            (b_id, nonce, ciphertext, tag, distance,
             variance) = struct.unpack("<6s 16s 9s 4s H H", data)
            # BLE Mac comes across the line in reverse order. We
            # reverse it for printing; but MAC calculations are on the
            # raw value
            m_data = {}
            m_data["b_id"] = bytes(
                [b_id[i] for i in range(len(b_id) - 1, -1, -1)]).hex()
            m_data["distance"] = distance / 100
            m_data["variance"] = variance / 100
            if b_id not in BEACONS:
                BEACONS[b_id] = Beacon(b_id)
            beacon = BEACONS[b_id]
            cipher = AES.new(beacon.key, AES.MODE_EAX, nonce, mac_len=4)
            cipher.update(b_id)
            try:
                plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            except ValueError as decrypt_verify_error:
                msg['type'] = "secbeacon_auth_failure"
                msg['data'] = str(decrypt_verify_error)
                if self.callback:
                    await self.callback(msg)
                else:
                    print(msg)
                return
            (clock, dk, flags) = struct.unpack("<IIB", plaintext)
            if beacon.clock and clock <= beacon.clock:
                if beacon.clock_skew(clock) > 2:
                    # Reject old clock values
                    msg["type"] = "secbeacon_replay_failure"
                    msg["data"] = "Attempted replay of {}".format(clock)
            dk_valid = beacon.validate_dk(dk, clock)
            if dk_valid:
                beacon.mask = 0xffffffff
                msg["type"] = "secbeacon"
                m_data["clock"] = clock
                m_data["skew"] = beacon.clock_skew(clock)
                m_data["flags"] = flags
                msg["data"] = m_data
        elif packet_type == PacketType.KEEPALIVE:
            msg["type"] = "listener_keepalive"
            msg["data"] = hexlify(l_id)
        else:
            msg["type"] = "listener_error"
            msg["data"] = "Unknown Packet type: {}".format(packet_type)
        if self.callback:
            await self.callback(msg)
        else:
            print(msg)
        self.transport.write(b'ACK')

    def error_received(self, exc: Exception) -> None:
        print('Error received:', exc)

    def connection_lost(self, exc: Exception) -> None:
        print("{} has disconnected".format(self.peername))
