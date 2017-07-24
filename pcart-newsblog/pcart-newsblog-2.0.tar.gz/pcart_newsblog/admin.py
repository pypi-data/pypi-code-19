from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from adminsortable.admin import SortableAdmin
from parler.admin import TranslatableAdmin
from cms.admin.placeholderadmin import PlaceholderAdminMixin
from .models import Category, Article


class CategoryAdmin(SortableAdmin, TranslatableAdmin):
    list_display = ('title', 'slug', 'active', 'added')
    date_hierarchy = 'added'
    search_fields = ('title',)
    list_filter = ('active',)

admin.site.register(Category, CategoryAdmin)


class ArticleAdmin(TranslatableAdmin, PlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'tags', 'published', 'pub_date', 'changed')
    date_hierarchy = 'changed'
    search_fields = ('title',)
    list_filter = ('category', 'author')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author', 'tags'),
        }),
        (_('SEO'), {
            'fields': ('page_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        (_('Content'), {
            'fields': ('lead_in', 'lead_image'),
        }),
        (_('Publication'), {
            'fields': ('published', 'pub_date'),
        }),
    )

admin.site.register(Article, ArticleAdmin)
