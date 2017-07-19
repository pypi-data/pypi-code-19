import abc

from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView


from ali_base_service.util.handlers import *
from main import models


class BaseListAPI(APIView):
    __metaclass__  = abc.ABCMeta

    def get(self, request):
        self.request = request
        search_object, start, count = read_get_request_data(request.GET)
        order_by = request.GET.get('order_by')
        phone_number = request.META.get('HTTP_PHONE_NUMBER')

        return get_successful_response(self.get_query_set().list(
            serializer=self.get_serializer(),
            search_object=search_object,
            start=start,
            count=count,
            order_by=order_by,
            phone_number=phone_number
        ))

    @abc.abstractmethod
    def get_query_set(self):
        pass

    @abc.abstractmethod
    def get_serializer(self):
        pass

    # def get_client(self):
    #     return get_client(self.request)


class BaseGetAPI(APIView):
    __metaclass__ = abc.ABCMeta

    def get(self, request, id):
        phone_number = request.META.get('HTTP_PHONE_NUMBER')

        return get_successful_response(
            self.get_query_set().instance(
                instance_id=id,
                without_user_serializer=self.get_serializer(),
                phone_number=phone_number
            ))

    @abc.abstractmethod
    def get_query_set(self):
        pass

    @abc.abstractmethod
    def get_serializer(self):
        pass


def get_client(request):
    return None  # todo rename to get current user and return django user instead

