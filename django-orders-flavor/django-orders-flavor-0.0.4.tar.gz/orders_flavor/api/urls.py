from django.conf.urls import include, url


app_name = 'orders_flavor.api'

urlpatterns = [
    url(r'^(v1/)?', include(
        'orders_flavor.api.v1.urls', namespace='v1')),
]
