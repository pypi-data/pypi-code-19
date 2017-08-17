# -*- coding:utf-8 -*-
import logging
from django.conf import settings
from rest_framework import permissions
from rest_framework import exceptions
from .utils import get_keyword

logger = logging.getLogger(__name__)

ALLOW_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD')
SAFE_METHODS = ('GET', 'HEAD', )


class DevicePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if settings.DEBUG or (request.user and request.user.is_superuser):
            return True
        if request.user and (request.user.is_staff and request.user.is_active):
            return True
        device_id = request.GET.get('device_id', None)
        device_id = device_id if device_id else request.POST.get('device_id', None)
        dev = Device.objects.filter(device_id=device_id).first()
        if dev and dev.token and dev.user and dev.user.is_active:
            return True
        else:
            return False


class TokenPermission(permissions.BasePermission):
    keyword = 'token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def has_permission(self, request, view):
        key = get_keyword(request, self.keyword)
        logger.debug("[permissions] token:%s", key)

        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            return False

        if not token.user.is_active:
            return False
        return True


class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        owner = getattr(obj, "owner", None)
        if owner:
            return obj.owner == request.user
        return super(IsOwner, self).has_object_permission(request, view, obj)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        """针对每一次请求的权限检查"""
        if request.method in SAFE_METHODS:
            return True

    def has_object_permission(self, request, view, obj):
        """针对数据库条目的权限检查，返回 True 表示允许"""

        # 允许访问只读方法
        if request.method in SAFE_METHODS:
            return True

        # 非安全方法需要检查用户是否是 owner
        owner = getattr(obj, "owner", None)
        if owner:
            return obj.owner == request.user
        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)