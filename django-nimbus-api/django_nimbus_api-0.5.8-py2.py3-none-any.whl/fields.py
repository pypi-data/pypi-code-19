# -*- coding: utf-8 -*-
from __future__ import absolute_import

import collections
import copy
import datetime
import decimal
import inspect
import json
import re
import uuid
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import (
    EmailValidator, MaxLengthValidator, MaxValueValidator, MinLengthValidator,
    MinValueValidator, RegexValidator, URLValidator, ip_address_validators
)
from django.forms import FilePathField as DjangoFilePathField
from django.forms import ImageField as DjangoImageField
from django.utils import six, timezone
from django.utils.dateparse import (
    parse_date, parse_datetime, parse_duration, parse_time
)
from django.utils.duration import duration_string
from django.utils.encoding import is_protected_type, smart_text
from django.utils.formats import localize_input, sanitize_separators
from django.utils.functional import cached_property
from django.utils.ipv6 import clean_ipv6_address
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from rest_framework.fields import Field, empty
from rest_framework import serializers


class DateTimeFieldWihTZ(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)
