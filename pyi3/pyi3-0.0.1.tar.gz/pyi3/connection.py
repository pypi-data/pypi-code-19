import json
import socket

from typing import cast, Any, Dict, List, Tuple, Union

from .command_reply import CommandReply
from .container import Container
from .output import Output
from .protocol import Event, EventReplyType, MessageType, ReplyType
from .protocol import build, decode
from .sockpath import get_socket_path
from .version import Version
from .workspace import Workspace

from .binding_event import BindingEvent
from .mode_event import ModeEvent
from .window_event import WindowEvent
from .workspace_event import WorkspaceEvent


def ipc_receive(sock) -> Tuple[Union[ReplyType, EventReplyType], str]:
    header = sock.recv(14)
    t, size = decode(header)
    payload = sock.recv(size)
    return t, payload.decode('utf-8')


EventType = Union[BindingEvent, ModeEvent, WindowEvent, WorkspaceEvent]


EVENT_TYPES = {
    EventReplyType.BINDING: BindingEvent,
    EventReplyType.MODE: ModeEvent,
    EventReplyType.WINDOW: WindowEvent,
    EventReplyType.WORKSPACE: WorkspaceEvent,
}  # type: Dict[EventReplyType, Any]


def make_event(ev_type: EventReplyType,
               data: Dict[str, Any]) -> EventType:
    return EVENT_TYPES[ev_type].from_dict(data)


class BaseConnection:
    def __init__(self, sockpath: str=None) -> None:
        self.sockpath = get_socket_path(sockpath)


class QueryConnection(BaseConnection):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(self.sockpath)

    def send(self, msg_type: MessageType, msg: str=''):
        message = build(msg_type, msg)
        self.socket.sendall(message)

    def receive(self) -> str:
        _, payload = ipc_receive(self.socket)
        return payload

    def get(self, msg_type: MessageType, msg: str='') -> Any:
        self.send(msg_type, msg)
        return json.loads(self.receive())

    def command(self, command: str):
        replies = self.get(MessageType.COMMAND, command)
        return [CommandReply.from_dict(reply) for reply in replies]

    def get_workspaces(self) -> List[Workspace]:
        wss = self.get(MessageType.GET_WORKSPACES)
        return [Workspace.from_dict(ws) for ws in wss]

    def get_outputs(self) -> List[Output]:
        outs = self.get(MessageType.GET_OUTPUTS)
        return [Output.from_dict(out) for out in outs]

    def get_tree(self) -> Container:
        return Container.from_dict(self.get(MessageType.GET_TREE))

    def get_marks(self) -> str:
        return self.get(MessageType.GET_MARKS)

    def get_bar_config(self) -> List[str]:
        return self.get(MessageType.GET_BAR_CONFIG)

    def get_version(self) -> Version:
        version = self.get(MessageType.GET_VERSION)
        return Version.from_dict(version)

    def get_binding_modes(self) -> List[str]:
        return self.get(MessageType.GET_BINDING_MODES)


class SubscriptionConnection(BaseConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sub_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sub_socket.connect(self.sockpath)

    def subscribe(self, events: List[Event]):
        events_json = json.dumps([e.value for e in events])
        message = build(MessageType.SUBSCRIBE, events_json)
        self.sub_socket.sendall(message)
        ipc_receive(self.sub_socket)

    def next_event(self) -> EventType:
        t, payload = ipc_receive(self.sub_socket)
        return make_event(cast(EventReplyType, t), json.loads(payload))


class Connection(QueryConnection, SubscriptionConnection):
    pass
