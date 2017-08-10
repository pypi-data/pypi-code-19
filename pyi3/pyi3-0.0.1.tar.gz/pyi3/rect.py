from .meta import NamedTuple, member


class Rect(NamedTuple):
    width = member()  # type: int
    height = member()  # type: int
    x = member()  # type: int
    y = member()  # type: int
