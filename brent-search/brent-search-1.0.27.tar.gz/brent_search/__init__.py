from ._test import test
from .bracket import bracket
from .brent import brent
from .optimize import minimize

__name__ = "brent-search"
__version__ = "1.0.27"
__author__ = "Danilo Horta"
__author_email__ = "horta@ebi.ac.uk"

__all__ = [
    "__name__", "__version__", "__author__", "__author_email__", "test",
    "bracket", "brent", "minimize"
]
