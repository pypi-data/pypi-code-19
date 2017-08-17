# -*- coding: utf-8 -*-
import re
from .extractor import EntityConfig, EntitiesFirst, EntitiesAll


class Patterns(object):
    @staticmethod
    def create_name_patterns(taxonomy):
        return EntitiesFirst(
            EntityConfig(u'no me llamo {NP}', 'name', None, True, taxonomy),
            EntityConfig(u'mi nombre no es {NP}', 'name', None, True, taxonomy),
            EntityConfig(u'no soy {NP}', 'name', None, True, taxonomy),
            EntityConfig(u'me llamo {NP}', 'name', None, False, taxonomy),
            EntityConfig(u'mi nombre es {NP}', 'name', None, False, taxonomy),
            EntityConfig(u'soy {NP}', 'name', None, False, taxonomy),
            EntityConfig(u'{(NN|NNP)+}', 'name', None, False, taxonomy, exclude=['email', 'phone', 'sorry']),
        )
    
    @staticmethod
    def create_email_patterns(taxonomy):
        return EntitiesFirst(
            EntityConfig(u'correo no es {EMAIL}', 'email', None, True, taxonomy),
            EntityConfig(u'correo ELECTRONIC no es {EMAIL}', 'email', None, True, taxonomy),
            EntityConfig(u'correo ELECTRONIC? es? {EMAIL}', 'email', None, False, taxonomy),
            EntityConfig(u'WRITE a {EMAIL}', 'email', None, False, taxonomy),
            EntityConfig(u'{EMAIL}', 'email', None, False, taxonomy, strict=True),
        )
    
    @staticmethod
    def create_phone_patterns(taxonomy):
        return EntitiesFirst(
            EntityConfig(u'PHONEWORD no es {PHONE}', 'phone', None, True, taxonomy),
            EntityConfig(u'NUMBERWORD no es {PHONE}', 'phone', None, True, taxonomy),
            EntityConfig(u'NUMBERWORD de PHONEWORD no es {PHONE}', 'phone', None, True, taxonomy),
            EntityConfig(u'PHONEWORD es? {PHONE}', 'phone', None, False, taxonomy),
            EntityConfig(u'NUMBERWORD es? {PHONE}', 'phone', None, False, taxonomy),
            EntityConfig(u'NUMBERWORD de? PHONEWORD es? {PHONE}', 'phone', None, False, taxonomy),
            EntityConfig(u'{PHONE}', 'phone', None, False, taxonomy, strict=True),
        )

    @classmethod
    def create_contact_patterns(cls, taxonomy):
        name_patterns = cls.create_name_patterns(taxonomy)
        email_patterns = cls.create_email_patterns(taxonomy)
        phone_patterns = cls.create_phone_patterns(taxonomy)
        return EntitiesAll(email_patterns, phone_patterns, name_patterns)


class BaseParent(object):
    def __call__(self, term):
        pass


class EmailParent(BaseParent):
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
    
    def is_email(self, text):
        try:
            body, domain = text.rsplit('@', 1)
            match_body = self.EMAIL_BODY_REGEX.match(body)
            match_domain = self.EMAIL_DOMAIN_REGEX.match(domain)
            return match_body is not None and match_domain is not None
        except ValueError:
            return None

    def __call__(self, term):
        result = super(EmailParent, self).__call__(term)
        if result:
            return result
        if self.is_email(term):
            return ['email']


class PhoneParent(BaseParent):
    PHONE_NUMBER_REGEX = re.compile(r'(\d{2}[\d\-\(\)\s]{3,}\d{2})', re.VERBOSE | re.IGNORECASE)
    
    def is_phone(self, text):
        return self.PHONE_NUMBER_REGEX.match(text) is not None

    def __call__(self, term):
        result = super(PhoneParent, self).__call__(term)
        if result:
            return result
        if self.is_phone(term):
            return ['phone']


class ContactParent(EmailParent, PhoneParent):
    def __call__(self, term):
        result = super(ContactParent, self).__call__(term)
        if result:
            return result
        if term in [u'numero', u'número']:
            return ['numberword']
        if term in [u'teléfono', u'telefono', u'celular', u'mobil', u'móbil', u'mobile', u'telefonico', u'telefónico']:
            return ['phoneword']
        if term in [u'electrónico', u'electronico']:
            return ['electronic']
        if term in [u'escribir', u'escribeme', u'escribime', u'escribirme', u'contactame', u'contáctame', u'contactar', u'contactarme']:
            return ['write']
        if term in [u'disculpa', u'disculpame', u'discúlpame', u'espera']:
            return ['sorry']
