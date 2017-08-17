# -*- encoding:utf-8 -*-
from .add_ons import get_addons
from django.conf import settings
from . import settings as local_settings


def get_settings(conf_name):
    if hasattr(settings, conf_name):
        return {conf_name: getattr(settings, conf_name)}
    if hasattr(local_settings, conf_name):
        return {conf_name: getattr(local_settings, conf_name)}
    return {}


def context(request):
    app_context = {'addons': get_addons().values()}
    app_context.update(get_settings('APP_NAME'))
    app_context.update(get_settings('AUTHOR'))
    app_context.update(get_settings('CAN_SIGNUP'))
    app_context.update(get_settings('CAN_RESET_PASSWORD'))
    app_context.update({'SIDEBAR_COLLAPSED': request.session.get('sidebar_collapsed', 'false')})
    return app_context
