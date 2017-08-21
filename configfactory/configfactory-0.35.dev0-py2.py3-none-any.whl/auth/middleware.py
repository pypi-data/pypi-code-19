from django.utils.functional import SimpleLazyObject

from configfactory.auth import get_user


def auth_middleware(get_response):
    """
    Authentication middleware.
    """
    def middleware(request):
        request.user = SimpleLazyObject(lambda: get_user(request))
        response = get_response(request)
        return response
    return middleware
