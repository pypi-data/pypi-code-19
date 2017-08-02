# -*- coding: utf-8 -*-

try:
    from django.apps import AppConfig
except ImportError:
    pass  # Django < 1.7
else:

    class DefaultConfig(AppConfig):
        name = 'threebot_repeat'
        try:
            from . import __version__ as version_info
        except:
            version_info = 'n/a'
        verbose_name = 'threebot_repeat (' + version_info + ')'
