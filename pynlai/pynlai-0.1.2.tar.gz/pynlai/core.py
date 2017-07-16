# -*- coding: utf-8 -*-

'''
core
----

core functions and classes for pynlai.
'''


from collections import OrderedDict
from functools import wraps
from operator import attrgetter
import six

from spacy.en import English
from spacy.tokens import Doc
from spacy.symbols import dobj, nsubj, VERB


def create_view(obj, view):
    '''
    filters object through view fields and returns field: value dict
    '''

    return OrderedDict([(f, attrgetter(f)(obj)) for f in view])


def nlp_preprocess(nlp_model):
    '''
    a decorator to pre-process text passed to nlp functions
    requires keyword args that at least contain doc and nlp
    '''

    def decorator(fcn):

        @wraps(fcn)
        def wrapper(*args, **kwargs):

            name = fcn.__name__

            kwargs.setdefault('doc', None)
            kwargs.setdefault('nlp', None)

            # validations
            if args:
                raise ValueError('pass args by name to %s' % name)

            if type(kwargs['doc']) not in (Doc, str, six.text_type):
                m = 'must pass `doc` arg of Doc or text type not %s'
                raise ValueError(m % type(kwargs['doc']))

            if type(kwargs['nlp']) is not nlp_model:
                m = 'must pass `nlp` arg of type %s'
                raise ValueError(m % nlp_model)

            # pre-processors
            if type(kwargs['doc']) is Doc:
                pass

            elif type(kwargs['doc']) is six.text_type:
                kwargs['doc'] = kwargs['nlp'](kwargs['doc'])

            else:
                kwargs['doc'] = kwargs['nlp'](six.u(kwargs['doc']))

            # call decorated function using pre-processed kwargs
            return fcn(**kwargs)

        return wrapper

    return decorator


@nlp_preprocess(English)
def find_dep(doc, dep, pos, **kwargs):
    '''
    finds dependencies in the sentence matching dep and (head) pos
    returns list of matching tokens
    '''

    return [t for t in doc if t.dep == dep and t.head.pos == pos]


@nlp_preprocess(English)
def to_ent(doc, **kwargs):
    '''
    returns entities and annotations
    see https://spacy.io/docs/usage/entity-recognition
    '''

    return [ent for ent in doc.ents]


@nlp_preprocess(English)
def to_nc(doc, **kwargs):
    '''
    returns noun chunks using spacy syntactic dependency parser
    see https://spacy.io/docs/usage/dependency-parse
    '''

    return [nc for nc in doc.noun_chunks]


@nlp_preprocess(English)
def to_obj(doc, **kwargs):
    '''
    finds the objects(s) of the sentence, which is the noun that is
    the recipient of a verb action
    '''

    return find_dep(doc=doc, dep=dobj, pos=VERB, **kwargs)


@nlp_preprocess(English)
def to_pos(doc, **kwargs):
    '''
    returns parts of speech from spacy POS tagger
    see https://spacy.io/docs/usage/pos-tagging
    '''

    return [word_token for word_token in doc]


@nlp_preprocess(English)
def to_sub(doc, **kwargs):
    '''
    finds the subject(s) of the sentence, which is the noun that is
    performing the verb(s) in the sentence
    '''

    return find_dep(doc=doc, dep=nsubj, pos=VERB, **kwargs)
