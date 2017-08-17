from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from utf8field import forms


class UTF8FileField(models.FileField):
    description = _('A text file containing only UTF-8 text')

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.UTF8FileField}
        defaults.update(kwargs)
        return super(UTF8FileField, self).formfield(**defaults)
