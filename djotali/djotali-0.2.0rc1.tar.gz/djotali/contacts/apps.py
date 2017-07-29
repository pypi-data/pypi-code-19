# coding: utf-8
from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save
from django.utils.functional import cached_property

from djotali.contacts.signals import before_contact_saved, after_contact_saved


class ContactsConfig(AppConfig):
    name = 'djotali.contacts'

    def ready(self):
        pre_save.connect(before_contact_saved, sender='contacts.Contact')
        post_save.connect(after_contact_saved, sender='contacts.Contact')

    @cached_property
    def all_contacts_group_id(self):
        from djotali.contacts.models import ContactsGroup
        return ContactsGroup.objects.get(name=ContactsGroup.all_contacts).id
