# coding: utf-8

from djotali.core.widgets import BoundModelsTableWidget


class ContactsWidget(BoundModelsTableWidget):
    class Media:
        js = BoundModelsTableWidget.Media.js + (
            'js/contacts-groups-edit-table.js',
        )
