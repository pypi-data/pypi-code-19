from django.contrib import admin
from .models import *


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    readonly_fields = [
        'sender',
        'sender_title',
        'recipient',
        'subject',
        'body',
        'delivered',
    ]

    list_display = [
        'recipient',
        'subject',
        'delivered',
        'created_at',
        'updated_at',
    ]

    search_fields = [
        'recipient'
    ]

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False