try:
    # Python 2
    from xmlrpclib import ServerProxy
except ImportError:
    # Python 3
    from xmlrpc.client import ServerProxy

try:
    # Python 2
    string_types = basestring
except NameError:
    # Python 3
    string_types = (str, bytes)

bstr = bytes
try:
    ustr = unicode
except NameError:
    ustr = str
