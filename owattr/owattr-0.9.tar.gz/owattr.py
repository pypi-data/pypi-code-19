from typing import (
    Callable,
    Dict,
)

__all__ = ['from_dict']
__author__ = "Motoki Naruse"
__copyright__ = "Motoki Naruse"
__credits__ = ["Motoki Naruse"]
__email__ = "motoki@naru.se"
__license__ = "MIT"
__maintainer__ = "Motoki Naruse"
__version__ = "0.9"


def from_dict(target_object: object, new_attrs: Dict[str, str]) -> None:
    if hasattr(target_object, '__all__'):
        # mypy says object doesn't have __all__, but module is sub type of
        # object.
        keys = target_object.__all__  # type: ignore
    else:
        keys = (key for key in dir(target_object) if not key.startswith('_'))

    for key in keys:
        if key not in new_attrs:
            continue

        original_attr = getattr(target_object, key)
        if isinstance(original_attr, Callable):  # type: ignore
            continue

        Type = type(original_attr)
        setattr(target_object, key, Type(new_attrs[key]))
