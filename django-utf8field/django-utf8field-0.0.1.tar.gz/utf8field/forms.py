from django.forms import FileField
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class UTF8FileField(FileField):
    def to_python(self, data):
        if data:
            try:
                data.read().decode('utf-8')
            except UnicodeError:
                raise ValidationError(_('Non UTF8-content detected'), code='utf8')

        return super(UTF8FileField, self).to_python(data)
