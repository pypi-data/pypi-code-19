from typing import Any, Dict

from .meta import member, NamedTuple


class CommandReply(NamedTuple):
    success = member()  # type: bool

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'CommandReply':
        return CommandReply(**d)
