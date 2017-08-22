# -*- coding: utf-8 -*-
import re

EMAIL_BODY_REGEX = re.compile('''
    ^(?!\.)                            # name may not begin with a dot
    (
      [-a-z0-9!\#$%&'*+/=?^_`{|}~]     # all legal characters except dot
      |
      (?<!\.)\.                        # single dots only
    )+
    (?<!\.)$                            # name may not end with a dot
''', re.VERBOSE | re.IGNORECASE)
EMAIL_DOMAIN_REGEX = re.compile('''
    (
      localhost
      |
      (
        [a-z0-9]
            # [sub]domain begins with alphanumeric
        (
          [-\w]*                         # alphanumeric, underscore, dot, hyphen
          [a-z0-9]                       # ending alphanumeric
        )?
      \.                               # ending dot
      )+
      [a-z]{2,}                        # TLD alpha-only
   )$
''', re.VERBOSE | re.IGNORECASE)

PHONE_NUMBER_REGEX = re.compile(r'(\d{2}[\d\-\(\)\s]{3,}\d{2})', re.VERBOSE | re.IGNORECASE)


def is_email(text):
    try:
        body, domain = text.rsplit('@', 1)
        match_body = EMAIL_BODY_REGEX.match(body)
        match_domain = EMAIL_DOMAIN_REGEX.match(domain)
        return match_body is not None and match_domain is not None
    except ValueError:
        return False


def is_phone(text):
    return PHONE_NUMBER_REGEX.match(text) is not None

