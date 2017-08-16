from ._test import test
from ._version import Version as _Version
from .bracket import bracket
from .brent import brent
from .optimize import minimize

_Version(__name__)

__all__ = [
    "__version__", "version_info", "test", "bracket", "brent", "minimize"
]
