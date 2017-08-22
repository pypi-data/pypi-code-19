from django.conf.urls import include, url

from listing.views import ListingDetail


urlpatterns = [
    url(
        r"^(?P<slug>[\w-]+)/$",
        ListingDetail.as_view(),
        name="listing-detail"
    ),
]
