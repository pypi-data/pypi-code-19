from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from fluent_contents.extensions import PluginHtmlField, PluginUrlField
from fluent_contents.models import ContentItem

from . import appsettings


@python_2_unicode_compatible
class ButtonItem(ContentItem):
    """
    Pager item, to show a previous/next page.
    The pages are auto determined, but can be overwritten
    """
    ALIGN_CHOICES = (
        ('', pgettext_lazy("align", u"Inline")),
        ('left', pgettext_lazy("align", u"Left")),
        ('center', pgettext_lazy("align", u"Center")),
        ('right', pgettext_lazy("align", u"Right")),
        ('block', pgettext_lazy("align", u"Full Width")),
    )

    title = models.CharField(_("Title"), max_length=200)
    url = PluginUrlField(_("URL"))

    style = models.CharField(_("Style"), max_length=50, choices=appsettings.FLUENTCMS_BUTTON_STYLES)
    size = models.CharField(_("Size"), blank=True, default='', max_length=10, choices=appsettings.FLUENTCMS_BUTTON_SIZES)
    align = models.CharField(_("Alignment"), blank=True, default='', max_length=50, choices=ALIGN_CHOICES)

    class Meta:
        verbose_name = _("Button")
        verbose_name_plural = _("Button")

    def __str__(self):
        return self.title

    @property
    def css_classes(self):
        classes = ['btn', self.style, self.size or '']
        if self.align:
            if self.align == 'left':
                classes.append('pull-left')
            elif self.align == 'right':
                classes.append('pull-right')
            elif self.align == 'block':
                classes.append('btn-block')

        return ' '.join(classes).rstrip().replace('  ', ' ')
