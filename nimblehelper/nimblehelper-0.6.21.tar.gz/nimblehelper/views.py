from rest_framework.viewsets import GenericViewSet
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from nimblehelper.helper import NimbleHelper


class BaseView(GenericViewSet):
    @staticmethod
    def __placeholder_function(x_consumer_id, params):
        return {'status': 500, 'x_consumer_id': x_consumer_id, 'params': params}

    serializer_class = Serializer
    list_api_function = __placeholder_function
    fields = []
    required_fields = []
    create_api_function = __placeholder_function
    create_fields = []
    required_create_fields = []

    @classmethod
    def list(cls, request):
        params = NimbleHelper.check_get_parameters(request=request, fields=cls.fields,
                                                   required_fields=cls.required_fields)
        response = cls.list_api_function(x_consumer_id=params["x_consumer_id"],
                                         params=params["data"])
        return Response(response, status=response["status"])

    @classmethod
    def create(cls, request):
        params = NimbleHelper.check_post_parameters(request=request, fields=cls.fields,
                                                    required_fields=cls.required_fields)
        response = cls.create_api_function(x_consumer_id=params["x_consumer_id"],
                                           params=params["data"])
        return Response(response, status=response["status"])
