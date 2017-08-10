from typing import Any, Dict

from .meta import NamedTuple, member


class Version(NamedTuple):
    major = member()  # type: int
    minor = member()  # type: int
    patch = member()  # type: int
    human_readable = member()  # type: str
    loaded_config_file_name = member()  # type: str

    @staticmethod
    def from_dict(d: Dict[Any, str]) -> 'Version':
        return Version(**d)
