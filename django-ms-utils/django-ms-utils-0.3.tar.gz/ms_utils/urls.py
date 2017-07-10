from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    url(r'jsi18n$', JavaScriptCatalog.as_view(), name='ms-jsi18n'),
]
