import coreapi
import coreschema
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_api_actions.views import ActionReadMixin


class UsersAPIView(APIView):
    """
    获得用户列表

    返回值：用户列表 `['a', 'b', ...]`

    """

    def get(self, request):
        return Response(['a', 'b'])


class UsersActionReadAPIView(ActionReadMixin, APIView):
    """
    获得用户列表, 用了`ActionReadMixin`后这是一个用 Read

    返回值：用户列表 `['a', 'b', ...]`

    """

    def get(self, request):
        return Response(['a', 'b'])


class UsersExtraFieldsAPIView(APIView):
    """
    获得用户列表, 带user_id/user_name会过滤

    返回值：
        - 带user_id: `['a']`
        - 不带user_id: `['a','b']`
    """

    extra_fields = [
        coreapi.Field(name='user_father', location='query', required=True,
                      schema=coreschema.String(description='用户的爹')),
        coreapi.Field(name='user_id', location='query', required=False,
                      schema=coreschema.Integer(description='用户id')),
        coreapi.Field(name='user_name', location='query', required=False,
                      schema=coreschema.String(description='用户名字'))
    ]

    def get(self, request):
        user_id = request.GET.get('user_id', '')
        if user_id:
            return Response(['a'])
        else:
            return Response(['a', 'b'])
