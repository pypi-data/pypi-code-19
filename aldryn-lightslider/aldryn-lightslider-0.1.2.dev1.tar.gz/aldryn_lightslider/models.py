# -*- coding: utf-8 -*-
from functools import partial

import filer
from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

import collections
import os
import django.forms.models

from . import utils, constants, fields

##########
# Mixins #  do NOT use outside of this package!
##########  Because changes here might require Database migrations!

CMSPluginField = partial(
    models.OneToOneField,
    to=CMSPlugin,
    related_name='+',
    parent_link=True,
)


class Classes(models.TextField):
    # TODO: validate
    default_field_class = fields.Classes

    def __init__(self, *args, **kwargs):
        if 'blank' not in kwargs:
            kwargs['blank'] = True
        if 'default' not in kwargs:
            kwargs['default'] = ''
        if 'help_text' not in kwargs:
            kwargs['help_text'] = 'space separated classes that are added to the class. see <a href="http://getbootstrap.com/css/" target="_blank">bootstrap docs</a>'
        super(Classes, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': self.default_field_class,
        }
        defaults.update(kwargs)
        return super(Classes, self).formfield(**defaults)


# Create your models here.
@python_2_unicode_compatible
class LightsliderPlugin(CMSPlugin):
    STYLE_DEFAULT = 'standard'

    TRANSITION_SLIDE = 'slide'
    TRANSITION_FADE = 'fade'

    TRANSITION_EFFECT_LINEAR = 'linear'
    TRANSITION_EFFECT_EASE = 'ease'
    TRANSITION_EFFECT_EASE_IN = 'ease-in'
    TRANSITION_EFFECT_EASE_OUT = 'ease-out'
    TRANSITION_EFFECT_EASE_IN_OUT = 'ease-in-out'

    STYLE_CHOICES = [
        (STYLE_DEFAULT, _('Standard')),
    ]

    TRANSITION_STYLE_CHOICES = (
        (TRANSITION_SLIDE, _('Slide')),
        (TRANSITION_FADE, _('Fade')),
    )

    TRANSITION_EFFECT_CHOICES = (
        (TRANSITION_EFFECT_LINEAR, _('Linear')),
        (TRANSITION_EFFECT_EASE, _('Ease')),
        (TRANSITION_EFFECT_EASE_IN, _('Ease in')),
        (TRANSITION_EFFECT_EASE_OUT, _('Ease out')),
        (TRANSITION_EFFECT_EASE_IN_OUT, _('Ease in out')),
    )

    cmsplugin_ptr = CMSPluginField()

    number_of_concurrent_slides = models.PositiveIntegerField(
        _('Number of concurrent slides'),
        default=3,
        help_text=_('How many images displayed '
                    'at the same time.'),
    )

    number_of_paginating_slides = models.PositiveIntegerField(
        _('Number of paginating slides'),
        default=1,
        help_text=_('How many images to slide out '
                    'when going forward or backward.'),
    )

    style = models.CharField(
        _('Style'),
        choices=STYLE_CHOICES + utils.get_additional_styles(),
        default=STYLE_DEFAULT,
        max_length=50,
    )
    aspect_ratio = models.CharField(
        _("aspect ratio"),
        max_length=10,
        blank=True,
        default='',
        choices=constants.ASPECT_RATIO_CHOICES
    )
    transition_style = models.CharField(
        _('Transition Style'),
        choices=TRANSITION_STYLE_CHOICES,
        default='',
        max_length=50,
        blank=True,
    )
    transition_effect = models.CharField(
        _('Transition Effect'),
        choices=TRANSITION_EFFECT_CHOICES,
        default='',
        max_length=50,
        blank=True,
    )
    ride = models.BooleanField(
        _('Ride'),
        default=True,
        help_text=_('Whether to mark the carousel as animating '
                    'starting at page load.'),
    )
    interval = models.IntegerField(
        _('Interval'),
        default=5000,
        help_text=_("The amount of time to delay between automatically "
                    "cycling an item."),
    )
    wrap = models.BooleanField(
        default=True,
        blank=True,
        help_text=_('Whether the carousel should cycle continuously or '
                    'have hard stops.')
    )
    pause = models.BooleanField(
        default=True,
        blank=True,
        help_text=_('Pauses the cycling of the carousel on mouseenter and '
                    'resumes the cycling of the carousel on mouseleave.')
    )
    classes = Classes()

    def __str__(self):
        data = django.forms.models.model_to_dict(self)
        data.update(dict(
            style_label=_('Style'),
            transition_effect_label=_('Transition Effect'),
            ride_label=_('Ride'),
            interval_label=_('Interval'),
            aspect_ratio_label=_('Aspect Ratio'),
        ))
        fields = [
            'style',
            'transition_effect',
            'ride',
            'interval',
            'aspect_ratio',
        ]
        if not data['ride']:
            fields.remove('interval')
        return ', '.join([
            '{key}: {value}'.format(
                key=data['{}_label'.format(field)],
                value=data[field]
            ) for field in fields
        ])

    def srcset(self):
        # more or less copied from image plugin.
        # TODO: replace with generic sizes/srcset solution
        items = collections.OrderedDict()
        if self.aspect_ratio:
            aspect_width, aspect_height = tuple([int(i) for i in self.aspect_ratio.split('x')])
        else:
            aspect_width, aspect_height = None, None
        for device in constants.DEVICES:
            width = device['width_gutter']  # TODO: should this should be based on the containing col size?
            width_tag = str(width)
            if aspect_width is not None and aspect_height is not None:
                height = int(float(width)*float(aspect_height)/float(aspect_width))
                crop = True
            else:
                height = 0
                crop = False
            items[device['identifier']] = {
                'size': (width, height),
                'size_str': "{}x{}".format(width, height),
                'width_str': "{}w".format(width),
                # 'subject_location': self.file.subject_location,
                'upscale': True,
                'crop': crop,
                'aspect_ratio': (aspect_width, aspect_height),
                'width_tag': width_tag,
            }

        return items


@python_2_unicode_compatible
class LightsliderSlidePlugin(CMSPlugin):
    excluded_attr_keys = ['class', 'href', 'target', ]
    cmsplugin_ptr = CMSPluginField()
    image = filer.fields.image.FilerImageField(
        verbose_name=_('image'),
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=100,
        blank=True
    )
    classes = Classes()

    def __str__(self):
        image_text = title_text = ''

        if self.image_id:
            if self.image.name:
                image_text = self.image.name
            elif self.image.original_filename \
                    and os.path.split(self.image.original_filename)[1]:
                image_text = os.path.split(self.image.original_filename)[1]
            else:
                image_text = 'Image'
        if self.title:
            text = strip_tags(self.title).strip()
            if len(text) > 100:
                title_text = '{}...'.format(text[:100])
            else:
                title_text = '{}'.format(text)

        if image_text and title_text:
            return '{} ({})'.format(image_text, title_text)
        else:
            return image_text or title_text


@python_2_unicode_compatible
class LightsliderSlideFolderPlugin(CMSPlugin):
    cmsplugin_ptr = CMSPluginField()
    folder = filer.fields.folder.FilerFolderField(
        verbose_name=_('folder'),
    )
    classes = Classes()

    def __str__(self):
        if self.folder_id:
            return self.folder.pretty_logical_path
        else:
            return _('not selected yet')
