"""chai_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from django.conf import settings
import importlib

urlpatterns = [
#     url(r'^admin/', admin.site.urls), # we turn off the native admin stuff
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

for app_name in settings.SERVER_APPS: # dynamically get the urls! we will enforce that the urlpatterns must exist for ALL apps
    
    try:
        module = importlib.import_module(app_name + '.urls', package=None)
        urlpatterns += module.urlpatterns
    except Exception as e:
        raise
        print('urlpatterns probably does not exist!', app_name, e)