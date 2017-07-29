# coding: utf-8
from djotali.contacts.templatetags.contacts_extras import format_number


def before_contact_saved(sender, instance, **kwargs):
    instance.phone_number = format_number(instance.phone_number).replace(' ', '')


def after_contact_saved(sender, instance, **kwargs):
    from djotali.contacts.models import ContactsGroup
    all_contacts = ContactsGroup.objects.get(name=ContactsGroup.all_contacts)
    all_contacts.contacts.add(instance)
    all_contacts.save()
