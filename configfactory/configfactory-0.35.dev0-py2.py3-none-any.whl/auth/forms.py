from django import forms
from django.core.exceptions import ValidationError

from configfactory.auth import authenticate


class LoginForm(forms.Form):

    username = forms.CharField(label='Username')

    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            self.user = authenticate(username, password)
            if self.user is None:
                raise ValidationError(
                    'Invalid username or password.'
                )
