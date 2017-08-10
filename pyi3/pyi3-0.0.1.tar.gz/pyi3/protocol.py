from enum import Enum
from struct import pack, unpack

from typing import Tuple, Union

MAGIC = b'i3-ipc'


class MessageType(Enum):
    COMMAND = 0
    GET_WORKSPACES = 1
    SUBSCRIBE = 2
    GET_OUTPUTS = 3
    GET_TREE = 4
    GET_MARKS = 5
    GET_BAR_CONFIG = 6
    GET_VERSION = 7
    GET_BINDING_MODES = 8


class ReplyType(Enum):
    COMMAND = 0
    WORKSPACES = 1
    SUBSCRIBE = 2
    OUTPUTS = 3
    TREE = 4
    MARKS = 5
    BAR_CONFIG = 6
    VERSION = 7
    BINDING_MODES = 8


class Event(Enum):
    WORKSPACE = 'workspace'
    OUTPUT = 'output'
    MODE = 'mode'
    WINDOW = 'window'
    BARCONFIG_UPDATE = 'barconfig_update'
    BINDING = 'binding'


class EventReplyType(Enum):
    WORKSPACE = 0
    OUTPUT = 1
    MODE = 2
    WINDOW = 3
    BARCONFIG_UPDATE = 4
    BINDING = 5


class I3ProtocolError(Exception):
    pass


def build(msg_type: MessageType, payload: str) -> bytes:
    payload_bytes = payload.encode('utf8')
    metadata = pack('=II', len(payload_bytes), msg_type.value)
    return b''.join((MAGIC, metadata, payload_bytes))


def decode(header: bytes) -> Tuple[Union[EventReplyType, ReplyType], int]:
    magic, size, reply_type_code = unpack('=6sII', header)

    is_event = bool(reply_type_code & 0x80000000)
    reply_type_code &= 0x7FFFFFFF

    if magic != MAGIC:
        raise I3ProtocolError("Incorrect reply.")

    if is_event:
        return EventReplyType(reply_type_code), size
    else:
        return ReplyType(reply_type_code), size
