from django.contrib import admin
from models import UrlTrace,UrlTraceGroup


class UrlTraceAdmin(admin.ModelAdmin):
    list_filter = ['is_active','url_trace_group']
    list_display = ['url_trace', 'url_trace_group', 'is_active','description','description']
    search_fields = ('url_trace', 'url_trace_group','description',)

class UrlTraceGroupAdmin(admin.ModelAdmin):
    list_filter = ['is_active']
    list_display = ['group_name', 'is_active','description','description']
    search_fields = ('group_name', 'description',)

admin.site.register(UrlTrace,UrlTraceAdmin)
admin.site.register(UrlTraceGroup, UrlTraceGroupAdmin)