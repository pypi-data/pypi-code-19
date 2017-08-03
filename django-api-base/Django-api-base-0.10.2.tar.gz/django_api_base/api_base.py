from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from .models import AccessToken, UserProfile, RefreshToken, DeviceID
from django.utils import timezone
import json
import logging
import importlib
logger = logging.getLogger('django')

UserProfileModel = getattr(settings, 'USER_PROFILE_MODEL_PATH', UserProfile)
if isinstance(UserProfileModel, str):
    path_split_list = UserProfileModel.split('.')
    if len(path_split_list) > 2:
        try:
            module_path = ".".join(path_split_list[:-1])
            model_class_name = path_split_list[-1]
            imported_module = importlib.import_module(module_path)
            UserProfileModel = getattr(imported_module, model_class_name)
            if not issubclass(UserProfileModel, UserProfile):
                UserProfileModel = UserProfile
                logger.info("Provide model class is not a subclass of 'UserProfile', Loading base model")

        except ImportError:
            logger.info("Invalid USER_PROFILE_MODEL_PATH value, Loading default 'UserProfile' model.")
            UserProfileModel = UserProfile

        except AttributeError:
            logger.info("Invalid USER_PROFILE_MODEL_PATH value, Loading default 'UserProfile' model.")
            UserProfileModel = UserProfile
    else:
        logger.info("Invalid USER_PROFILE_MODEL_PATH value, Loading default 'UserProfile' model.")
        UserProfileModel = UserProfile


class StatusCode(View):
    # Success Codes
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_203_NON_AUTHORITATIVE = 203
    HTTP_204_NO_CONTENT = 204
    HTTP_205_RESET_CONTENT = 205
    HTTP_206_PARTIAL_CONTENT = 206

    # Client Error Codes
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_402_PAYMENT_REQUIRED = 402
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_406_NOT_ACCEPTABLE = 406
    HTTP_408_REQUEST_TIMEOUT = 408
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_426_FORCE_UPDATE = 426

    # Server Error Codes
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504


