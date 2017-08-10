# -*- coding: utf-8 -*-
from django.conf.urls import url


from . import views

urlpatterns = [
    url(
        regex="^photo/$",
        view=views.get_photo_by_name,
        name='photo',
    ),
    url(
        regex="^photo/blob/$",
        view=views.get_photo_blob,
        name='blob',
    ),
	]
