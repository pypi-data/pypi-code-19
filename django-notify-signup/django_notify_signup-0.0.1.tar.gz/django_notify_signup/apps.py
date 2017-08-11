from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class NotifySignupConfig(AppConfig):
    name = 'django_notify_signup'
    verbose_name = 'Django Notify Signup'

    def ready(self):
        from . import signals  # noqa
