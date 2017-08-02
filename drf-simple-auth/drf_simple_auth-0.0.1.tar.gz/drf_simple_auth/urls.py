from __future__ import absolute_import

from django.conf.urls import url

from .api import AuthLogin, AuthSignup

urlpatterns = [
    url(r'login/$', AuthLogin.as_view(), name='auth-login'),
    url(r'signup/$', AuthSignup.as_view(), name='auth-signup'),
]
