from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

class KongUserMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user_id = request.META.get('HTTP_X_AUTHENTICATED_USERID', None)
        source = request.META.get('HTTP_X_CONSUMER_USERNAME', None)

        if user_id:
            user = get_user_model()(id=user_id, username=user_id)
        else:
            user = AnonymousUser()

        request.user = user
        request.source = source
        print(source)
        response = self.get_response(request)
        return response
