import sys
from .utils import make_get_json


def make_path(path):
    return 'statuses/{}.as'.format(path)


for name, path in (
        ('public', 'public_timeline'),
        ('home', 'home_timeline'),
        ('friends', 'friends_timeline'),
        ('user', 'user_timeline'),
        ('mentions', 'mentions'),
        ('replies', 'replies')
):
    setattr(sys.modules[__name__], name, make_get_json(name, make_path(path)))
