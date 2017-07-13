from typing import Any


class StrLengthDict(dict):
    def __init__(self, _dict: dict, **kwargs):
        super().__init__()

        self.update(_dict, **kwargs)

    def update(self, _dict: dict = None, **kwargs):
        _dict = _dict or dict()

        if len(kwargs) > 0:
            _dict.update(kwargs)

        for key, value in _dict.items():
            self[key] = value

    def __getitem__(self, item: str) -> tuple:
        if item in self:
            return super().__getitem__(item)

        raise KeyError('Item not found')

    def __setitem__(self, key: str, value: Any):
        if not isinstance(key, str):
            raise KeyError('Key must be a string')

        if key in self:
            raise KeyError('Key already exists')

        super().__setitem__(key, (len(key), value))
