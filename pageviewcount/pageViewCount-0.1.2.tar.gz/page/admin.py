from django.contrib import admin

from page.models import ViewCount


@admin.register(ViewCount)
class ViewCountAdmin(admin.ModelAdmin):
    fields = ('url', 'client_ip', 'hits', 'created')
    list_display = ('url', 'created')
    list_filter = ('url', 'created')
