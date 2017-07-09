import logging
import socket
import struct
import json

__version__ = '0.0.5'

logger = logging.getLogger(__name__)
DEFAULT_SOCKET_TIMEOUT = 5.0
ZABBIX_HEADER = b'ZBXD\1'


class ZabbixInvalidHeaderError(Exception):
    def __init__(self, *args):
        self.raw_response = args[0]
        super(ZabbixInvalidHeaderError, self).__init__(
            u'Invalid header during response from server')


class ZabbixInvalidResponseError(Exception):
    def __init__(self, *args):
        self.raw_response = args[0]
        super(ZabbixInvalidResponseError, self).__init__(
            u'Invalid response from server')


def get_data_to_send(packet):
    packet_length = len(packet)
    data_header = struct.pack('q', packet_length)
    packet = packet.encode('utf-8')
    return ZABBIX_HEADER + data_header + packet


def get_raw_response(sock):
    response_data_header = sock.recv(8)
    response_data_header = response_data_header[:4]
    response_len = struct.unpack('i', response_data_header)[0]
    raw_response = sock.recv(response_len).decode('utf-8')
    return raw_response


def send(packet, server='127.0.0.1', port=10051,
         timeout=DEFAULT_SOCKET_TIMEOUT):
    socket.setdefaulttimeout(timeout)

    data_to_send = get_data_to_send(packet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server, port))
        sock.send(data_to_send)
    except Exception:
        logger.exception(u'Error talking to server')
        raise
    else:
        response_header = sock.recv(5)
        if not response_header == ZABBIX_HEADER:
            raise ZabbixInvalidHeaderError(packet)
        raw_response = get_raw_response(sock)
    finally:
        sock.close()
    return ZabbixTrapperResponse(raw_response)


class ZabbixTrapperResponse(object):
    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.data = None
        self.parse_response()

    def parse_response(self):
        try:
            self.data = self.parse_raw_response()
        except Exception:
            logger.exception('Error parsing decoded response')
            raise ZabbixInvalidResponseError(self.raw_response)

    def parse_raw_response(self):
        try:
            json_response = json.loads(self.raw_response)
            if json_response['response'] == 'failed':
                logger.warning('Fetching items failed: {0}'.format(
                    json_response))
                response = []
            else:
                response = json_response['data']
        except Exception:
            logger.exception('Error parsing raw response')
            raise ZabbixInvalidResponseError(self.raw_response)
        else:
            return response


class ItemList(object):
    def __init__(self, host):
        self.host = host

    def get(self, server, port=10051, hostMetadata=None):
        raw_packet = {
            'request': 'active checks',
            'host': self.host
        }
        if hostMetadata is not None:
            raw_packet['host_metadata'] = hostMetadata

        packet = json.dumps(raw_packet)
        return send(packet, server, port)
