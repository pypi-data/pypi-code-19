from __future__ import absolute_import, unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from .notify import send_user_signup_email


@receiver(post_save, sender=get_user_model())
def notify_user_signup(sender, instance=None, created=False, **kwargs):
    if getattr(settings, 'DISABLE_SIGNUP_NOTIFY', False):
        return

    if not created:
        return

    # On signup
    send_user_signup_email.delay(instance.id)
