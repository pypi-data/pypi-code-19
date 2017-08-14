import json

version_info = (0, 0, 0)
__version__ = "0.0.0"

with open("package.json") as f:
    packageJSON = json.load(f)
    __version__ = packageJSON['version']

    version_info = tuple(__version__.split('.'))
