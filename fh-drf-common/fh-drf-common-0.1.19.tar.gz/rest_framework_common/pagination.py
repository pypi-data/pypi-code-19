from rest_framework.pagination import PageNumberPagination


class LargePageNumberPagination(PageNumberPagination):
    page_size = 100


class FlexPageSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
