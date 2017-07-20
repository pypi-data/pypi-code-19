from django.conf import settings
from django.contrib import admin
from .models import EmailTemplate, Logs, SysProcess


class LogsAdmin(admin.ModelAdmin):
    list_display = ('log_name', '_log_level', '_log_msg', 'created_at')
    fields = ('log_name', 'log_level', 'log_msg')
    list_filter = ['created_at', 'log_level']
    search_fields = ['log_name', 'log_level', 'log_msg']

    def __init__(self, *args, **kwargs):
        super(LogsAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', '_message')


class SysProcessAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'content_type', 'priority', 'status', 'created_at')
    fields = ('content_id', 'content_type', 'priority', 'status',)
    list_filter = ['priority', 'content_id', 'content_type']
    search_fields = ['content_id', 'content_type', 'priority', 'status', ]

    def __init__(self, *args, **kwargs):
        super(SysProcessAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False


admin.site.site_header = settings.CNM_CONFIGS['site_name']
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Logs, LogsAdmin)
admin.site.register(SysProcess, SysProcessAdmin)
