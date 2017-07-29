# coding: utf-8
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import serializers

from djotali.contacts.templatetags.contacts_extras import format_number
from djotali.core.models import TrackedModel


class Contact(TrackedModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        ordering = ["-created"]


class ContactSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField('serialize_phone_number')
    repr = serializers.SerializerMethodField('serialize_repr')

    def serialize_phone_number(self, contact):
        return format_number(contact.phone_number)

    def serialize_repr(self, contact):
        return "%s (%s)" % (contact, self.serialize_phone_number(contact))

    class Meta:
        model = Contact
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'modified', 'repr')


class UserContactsGroupsManager(models.Manager):
    def get_queryset(self):
        return super(UserContactsGroupsManager, self).get_queryset().filter(~Q(name=ContactsGroup.all_contacts))


class ContactsGroup(TrackedModel):
    all_contacts = "all.contacts"

    name = models.CharField(name='name', max_length=150, unique=True)
    contacts = models.ManyToManyField('Contact')

    user_contacts_groups = UserContactsGroupsManager()

    def __str__(self):
        return _(self.name)

    def is_all_contacts(self):
        return self.name == ContactsGroup.all_contacts


class ContactsGroupSerializer(serializers.HyperlinkedModelSerializer):
    contacts = ContactSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ContactsGroup
        fields = ('url', 'name', 'contacts', 'modified')
