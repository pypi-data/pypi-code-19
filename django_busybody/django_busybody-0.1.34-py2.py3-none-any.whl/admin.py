# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from . import models


@admin.register(models.History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "who", "uri", "changed_at", "target_type", "target_object_id")
    ordering = ("-changed_at", )


@admin.register(models.EmailCategory)
class EmailCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at", "updated_at")


@admin.register(models.EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "when", "to", "subject", "ok", "message_id")
    list_filter = ("ok", "bounced", "complained", "delivered", "category")
    search_fields = ('to', 'subject')
