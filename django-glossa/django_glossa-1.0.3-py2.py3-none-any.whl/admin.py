# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib import admin

from . import models


class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'alias', )
    # list_display_links = ('name', )
    search_fields = ('name', 'definition', )

admin.site.register(models.Term, TermAdmin)
