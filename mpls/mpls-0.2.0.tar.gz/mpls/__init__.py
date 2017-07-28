from .version import __version__
from .cache import clear_cache
from .config import configure, load_config
from .mpls import collect, get, use, temp

__all__ = [
    "clear_cache",
    "configure", "load_config",
    "collect", "get", "use", "temp"
]
