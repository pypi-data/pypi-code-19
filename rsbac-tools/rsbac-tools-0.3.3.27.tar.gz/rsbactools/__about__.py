import os

__all__ = [
    "__title__", "__summary__", "__uri__", "__version__", "__commit__",
    "__author__", "__email__", "__license__", "__copyright__",
]


try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_dir = None


__title__ = "rsbac-tools"
__summary__ = "Command-line tools for daily tasks on a RSBAC System"
__uri__ = "https://bitbucket.org/igraltist/rsbac-tools"

__version__ = "15.0.dev0"

__author__ = "Jens Kasten"
__email__ = "info@kasten-edv.de"

__license__ = "GNU GPLv3"
