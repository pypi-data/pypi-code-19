from ._version import get_versions
from .scout import Scout

__version__ = get_versions()['version']
del get_versions
