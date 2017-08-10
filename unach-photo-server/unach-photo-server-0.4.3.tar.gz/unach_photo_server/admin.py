# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from unach_photo_server.forms import PhotoRepositoryAdminForm
from .models import AppRegister, PhotoRepository


@admin.register(AppRegister)
class AppRegisterAdmin(admin.ModelAdmin):
    readonly_fields = ['token']
    list_display = ['name', 'description', 'token', 'domain_name', 'created_at']
    search_fields = ('name', 'domain_name')
    list_filter = ['created_at']


@admin.register(PhotoRepository)
class PhotoRepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'repo_type', 'created_at']
    search_fields = ('name', )
    form = PhotoRepositoryAdminForm