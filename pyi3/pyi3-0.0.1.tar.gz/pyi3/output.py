from typing import Any, Dict

from .meta import NamedTuple, member
from .rect import Rect


class Output(NamedTuple):
    active = member()  # type: bool
    current_workspace = member()  # type: str
    name = member()  # type: str
    primary = member()  # type: bool
    rect = member()  # type: Rect

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Output':
        d['rect'] = Rect(**d['rect'])
        return Output(**d)
