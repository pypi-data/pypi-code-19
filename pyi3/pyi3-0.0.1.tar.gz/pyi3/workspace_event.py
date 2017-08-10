from typing import Any, Dict

from .container import Container
from .meta import member, NamedTuple


class WorkspaceEvent(NamedTuple):
    change = member()  # type: str
    current = member()  # type: Container
    old = member()  # type: Container

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'WorkspaceEvent':
        if d['change'] == 'focus':
            d['old'] = Container.from_dict(d['old'])
        d['current'] = Container.from_dict(d['current'])

        return WorkspaceEvent(**d)
