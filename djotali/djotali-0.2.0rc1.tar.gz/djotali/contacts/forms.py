# coding: utf-8
import phonenumbers
from django.core.exceptions import ValidationError
from django.forms import CharField, Field
from django.utils.translation import ugettext_lazy as _
from phonenumbers.phonenumberutil import NumberParseException

from djotali.contacts.models import Contact, ContactsGroup
from djotali.contacts.widgets import ContactsWidget
from djotali.core.forms import BaseForm


class ContactForm(BaseForm):
    # Max number of characters of a senegalese telephone number including whitespaces
    phone_number = CharField(initial='+221 ', label='Téléphone', max_length=17)
    first_name = CharField(label='Prénom')
    last_name = CharField(label='Nom')

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        error_message = 'Le numéro de téléphone entré est erroné'
        try:
            if not phonenumbers.is_valid_number(phonenumbers.parse(phone_number, 'SN')):
                raise ValidationError(_(error_message), code='invalid')
        except NumberParseException:
            raise ValidationError(_(error_message), code='invalid')

        return phone_number


class ContactsGroupForm(BaseForm):
    name = CharField(label='Nom')
    contacts = Field(label='Contacts', widget=ContactsWidget)

    class Meta:
        model = ContactsGroup
        fields = ['name', 'contacts']