# REST Api parent class. This class is extended to perform the common functionality of a REST api
class ApiView(View):
    flag = StatusCode.HTTP_403_FORBIDDEN
    NULL_VALUE_VALIDATE = [None, '', ' ']

    def get(self, request, *args, **kwargs):
        dic = {'message': "GET Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        dic = {'message': "POST Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, *args, **kwargs):
        dic = {'message': "PUT Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        dic = {'message': "DELETE Method is not allowed"}
        return JsonWrapper(dic, StatusCode.HTTP_405_METHOD_NOT_ALLOWED)


# This class is for wrapping the json response
class JsonWrapper(JsonResponse):
    def __init__(self, data, flag):
        wrapper_dic = {
            'status': flag,
            'data': data
        }
        super(JsonWrapper, self).__init__(wrapper_dic, status=flag, json_dumps_params={"indent": 4})


# Decorator for getting data from raw body data
def get_raw_data(func):
    def get_data(request, *args, **kwargs):
        json_data = request.body

        try:
            request.DATA = json.loads(json_data.decode('utf-8'))

        except Exception as e:
            dic = {'message': "Please provide json data and GET Method is not allowed", "error": e.args}
            flag = StatusCode.HTTP_400_BAD_REQUEST
            return JsonWrapper(dic, flag)

        return func(request, *args, **kwargs)

    return get_data


# Decorator for getting the access token
def verify_access_token(func):
    def verify(request, *args, **kwargs):
        flag = StatusCode.HTTP_400_BAD_REQUEST
        access_token = request.META.get('HTTP_ACCESS_TOKEN')
        if access_token is not None:
            try:
                access_token = AccessToken.objects.get(token=access_token, expires__gte=timezone.now().date())
                request.user_profile = UserProfileModel.objects.get(user=access_token.user)

            except AccessToken.DoesNotExist:
                dic = {"message": "SESSION EXPIRED"}
                flag = StatusCode.HTTP_401_UNAUTHORIZED
                return JsonWrapper(dic, flag)

            except UserProfileModel.DoesNotExist:
                pass

        else:
            dic = {"message": "PLEASE PROVIDE AN ACCESS TOKEN"}
            return JsonWrapper(dic, flag)

        return func(request, *args, **kwargs)

    return verify


class AccessTokenManagement(object):

    @staticmethod
    def initialise_access_token(device_id, user):
        """Method for initialising access token, refresh token and device id data for user"""
        try:
            device = DeviceID.objects.get(device_id=device_id)
            if device.user == user:
                try:
                    refresh_token = RefreshToken.objects.get(device_id=device, user=user, expire_count__gte=1)

                except RefreshToken.DoesNotExist:
                    refresh_token = RefreshToken.objects.create(user=user, device_id=device)

                access_tokens = AccessToken.objects.filter(user=user, expires__gt=timezone.now().date()).order_by('-id')

                if access_tokens:
                    access_token = access_tokens[0]
                else:
                    access_token = AccessToken.objects.create(user=user)
                    refresh_token.expire_count -= 1
                    if refresh_token.expire_count == 0:
                        refresh_token.delete()
                        device = DeviceID.objects.get(device_id=device_id)
                        refresh_token = RefreshToken.objects.create(device_id=device, user=device.user)
                    else:
                        refresh_token.save()

            else:
                device.delete()
                device = DeviceID.objects.create(device_id=device_id, user=user)
                refresh_token = RefreshToken.objects.create(user=user, device_id=device)
                access_token = AccessToken.objects.create(user=user)

        except DeviceID.DoesNotExist:
            device = DeviceID.objects.create(device_id=device_id, user=user)
            refresh_token = RefreshToken.objects.create(user=user, device_id=device)
            access_token = AccessToken.objects.create(user=user)

        return access_token, refresh_token

    @staticmethod
    def refresh_access_token(device_id, refresh_token):
        """
        This method is for refreshing access tokens when they expire. Multiple access tokens will be valid for a user
        """
        try:
            refresh_token = RefreshToken.objects.get(
                token=refresh_token, device_id__device_id=device_id, expire_count__gt=0)
            access_token = AccessToken.objects.create(user=refresh_token.user)
            refresh_token.expire_count -= 1
            if refresh_token.expire_count == 0:
                refresh_token.delete()
                device = DeviceID.objects.get(device_id=device_id)
                refresh_token = RefreshToken.objects.create(device_id=device, user=device.user)
            else:
                refresh_token.save()

            now_date = timezone.now().date()
            if AccessToken.objects.filter(expires__lt=now_date).exists():
                AccessToken.objects.filter(expires__lt=now_date).delete()

        except RefreshToken.DoesNotExist:
            return None, "Invalid Refresh Token"

        return access_token, refresh_token

    @staticmethod
    def refresh_access_token_single(device_id, refresh_token):
        """
        This method is for refreshing access tokens when they expire. Only single access token will be valid for a user
        """
        try:
            refresh_token = RefreshToken.objects.get(
                token=refresh_token, device_id__device_id=device_id, expire_count__gt=0)
            AccessToken.objects.filter(user=refresh_token.user).delete()
            access_token = AccessToken.objects.create(user=refresh_token.user)
            refresh_token.expire_count -= 1
            if refresh_token.expire_count == 0:
                refresh_token.delete()
                device = DeviceID.objects.get(device_id=device_id)
                refresh_token = RefreshToken.objects.create(device_id=device, user=device.user)
            else:
                refresh_token.save()

            now_date = timezone.now().date()
            if AccessToken.objects.filter(expires__lt=now_date).exists():
                AccessToken.objects.filter(expires__lt=now_date).delete()

        except RefreshToken.DoesNotExist:
            return None, "Invalid Refresh Token"

        return access_token, refresh_token

    @staticmethod
    def delete_access_token_permission(user):
        """Method for deleting all the access tokens and refresh tokens of a user"""

        DeviceID.objects.filter(user=user).delete()
        AccessToken.objects.filter(user=user).delete()
