from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from .models import AuthToken


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'key')
    list_filter = ('user',)
    list_select_related = ('user',)
    search_fields = ('user__username', 'device_id', 'key',)
