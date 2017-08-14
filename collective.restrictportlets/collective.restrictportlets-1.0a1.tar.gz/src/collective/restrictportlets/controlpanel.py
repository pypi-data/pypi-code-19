# -*- coding: utf-8 -*-
from collective.restrictportlets import _
from collective.restrictportlets.interfaces import ISettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import form


class ControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ISettings


ControlPanelView = layout.wrap_form(ControlPanelForm, ControlPanelFormWrapper)
ControlPanelView.label = _(u'Restrict portlets')
