from django.contrib import admin

from .models import Feed, Item


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'uuid')
    readonly_fields = ('uuid',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'feed', 'item_type', 'published_date', 'is_published')
    list_filter = ('feed', 'item_type')
    readonly_fields = ('uuid', 'item_type')
