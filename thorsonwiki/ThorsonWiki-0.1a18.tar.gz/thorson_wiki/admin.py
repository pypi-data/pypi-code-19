from django import forms
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext as _
from thorson_wiki.models import *

font_family = "Menlo, Monaco, Consolars, \"Courier New\", monospace"

class ArticleAdmin(admin.ModelAdmin):
    """
    Represents the Article model on the admin site.
    """

    # The fields to be displayed
    list_display = ('title', 'namespace', 'public')
    list_filter = ('namespace', 'public')

    fieldsets = (
        (None, {'fields': ('title', 'content')}),
        (_("Meta"), {'fields': ('namespace', 'public', 'redirect')})
    )

    search_fields = ('title', 'content')
    ordering = ('title', 'namespace', 'public')
    filter_horizontal = ()

    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea({
                'style': "font-family: %s;" % font_family,
                'class': 'vLargeTextField',
                'rows': '10',
                'cols': '40',
            }),
        },
    }

admin.site.register(Article, ArticleAdmin)
