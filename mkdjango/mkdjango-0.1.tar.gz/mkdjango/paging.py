from .serialize import is_query_set

__author__ = 'Michael'


class PageWrapper(object):
    DEFAULT_PAGE_SIZE = 20
    PAGE_SIZE_KEY = 'page_size'
    PAGE_NUM_KEY = 'page_num'

    def __init__(self, get_response):
        self.__get_response = get_response

    @staticmethod
    def __get_positive_int(request, name, default):
        val = request.GET.get(name)
        try:
            val = int(val)
        except ValueError:
            return default
        if val <= 0:
            return default
        return val

    def __get_page_size(self, request):
        return self.__get_positive_int(request, self.PAGE_SIZE_KEY, self.DEFAULT_PAGE_SIZE)

    def __get_page_num(self, request):
        return self.__get_positive_int(request, self.PAGE_NUM_KEY, 1)

    def __call__(self, request):
        response = self.__get_response(request)

        if request.method != 'GET':
            return response

        if self.PAGE_SIZE_KEY not in request.GET:
            return response

        page_size = self.__get_page_size(request)
        page_num = self.__get_page_num(request)

        a = page_size * (page_num - 1)
        b = page_size * page_num

        if is_query_set(response):
            response = response.all()
            size = response.count()
        else:
            size = len(response)

        if a >= size:
            return {
                "page_size": page_size,
                "page_num": page_num,
                "total_size": size,
                "has_data": False
            }

        if b > size:
            b = size

        objects = response[a:b]
        return {
            "page_size": page_size,
            "page_num": page_num,
            "total_size": size,
            "has_data": True,
            "objects": objects,
            "start_index": a,
            "end_index": b - 1,
        }
