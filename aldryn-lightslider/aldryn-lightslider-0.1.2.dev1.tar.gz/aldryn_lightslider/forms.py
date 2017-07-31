import django.forms
from . import models
from django.utils.translation import ugettext_lazy as _


class LightsliderPluginForm(django.forms.ModelForm):

    class Meta:
        fields = [
            'number_of_concurrent_slides',
            'number_of_paginating_slides',
            'style',
            'transition_style',
            'transition_effect',
            'ride',
            'interval',
        ]
        model = models.LightsliderPlugin

    def clean_style(self):
        style = self.cleaned_data.get('style')
        template = 'aldryn_lightslider/plugins/lightslider/{}/lightslider.html'.format(
            style)
        # Check if template for style exists:
        try:
            django.template.loader.select_template([template])
        except django.template.TemplateDoesNotExist:
            raise django.forms.ValidationError(
                _("Not a valid style (Template %s does not exist)") % template
            )
        return style


class LightsliderSlidePluginForm(django.forms.ModelForm):

    class Meta:
        fields = ['image', 'title', 'classes', ]
        model = models.LightsliderSlidePlugin

