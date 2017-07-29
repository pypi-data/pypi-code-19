# coding: utf-8

from django import forms

from djotali.campaigns.models import Campaign
from djotali.campaigns.widgets import CampaignContactsGroupBoundModelsSelectWidget
from djotali.contacts.models import ContactsGroup
from djotali.core.forms import BaseForm
from djotali.core.widgets import DateTimeFieldWidget


class CampaignForm(BaseForm):
    class Meta:
        model = Campaign
        fields = ['name', 'start_date', 'message', 'contacts_group']

    name = forms.CharField(label='Nom')
    start_date = forms.DateTimeField(label='Lancement', widget=DateTimeFieldWidget)
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'rows': 2}))
    contacts_group = forms.ModelChoiceField(label='Groupe de contacts', queryset=ContactsGroup.objects,
                                            widget=CampaignContactsGroupBoundModelsSelectWidget)
