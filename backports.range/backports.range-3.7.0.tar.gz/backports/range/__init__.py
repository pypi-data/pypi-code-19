"""
Backport of python3.X range class
"""
# We jump some hoops here to use the best implementation as available:
# - The fallback is ALWAYS a pure-python implementation for both range
#   and range_iterator, which are prefixed by "py"
# - If compiled via Cython, there is a Cython-only version of the iterator
from .pyrange import range

__all__ = ['range']
