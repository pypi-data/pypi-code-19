import importlib
openapi_codec = importlib.import_module('gb_openapi_codec.python-openapi-codec.openapi_codec')
# https://stackoverflow.com/a/21221452/784648
module_dict = openapi_codec.__dict__
try:
    to_import = openapi_codec.__all__
except AttributeError:
    to_import = [name for name in module_dict if not name.startswith('_')]
locals().update({name: module_dict[name] for name in to_import})

__version__ = '1.3.4'
