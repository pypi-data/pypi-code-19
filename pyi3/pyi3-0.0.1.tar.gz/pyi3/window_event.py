from typing import Any, Dict

from .container import Container
from .meta import member, NamedTuple


class WindowEvent(NamedTuple):
    change = member()  # type: str
    container = member()  # type: Container

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'WindowEvent':
        d['container'] = Container.from_dict(d['container'])

        return WindowEvent(**d)
