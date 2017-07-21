from django.http.request import HttpRequest
from django.utils.http import urlsafe_base64_decode
from rinzler.exceptions.auth_exception import AuthException
from onyxerp.core.services.app_service import AppService
import jwt
import base64
import json


class JwtService(object):

    app_service = object
    __jwt_alg = "HS256"
    __cleared_routes = dict()
    __config = dict()

    def __init__(self, config: dict()):
        self.__config = config
        self.app_service = AppService(config)
        self.__cleared_routes = config["JWT_ROUTES_WHITE_LIST"]

    def authenticate(self, request: HttpRequest, auth_route: str(), params: dict()):
        if auth_route not in self.__cleared_routes:

            token = self.get_authorization_jwt(request)
            data = self.check_jwt(token, auth_route)

            return {
                "token": token,
                "data": data,
            }
        else:
            return dict()

    def get_authorization_jwt(self, request: HttpRequest):

        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthException("JWT não informado.")

        token = request.META['HTTP_AUTHORIZATION']
        if 'Bearer ' not in token:
            raise AuthException("JWT não informado.")
        return token[7:]

    def decode(self, token, key):
        try:
            return jwt.decode(token, key)
        except BaseException as e:
            raise AuthException("Token inválido ou expirado.")

    def get_jwt_payload(self, token):
        exp = token.split(".")
        payload = urlsafe_base64_decode(exp[1])
        return json.loads(payload.decode("utf-8"))

    def check_jwt(self, token: str(), auth_route: str()):
        try:
            exp = token.split(".")
            payload = urlsafe_base64_decode(exp[1])
            json_data = json.loads(payload.decode("utf-8"))

            app_key = base64.encodebytes(json_data['data']['app']['apikey'].encode("utf-8"))

            app_data = self.app_service.get_app(app_key.decode("utf-8"))
            key = base64.b64encode(app_data['data']['apiSecret'].encode("utf-8"))
            return self.decode(token, key)
        except Exception as e:
            raise AuthException("Token inválido ou expirado.")
