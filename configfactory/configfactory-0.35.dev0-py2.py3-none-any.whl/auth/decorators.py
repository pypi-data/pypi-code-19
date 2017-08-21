from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from configfactory.auth import get_user


def login_required():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            user = get_user(request)
            if not user.is_authenticated:
                return redirect(to=reverse('login'))
            return func(request, *args, **kwargs)
        return inner
    return decorator


def admin_required():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            user = get_user(request)
            if not user.is_authenticated:
                return redirect(to=reverse('login'))
            if not user.is_admin:
                raise PermissionDenied
            return func(request, *args, **kwargs)
        return inner
    return decorator
