import sys
from .utils import make_get_json

for name, path in (
        ('friends', 'statuses/friends.json'),
        ('followers', 'statuses/followers.json'),
        ('show', 'users/show.json'),
        ('friends_ids', 'friends/ids.json'),
        ('followers_ids', 'followers/ids.json')
):
    setattr(sys.modules[__name__], name, make_get_json(name, path))
