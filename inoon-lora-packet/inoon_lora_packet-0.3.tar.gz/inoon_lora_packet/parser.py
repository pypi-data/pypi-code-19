from inoon_lora_packet.packet import (PacketHeader, PacketType,
                                      InvalidPacketError,
                                      NotSupportedPacketError)
from inoon_lora_packet.ack import AckV2Packet
from inoon_lora_packet.alive import AliveV2Packet
from inoon_lora_packet.event import EventV2Packet
from inoon_lora_packet.notice import NoticeV2Packet
from inoon_lora_packet.data_log import DataLogV2Packet


class PacketParser():
    @classmethod
    def parse(cls, raw_packet):
        if len(raw_packet) < 16:
            raise InvalidPacketError

        header = PacketHeader(raw_packet)
        raw_payload = raw_packet[16:]
        packet = None

        if header.packet.type == PacketType.alive:
            packet = AliveV2Packet(raw_payload)
        elif header.packet.type == PacketType.notice:
            packet = NoticeV2Packet(raw_payload)
        elif header.packet.type == PacketType.data_log:
            packet = DataLogV2Packet(raw_payload)
        elif header.packet.type == PacketType.event:
            packet = EventV2Packet(raw_payload)
        elif header.packet.type == PacketType.ack:
            packet = AckV2Packet(raw_payload)
        else:
            raise NotSupportedPacketError

        return header, packet
