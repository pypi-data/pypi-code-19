from django.conf.urls import include, url
from mmogo.website import views


urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^contacts/$', views.contact_us, name="contact_us"),
    url(r'^about/$', views.about_us, name="about_us"),
]
