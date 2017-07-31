from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from . import models, forms

###############
# Lightslider #
###############


# Base Classes
class LightsliderBase(CMSPluginBase):
    module = _("Bootstrap3")


class LightsliderSlideBase(LightsliderBase):
    require_parent = True
    parent_classes = ['LightsliderCMSPlugin']

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['image'] = instance.image
        return context

    def get_slide_template(self, instance, name='slide'):
        if instance.parent is None:
            # defaults to default style
            style = models.LightsliderPlugin.STYLE_DEFAULT
        else:
            style = getattr(instance.parent.get_plugin_instance()[0], 'style', models.LightsliderPlugin.STYLE_DEFAULT)
        return 'aldryn_lightslider/plugins/lightslider/{}/{}.html'.format(style, name)

    def get_render_template(self, context, instance, placeholder):
        return self.get_slide_template(instance=instance)


# Plugins
class LightsliderCMSPlugin(LightsliderBase):
    name = _('Lightslider')
    model = models.LightsliderPlugin
    change_form_template = 'admin/aldryn_lightslider/base.html'
    render_template = False
    form = forms.LightsliderPluginForm
    allow_children = True
    child_classes = [
        'LightsliderSlideCMSPlugin',
        # 'Bootstrap3CarouselSlideFolderCMSPlugin',
    ]
    fieldsets = (
        (None, {
            'fields': (
                'number_of_concurrent_slides',
                'number_of_paginating_slides',
                'style',
                'transition_style',
                'transition_effect',
                ('ride', 'interval'),
                'aspect_ratio',

            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': (
                'classes',
                'pause',
                'wrap',
            ),
        }),
    )

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        if instance.child_plugin_instances:
            number_of_slides = sum([
                plugin.folder.file_count
                if isinstance(plugin, LightsliderCMSPlugin) else 1
                for plugin in instance.child_plugin_instances
            ])
        else:
            number_of_slides = 0
        context['slides'] = range(number_of_slides)
        return context

    def get_render_template(self, context, instance, placeholder):
        return 'aldryn_lightslider/plugins/lightslider/{}/lightslider.html'.format(
            instance.style)


class LightsliderSlideCMSPlugin(LightsliderSlideBase):
    form = forms.LightsliderSlidePluginForm
    model = models.LightsliderSlidePlugin
    name = _('Lightslider Slide')
    change_form_template = 'admin/aldryn_lightslider/base.html'
    allow_children = True
    fieldsets = (
        (None, {
            'fields': (
                'image',
                'title',
            )
        }),
    )


class LightsliderSlideFolderCMSPlugin(LightsliderSlideBase):
    """
    Slide Plugin that renders a slide for each image in the linked folder.
    """
    name = _('Lightslider Slides Folder')
    model = models.LightsliderSlideFolderPlugin

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['slide_template'] = self.get_slide_template(
            instance=instance,
            name='image_slide',
        )
        return context

    def get_render_template(self, context, instance, placeholder):
        return self.get_slide_template(instance=instance, name='slide_folder')


plugin_pool.register_plugin(LightsliderCMSPlugin)
plugin_pool.register_plugin(LightsliderSlideCMSPlugin)
# plugin_pool.register_plugin(Bootstrap3CarouselSlideFolderCMSPlugin)
