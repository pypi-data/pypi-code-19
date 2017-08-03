import sys
from .utils import make_post_json

def make_path(path):
    return 'blocks/{}.json'.format(path)


for name in ('create', 'destroy'):
    setattr(sys.modules[__name__], name, make_post_json(name, make_path(name)))
