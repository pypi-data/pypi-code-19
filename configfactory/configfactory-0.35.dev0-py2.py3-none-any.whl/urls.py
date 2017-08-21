from django.conf.urls import include, url

from configfactory import views

urlpatterns = [
    url(r'^$', view=views.index, name='index'),
    url(r'^ping/$', view=views.ping, name='ping'),
    url(r'^alive/$', view=views.alive, name='alive'),
    url(r'^backup/dump/$', view=views.backup_dump, name='dump_backup'),
    url(r'^backup/load/$', view=views.backup_load, name='load_backup'),
    url(r'^backup/load/(?P<filename>.+)/$', view=views.backup_load, name='load_backup_file'),
    url(r'^backup/delete/(?P<filename>.+)/$', view=views.backup_delete, name='delete_backup'),
    url(r'^backup/serve/(?P<filename>.+)/$', view=views.backup_serve, name='serve_backup_file'),
    url(r'^logs/$', view=views.logs_index, name='logs'),
    url(r'^logs/serve/(?P<filename>.+)/$', view=views.logs_serve, name='serve_log_file'),
    url(r'^', include('configfactory.users.urls')),
    url(r'^', include('configfactory.configurations.urls')),
    url(r'^api/', include('configfactory.api.urls')),
]
