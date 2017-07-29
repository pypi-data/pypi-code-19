# coding: utf-8
from django.apps import apps
from django.urls import reverse

from djotali.core.widgets import BoundModelsSelectWidget


class CampaignContactsGroupBoundModelsSelectWidget(BoundModelsSelectWidget):
    def get_url(self, value):
        all_contacts_group_id = apps.get_app_config('contacts').all_contacts_group_id
        if all_contacts_group_id == value:
            return None
        return reverse('contacts-groups:edit', args=(value,))

    def get_label(self):
        return "Editer le groupe de contacts actuel"
