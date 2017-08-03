import sys
from .utils import make_get_json, make_post_json

def make_path(path):
    return 'account/{}.json'.format(path)


verify_credentials = make_get_json('verify_credentials', make_path('verify_credentials'))


for name in (
        'update_profile_image',
        'update_profile',
        'register'
):
    setattr(sys.modules[__name__], name, make_post_json(name, make_path(name)))
