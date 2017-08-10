from typing import Any, Dict

from .meta import member, NamedTuple
from .rect import Rect


class Workspace(NamedTuple):
    focused = member()  # type: bool
    name = member()  # type: str
    num = member()  # type: int
    output = member()  # type: str
    rect = member()  # type: Rect
    urgent = member()  # type: bool
    visible = member()  # type: bool

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Workspace':
        d['rect'] = Rect(**d['rect'])
        return Workspace(**d)
