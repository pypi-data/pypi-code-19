# -*- coding: utf-8 -*-

__author__ = 'Brian Lee'

from HexByteConversion import HexToByte

# Constants
UF_PACKET_START_CODE = 0x40
UF_NETWORK_PACKET_START_CODE = 0x41
UF_PACKET_END_CODE = 0x0a
UF_PACKET_LEN = 13
UF_NETWORK_PACKET_LEN = 15
UF_PACKET_COMMAND = 0
UF_PACKET_TERMINAL_ID = 1
UF_PACKET_PARAM = 2
UF_PACKET_SIZE = 3
UF_PACKET_FLAG = 4
UF_PACKET_CHECKSUM = 5

# Byte position of packet components
UF_PACKET_START_CODE_POS = 0
UF_PACKET_COMMAND_POS = 1
UF_PACKET_PARAM_POS = 2
UF_PACKET_SIZE_POS = 6
UF_PACKET_FLAG_POS = 10
UF_PACKET_CHECKSUM_POS = 11
UF_PACKET_END_CODE_POS = 12

UF_NETWORK_PACKET_START_CODE_POS = 0
UF_NETWORK_PACKET_TERMINALID_POS = 1
UF_NETWORK_PACKET_COMMAND_POS = 3
UF_NETWORK_PACKET_PARAM_POS = 4
UF_NETWORK_PACKET_SIZE_POS = 8
UF_NETWORK_PACKET_FLAG_POS = 12
UF_NETWORK_PACKET_CHECKSUM_POS = 13
UF_NETWORK_PACKET_END_CODE_POS = 14

# Data packet
UF_DEFAULT_DATA_PACKET_SIZE = 4 * 1024


def unsigned32(n):
    return n & 0xFFFFFFFF


def validate_checksum(recv_data, network_mode):
    chksum = 0
    length = 0

    if len(recv_data) < 13:
        return False

    if network_mode == 1:
        length = 15 - 2
    else:
        length = 13 - 2

    for i in range(length):
        chksum = chksum + recv_data[i]

    chksum = chksum & 0xFF

    if recv_data[length] != chksum:
        return False
    else:
        return True

def calculate_checksum(packet, size):
    checksum = 0
    for i in range(size):
        checksum += packet[i]
    return checksum

def make_packet(command, param=0, size=0, flag=0):

    packet = [0 for _ in range(UF_PACKET_LEN)]

    packet[UF_PACKET_START_CODE_POS] = UF_PACKET_START_CODE;
    packet[UF_PACKET_COMMAND_POS] = command;
    packet[UF_PACKET_PARAM_POS] = param & 0xFF;
    packet[UF_PACKET_PARAM_POS + 1] = (param >> 8) & 0xF;
    packet[UF_PACKET_PARAM_POS + 2] = (param >> 16) & 0xF;
    packet[UF_PACKET_PARAM_POS + 3] = (param >> 24) & 0xF;
    packet[UF_PACKET_SIZE_POS] = size;
    packet[UF_PACKET_SIZE_POS + 1] = (size >> 8) & 0xF;
    packet[UF_PACKET_SIZE_POS + 2] = (size >> 16) & 0xF;
    packet[UF_PACKET_SIZE_POS + 3] = (size >> 24) & 0xF;
    packet[UF_PACKET_FLAG_POS] = flag;
    packet[UF_PACKET_CHECKSUM_POS] = calculate_checksum(packet, UF_PACKET_CHECKSUM_POS)
    packet[UF_PACKET_END_CODE_POS] = UF_PACKET_END_CODE;

    str_packet = ''
    for x in packet:
        str_packet = str_packet + hex(int(x))[2:].zfill(2)

    return HexToByte(str_packet)


def make_network_packet(command, terminal_id, param=0, size=0, flag=0):
    packet = [0 for _ in range(UF_NETWORK_PACKET_LEN)]

    packet[UF_NETWORK_PACKET_START_CODE_POS] = UF_NETWORK_PACKET_START_CODE
    packet[UF_NETWORK_PACKET_TERMINALID_POS] = terminal_id & 0xFF
    packet[UF_NETWORK_PACKET_TERMINALID_POS + 1] = (terminal_id >> 8) & 0xFF
    packet[UF_NETWORK_PACKET_COMMAND_POS] = command
    packet[UF_NETWORK_PACKET_PARAM_POS] = param & 0xFF
    packet[UF_NETWORK_PACKET_PARAM_POS + 1] = (param >> 8) & 0xF
    packet[UF_NETWORK_PACKET_PARAM_POS + 2] = (param >> 16) & 0xF
    packet[UF_NETWORK_PACKET_PARAM_POS + 3] = (param >> 24) & 0xF
    packet[UF_NETWORK_PACKET_SIZE_POS] = size
    packet[UF_NETWORK_PACKET_SIZE_POS + 1] = (size >> 8) & 0xF
    packet[UF_NETWORK_PACKET_SIZE_POS + 2] = (size >> 16) & 0xF
    packet[UF_NETWORK_PACKET_SIZE_POS + 3] = (size >> 24) & 0xF
    packet[UF_NETWORK_PACKET_FLAG_POS] = flag
    packet[UF_NETWORK_PACKET_CHECKSUM_POS] = calculate_checksum(packet, UF_PACKET_CHECKSUM_POS)
    packet[UF_NETWORK_PACKET_END_CODE_POS] = UF_PACKET_END_CODE

    str_packet = ''
    for x in packet:
        str_packet = str_packet + hex(int(x))[2:].zfill(2)

    return HexToByte(str_packet)


def parse_packet(recvData):
    if len(recvData) == 0:
        return [0, 0, 0, 0, 0, 0, 0]

    if not validate_checksum(recvData):
        return [0, 0, 0, 0, 0, 0, 0]

    startcode = recvData[0]
    command = recvData[1]
    param = (recvData[2] << 0) | (recvData[3] << 8) | (recvData[4] << 16) | (recvData[5] << 24)
    size = (recvData[6] << 0) | (recvData[7] << 8) | (recvData[8] << 16) | (recvData[9] << 24)
    flag = recvData[10]
    checksum = recvData[11]
    endcode = recvData[12]

    return [startcode, command, param, size, flag, checksum, endcode]


def parse_network_packet(recvData):
    if not validate_checksum(recvData):
        return []

    startcode = recvData[0]
    moduleID = recvData[1]
    command = recvData[3]
    param = (recvData[4] << 0) | (recvData[5] << 8) | (recvData[6] << 16) | (recvData[7] << 24)
    size = (recvData[8] << 0) | (recvData[9] << 8) | (recvData[10] << 16) | (recvData[11] << 24)
    flag = recvData[12]
    checksum = recvData[13]
    endcode = recvData[14]

    return [startcode, command, param, size, flag, checksum, endcode]


def make_four_byte_checksum(data_packet):
    checksum = 0
    for x in data_packet:
        checksum = checksum + x

    return checksum & 0xFFFFFFFF






# unit test
if __name__ == '__main__':
    print make_packet(0x41, 0x12345678, 0x87654321, 1)
    print make_network_packet(0x41, 0x01, 0x12345678, 0x87654321, 1)

    a = [64, 3, 137, 0, 0, 0, 0, 3, 3, 22, 97, 73, 10]

    for x in parse_packet(a):
        print hex(x)[2:].zfill(2)
