from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from rest_framework import routers
from rest_framework_extras import discover
from jmbo import api as jmbo_api

from listing import api as listing_api


admin.autodiscover()

router = routers.DefaultRouter()
discover(router)
jmbo_api.register(router)
listing_api.register(router)

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^api/(?P<version>(v1))/", include(router.urls)),
    url(r"^jmbo/", include("jmbo.urls", namespace="jmbo")),
    url(r"^listing/", include("listing.urls", namespace="listing")),
]
