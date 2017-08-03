import base64
import random
import string
import rollbar
import sys
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect


# Class for reporting custom message in rollbar
class RollbarCustomReport:
    def __init__(self, message):
        rollbar.report_message(message)


# Class for reporting occured error in rollbar
class RollbarReport:
    def __init__(self):
        rollbar.report_exc_info(sys.exc_info())


class UserStatus(object):
    """User status levels"""

    only_normal_user = 'only_normal_user'
    staff_and_below = 'staff_and_below'
    staff_and_above = 'staff_and_above'
    only_staff = 'only_staff'
    superuser = 'superuser'


# Function for generating random string
def random_number_generator(size=25, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Function for sending template email
def send_template_email(subject, message, to):
    from_email = settings.FROM_EMAIL
    send_mail(subject, message, recipient_list=to, from_email=from_email, html_message=message, fail_silently=True)


# Decorator for checking the permission of the user
def verify_permission(level=None):
    """
    :param level: Level of the user (None/only_normal_user/staff_and_above/only_staff/superuser)
    """

    def verify_permission_view(func):
        def verify(request, *args, **kwargs):

            if level == UserStatus.superuser:
                if not request.user.is_superuser:
                    return redirect('404')

            elif level == UserStatus.staff_and_below:
                if request.user.is_superuser:
                    return redirect('404')

            elif level == UserStatus.staff_and_above:
                if not request.user.is_staff:
                    return redirect('404')

            elif level == UserStatus.only_normal_user:
                if request.user.is_staff or request.user.is_superuser:
                    return redirect('404')

            elif level == UserStatus.only_staff:
                if not request.user.is_staff and request.user.is_superuser:
                    return redirect('404')

            else:
                pass

            return func(request, *args, **kwargs)

        return verify

    return verify_permission_view
