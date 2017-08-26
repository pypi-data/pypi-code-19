# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

urlpatterns = [
    url(r'^contact/', include('contact_form.urls', namespace='contact_form',
                              app_name='contact_form')),
]
