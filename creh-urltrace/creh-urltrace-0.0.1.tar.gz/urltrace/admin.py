from django.contrib import admin
from models import UrlTrace


class UrlAdmin(admin.ModelAdmin):
    list_filter = ['is_active','url_trace_group']
    list_display = ['url_trace', 'url_trace_group', 'is_active','description','description']
    search_fields = ('url_trace', 'url_trace_group','description',)


admin.site.register(UrlTrace,UrlAdmin)