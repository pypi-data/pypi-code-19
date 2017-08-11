from django.http import JsonResponse, HttpResponse

__author__ = 'Michael'


class AjaxErrorResponse(Exception):
    CODE = None
    MSG = None

    def __init__(self, code=None, msg=None, data=None):
        self.__code = code or self.CODE
        if not self.__code:
            raise ValueError("error code must be non-zero")

        self.__msg = msg or self.MSG
        self.__data = data

    def get_object(self):
        return {
            'code': self.__code,
            'msg': self.__msg,
            'data': self.__data
        }

    def get_response(self):
        return JsonResponse(self.get_object())


class JsonResponseWrapper(object):
    def __init__(self, get_response):
        self.__get_response = get_response

    def __call__(self, request):
        response = self.__get_response(request)

        if isinstance(response, HttpResponse):
            return response
        else:
            return JsonResponse({
                'code': 0,
                'data': response
            })

    def process_exception(self, request, e):
        if isinstance(e, AjaxErrorResponse):
            return e.get_response()
        else:
            return None
