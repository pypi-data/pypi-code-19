import sys

from .utils import make_get_json, make_post_json


def make_path(path):
    return 'friendships/{}.json'.format(path)


for name in ('exists', 'show') :
    setattr(sys.modules[__name__], name, make_get_json(name, make_path(name)))

for name in ('create', 'destroy'):
    setattr(sys.modules[__name__], name, make_post_json(name, make_path(name)))
