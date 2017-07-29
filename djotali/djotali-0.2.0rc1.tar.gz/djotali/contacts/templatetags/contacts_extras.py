# coding: utf-8
import phonenumbers
from django import template
from django.template.defaultfilters import stringfilter
from phonenumbers.phonenumberutil import NumberParseException

register = template.Library()


@register.filter
@stringfilter
def format_number(phone_number):
    try:
        return phonenumbers.format_number(phonenumbers.parse(phone_number, region='SN'),
                                          phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except NumberParseException:
        return phone_number
