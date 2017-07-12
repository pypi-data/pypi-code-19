from typing import Any


class StrLengthDict(dict):
    def __getattr__(self, item: str) -> tuple:
        if item in self:
            return self[item]

        raise KeyError('Item not found')

    def __setattr__(self, key: str, value: Any):
        if not isinstance(key, str):
            raise KeyError('Key must be a string')

        if key in self:
            raise KeyError('Key already exists')

        self[key] = len(key), value
