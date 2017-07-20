# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import re
from django.core.exceptions import ValidationError


class AlNumPasswordValidator(object):
    '''
    forbit alphabet only or number only password
    '''

    def validate(self, password, user=None):
        xp0 = re.compile('^[a-zA-Z]+$')
        xp1 = re.compile('^[0-9]+$')
        if xp0.match(password) or xp1.match(password):
            raise ValidationError("英数のみ、数字のみのパスワードは指定することができません。")

    def get_help_text(self):
        return "英数と数字を混在させる必要があります。"


class SimplePasswordValidator(object):
    '''
    forbit only two kinds of char password. e.g) aaaa1111
    '''

    def validate(self, password, user=None):
        s = set(password)
        if len(s) == 2:
            raise ValidationError("英数字は必ず３種類以上含めて下さい。")

    def get_help_text(self):
        return "英数字は必ず３種類以上含めて下さい。"


class CheckIdPasswordValdiator(object):
    '''
    forbit password is same as username
    '''

    def validate(self, password, user=None):
        if not user:
            return
        if user.username == password:
            raise ValidationError("IDと同じパスワードは利用不可です。")

    def get_help_text(self):
        return "IDと同じパスワードは利用不可です。"
