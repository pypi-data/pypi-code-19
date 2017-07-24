from django.contrib import admin
from adminsortable.admin import SortableAdmin
from parler.admin import TranslatableAdmin
from .models import Group, Person


class GroupAdmin(SortableAdmin, TranslatableAdmin):
    list_display = ('title', 'slug', 'added')
    search_fields = ('title',)
    date_hierarchy = 'added'

admin.site.register(Group, GroupAdmin)


class PersonAdmin(SortableAdmin, TranslatableAdmin):
    list_display = ('full_name', 'role', 'active', 'changed')
    search_fields = ('full_name',)
    list_filter = ('groups', 'active')
    date_hierarchy = 'changed'

admin.site.register(Person, PersonAdmin)
