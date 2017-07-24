from dateutil.relativedelta import relativedelta
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
import datetime


class AtLeastOneRequiredValidator(object):
    message = _('At least one of the fields ({}) is required.')

    def __init__(self, *fields):
        self.fields = fields

    def __call__(self, attrs):
        passes = False
        for field in self.fields:
            if attrs.get(field):
                passes = True
                break

        if not passes:
            fields_str = ', '.join(self.fields)
            raise serializers.ValidationError(self.message.format(fields_str))


class AtLeastAge(object):
    message = _('Need to be at least {} years of age.')

    def __init__(self, age, raises=exceptions.PermissionDenied):
        self.age = age
        self.raises = raises

    def __call__(self, value):
        age = relativedelta(datetime.date.today(), value)

        if age.years < self.age:
            raise self.raises(self.message.format(self.age))


class GreaterThan(object):
    """
    Validates that one value is greater than another value
    """
    message = _('{} must be greater than {}.')

    def __init__(self, low_field, high_field):
        self.low_field = low_field
        self.high_field = high_field

    def __call__(self, attrs):
        if attrs.get(self.low_field) >= attrs.get(self.high_field):
            raise serializers.ValidationError(self.message.format(self.high_field, self.low_field))
