from django_api_base.api_base import JsonWrapper, StatusCode
from django_api_base.utils import RollbarReport


class APIExceptionHandler(object):
    """
    Middleware have to be defined with __init__ and __call__ method in Django 1.10 and above
    __init__ and __call__ methods are only required in django 1.10 and above.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        url = request.get_full_path()
        first_path = url.split('/')[1]
        if first_path == 'api':
            if isinstance(exception, Exception):
                dic = {"message": "Something went wrong", "error": exception.args}
                RollbarReport()
                return JsonWrapper(dic, StatusCode.HTTP_500_INTERNAL_SERVER_ERROR)
        return None

