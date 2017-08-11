from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.core.mail import mail_admins

from celery import shared_task


@shared_task
def send_user_signup_email(user_id):
    user = get_user_model().objects.get(id=user_id)

    mail_admins('User Signup', 'User signup: {}'.format(user.username))
