# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import re
import logging
import json
from functools import wraps

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.six import string_types, text_type
from django.utils.translation import ugettext as _, ungettext


class CustomPasswortValidator(object):

    def validate(self, password, user=None):
        try:
            password.encode('ascii')
        except UnicodeEncodeError:
            raise ValidationError(_('Password must only contain ascii character.'))
        # check for digit
        if not any(char.isdigit() for char in password):
            raise ValidationError(_('Password must contain at least 1 digit.'))
        # check for letter
        if not any(char.isalpha() and char.isupper() for char in password):
            raise ValidationError(_('Password must contain at least 1 upper letter.'))
        if not any(char.isalpha() and char.islower() for char in password):
            raise ValidationError(_('Password must contain at least 1 lower letter.'))

    def get_help_text(self):
        return _("Your password must contain at least 1 digit and 1 upper letter and 1 lower letter.")


