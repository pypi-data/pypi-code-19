"""
stdlib's json and ujson compatible module
"""

try:
    from ujson import dumps as json_dumps
except ImportError:
    from json import dumps as json_dumps
try:
    from ujson import loads as json_loads
except ImportError:
    from json import loads as json_loads

__all__ = ['json_dumps', 'json_loads']
