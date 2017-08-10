from typing import Any, Dict

from .meta import member, NamedTuple


class Binding(NamedTuple):
    command = member()  # type: str
    event_state_mask = member()  # type: List[str]
    input_code = member()  # type: int
    input_type = member()  # type: str
    mods = member()  # type: List[str]
    symbol = member()  # type: str

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        return Binding(**d)


class BindingEvent(NamedTuple):
    binding = member()  # type: Binding
    change = member()  # type: str

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'BindingEvent':
        d['binding'] = Binding.from_dict(d['binding'])

        return BindingEvent(**d)
