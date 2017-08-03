import sys
from .utils import make_get_json, make_post_json


def make_path(path):
    prefix = 'direct_messages'
    if path:
        return prefix + '/{}.json'.format(path)
    return prefix + '.json'


for name, path in (
        ('received', ''),
        ('sent', 'sent'),
):
    setattr(sys.modules[__name__], name, make_get_json(name, make_path(path)))


new = make_post_json('new', make_path('new'))
