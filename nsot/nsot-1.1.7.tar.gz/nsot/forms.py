"""
NSoT custom forms.
"""

from django.contrib.auth import get_user_model

from custom_user.forms import EmailUserChangeForm


class NsotUserChangeForm(EmailUserChangeForm):
    class Meta:
        model = get_user_model()
        exclude = ('password',)
