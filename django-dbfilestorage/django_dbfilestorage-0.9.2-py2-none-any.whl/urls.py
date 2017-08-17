from django.conf.urls import url
import views

urlpatterns = [
    url(r'^(?P<name>.*)$', views.show_file, name="dbstorage_file"),
]
