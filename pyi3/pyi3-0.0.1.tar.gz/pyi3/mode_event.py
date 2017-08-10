from typing import Any, Dict

from .meta import member, NamedTuple


class ModeEvent(NamedTuple):
    change = member()  # type: str
    pango_markup = member()  # type: bool

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'ModeEvent':
        return ModeEvent(**d)
