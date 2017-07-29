# coding: utf-8
from django.contrib import admin

from djotali.contacts import models


class ContactAdmin(admin.ModelAdmin):
    model = models.Contact
    fields = ['first_name', 'last_name', 'phone_number', 'is_removed']
    list_display = ('first_name', 'last_name', 'phone_number', 'is_removed')


class ContactInline(admin.StackedInline):
    model = models.ContactsGroup.contacts.through


class GroupAdmin(admin.ModelAdmin):
    model = models.ContactsGroup
    fields = ['name', 'is_removed']
    list_display = ('name', 'is_removed')
    inlines = [ContactInline]
    exclude = ('contacts',)


admin.site.register(models.ContactsGroup, GroupAdmin)
admin.site.register(models.Contact, ContactAdmin)
