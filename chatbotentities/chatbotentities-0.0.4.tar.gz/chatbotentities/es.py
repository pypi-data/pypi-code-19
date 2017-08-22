# -*- coding: utf-8 -*-
import re
from .extractor import EntityConfig, EntityNegation, EntitiesFirst, EntitiesAll

from pattern.search import Classifier, Taxonomy


class BasePatterns(object):
    @classmethod
    def taxonomy(cls):
        result = Taxonomy()
        result.classifiers.append(Classifier(cls.parent))
        return result


class EmailPatterns(BasePatterns):
    @classmethod
    def parent(cls, term):
        from .validators import is_email
        if is_email(term):
            return ['email']
        if term in [u'electrónico', u'electronico']:
            return ['electronico']
        if term in [u'escribir', u'escribeme', u'escribime', u'escribirme', u'contactame', u'contáctame', u'contactar', u'contactarme']:
            return ['escribir']

    @classmethod
    def patterns(cls):
        from .extractor import EntityFirst, EntityPattern
        taxonomy = cls.taxonomy()
        def negation(expression):
            return EntityPattern('email', expression, negation=True, taxonomy=taxonomy)
        def extractor(expression, negation, strict=False):
            return EntityPattern('email', expression, variables={'value': 1}, 
                       negation=negation, taxonomy=taxonomy, strict=strict)
        return EntityFirst(
            negation(u'mal el|mi correo ELECTRONICO?'),
            negation(u'correo ELECTRONICO? es|esta|está mal|incorrecto'),
            negation(u'correo ELECTRONICO? no es|esta|está bien|correcto'),
            negation(u'no es mi|el correo ELECTRONICO?'),
            extractor(u'correo ELECTRONICO? no es {EMAIL}', negation=True),
            extractor(u'correo ELECTRONICO? es? {EMAIL}', negation=False),
            extractor(u'ESCRIBIR a {EMAIL}', negation=False),
            extractor(u'{EMAIL}', negation=False)
        )


class PhonePatterns(BasePatterns):
    @classmethod
    def parent(cls, term):
        from .validators import is_phone
        if is_phone(term):
            return ['phone']
        if term in [u'numero', u'número']:
            return ['numero']
        if term in [u'teléfono', u'telefono', u'celular', u'mobil', u'móbil', u'mobile', u'telefonico', u'telefónico', 'cel']:
            return ['telefono']
        
    @classmethod
    def patterns(cls):
        from .extractor import EntityFirst, EntityPattern
        taxonomy = cls.taxonomy()
        def negation(expression):
            return EntityPattern('phone', expression, negation=True, taxonomy=taxonomy)
        def extractor(expression, negation, strict=False):
            return EntityPattern('phone', expression, variables={'value': 1}, 
                       negation=negation, taxonomy=taxonomy, strict=strict)
        return EntityFirst(
            negation(u'mal el|en TELEFONO|NUMERO'),
            negation(u'mal el NUMERO de? TELEFONO'),
            negation(u'TELEFONO|NUMERO esta|está mal'),
            negation(u'NUMERO de? TELEFONO esta|está mal'),
            negation(u'no es mi TELEFONO|NUMERO'),
            negation(u'no es mi NUMERO de? TELEFONO'),
            extractor(u'NUMERO|TELEFONO no es {PHONE}', negation=True),
            extractor(u'NUMERO de TELEFONO no es {PHONE}', negation=True),
            extractor(u'TELEFONO|NUMERO es? {PHONE}', negation=False),
            extractor(u'NUMERO de? TELEFONO es? {PHONE}', negation=False),
            extractor(u'{PHONE}', negation=False, strict=True),
        )


class NamePatterns(BasePatterns):
    @classmethod
    def parent(cls, term):
        if term in [u'disculpa', u'disculpame', u'discúlpame', u'espera']:
            return ['sorry']
        if term in ['nombre']:
            return ['name']

    @classmethod
    def patterns(cls):
        from .extractor import EntityFirst, EntityPattern
        taxonomy = cls.taxonomy()
        def negation(expression):
            return EntityPattern('name', expression, negation=True, taxonomy=taxonomy)
        def extractor(expression, negation, strict=False, exclude=None):
            return EntityPattern('name', expression, variables={'value': 1},
                       negation=negation, taxonomy=taxonomy, strict=strict, exclude=exclude)
        return EntityFirst(
            negation(u'mal el nombre'),
            negation(u'nombre esta|está mal'),
            negation(u'no es mi nombre'),
            
            extractor(u'equivoque|equivoqué con|escribiendo|poniendo el nombre', negation=True),
            extractor(u'no me llamo {(NN|NNP)+}', negation=True),
            extractor(u'mi nombre no es {(NN|NNP)+}', negation=True),
            extractor(u'no soy {(NN|NNP)+}', negation=True),
            
            extractor(u'me llamo {(NN|NNP)+}', negation=False),
            extractor(u'mi nombre es {(NN|NNP)+}', negation=False),
            extractor(u'soy {(NN|NNP)+}', negation=False),
        )


class CompanyPatterns(BasePatterns):
    @classmethod
    def parent(cls, term):
        if term in [u'disculpa', u'disculpame', u'discúlpame', u'espera']:
            return ['sorry']
        if term in ['nombre']:
            return ['name']
        if term in ['empresa', 'compañia', 'compania', 'compañía', 'companía']:
            return ['company']
   
    @classmethod
    def patterns(cls):
        from .extractor import EntityFirst, EntityPattern
        taxonomy = cls.taxonomy()
        def negation(expression):
            return EntityPattern('company', expression, negation=True, taxonomy=taxonomy)
        def extractor(expression, negation, strict=False, exclude=None):
            return EntityPattern('company', expression, variables={'value': 1},
                       negation=negation, taxonomy=taxonomy, strict=strict, exclude=exclude)
        return EntityFirst(
            negation(u'mal (el nombre de)? la COMPANY'),
            negation(u'(nombre de)? la COMPANY esta|está mal'),
            negation(u'no es (el nombre de)? la COMPANY'),
            extractor(u'equivoque|equivoqué con|escribiendo|poniendo (el nombre de)? la COMPANY', negation=True),
            extractor(u'la COMPANY no se llama {(NN|NNP)+}', negation=True),
            extractor(u'el nombre de la COMPANY no es {(NN|NNP)+}', negation=True),
            extractor(u'la COMPANY no es {(NN|NNP)+}', negation=True),
            extractor(u'COMPANY se llama {(NN|NNP)+}', negation=False),
            extractor(u'nombre de la COMPANY es {(NN|NNP)+}', negation=False),
            extractor(u'COMPANY es {(NN|NNP)+}', negation=False),
        )


class DefaultNamePatterns(NamePatterns):
    @classmethod
    def patterns(cls):
        from .extractor import EntityPattern
        taxonomy = cls.taxonomy()
        return EntityPattern(None, u'{(NN|NNP)+}', variables={'value': 1}, negation=False,
                   taxonomy=taxonomy, strict=False, exclude=['email', 'phone', 'sorry', 'name'])


class ContactPatterns(BasePatterns):
    @classmethod
    def patterns(cls):
        from .extractor import EntityConcat
        email = EmailPatterns.patterns()
        phone = PhonePatterns.patterns()
        name = NamePatterns.patterns()
        company = CompanyPatterns.patterns()
        default_name = DefaultNamePatterns.patterns()
        return (email + phone + company + name) * default_name

