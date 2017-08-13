# method to get user from middleware
def get_current_user():
    from django.conf import settings
    from teamroles.middleware.usermiddleware import _tls
    get_user_fn = getattr(settings, 'GET_CURRENT_USER', None)

    if get_user_fn:
        return get_user_fn()

    return getattr(_tls, 'user', None)

