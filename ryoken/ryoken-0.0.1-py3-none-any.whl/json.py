from typing import Any
from .exceptions import UnexpectedJsonData, JsonDecodeError

try:
    from ujson import loads, dumps, load, dump
except ImportError:
    from json import loads, dumps, load, dump
finally:
    json_load = load
    json_dump = dump
    json_loads = loads
    json_dumps = dumps


class JSON:
    @staticmethod
    async def decode(data: str) -> Any:
        if not isinstance(data, str):
            raise UnexpectedJsonData

        try:
            decoded_data = json_loads(data)
        except ValueError:
            raise JsonDecodeError

        return decoded_data

    @staticmethod
    async def encode(data: Any, pretty: bool = False) -> str:
        return json_dumps(data, indent=4) if pretty else json_dumps(data)
