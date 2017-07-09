"""Feature extractors that extract features from a CoreNLP annotated
response."""

from collections import namedtuple
from itertools import chain

from .wordnet import WordNetExpander
from .supported_lang import SupportedLang

def _ner_extractor(resp_dict, ner_type, lang):
    """Helper for different types of named-entities.
    
    Input:
        resp_dict - the CoreNLP-generated dictionary
        ner_type - the treebank tag that must be set for the NER field to match
        lang - the SupportedLang of the article.
        
    Returns:
        A generator of (word, pos) tuples."""

    nt = namedtuple('Term', 'word pos')
    for sentence in resp_dict['sentences']:
        for token in sentence['tokens']:
            if token['ner'] == ner_type:
                key = 'word' if lang is SupportedLang.ENGLISH else 'word_translation'
                yield nt(token[key], token['pos'])


def _pos_extractor(resp_dict, pos_set, lang):
    """Helper function for extracting tokens that are a particular part of
    speech."""
    for sentence in resp_dict['sentences']:
        for token in sentence['tokens']:
            if token['pos'] in pos_set:
                key = 'word' if lang is SupportedLang.ENGLISH else 'word_translation'
                yield token[key]


def _make_response_extractor(resp_dict, key, lang):
    """Creates an extractor from each token in a sentence."""
    for sentence in resp_dict['sentences']:
        for token in sentence['tokens']:
            key = 'word' if lang is SupportedLang.ENGLISH else 'word_translation'
            yield token[key]


def nouns(article):
    """Extracts all the words that are nouns.

    The nouns are those tokens with the Tag 'NN', 'NNS',
    'NNP', and 'NNPS', standing for Noun, singluar or mass, Noun, plural,
    Proper noun, singular, Proper noun, plural for english articles.  For
    chinese articles, they are tagged with 'NT', 'NR', or 'NN' for Temporal
    Noun, Proper Noun, or Verbal Noun/Other Noun.

    See https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    and http://repository.upenn.edu/cgi/viewcontent.cgi?article=1039&context=ircs_reports
    """
    en_nouns_pos = {'NN', 'NNS', 'NNP', 'NNPS'}
    ch_nouns_pos = {'NT', 'NR', 'NN'}
    lang = SupportedLang(article.lang)
    tags = en_nouns_pos if lang is SupportedLang.ENGLISH else ch_nouns_pos
    return _pos_extractor(article.corenlp_json, tags, lang)


def verbs(article):
    """Extracts all the words that are verbs.

    Verbs are those tokens with the tags 'VB', 'VBD', 'VBG', 'VBN', 'VBP', and
    'VBZ', standing for Verb base form, Verb past tense, Verb gerund or present
    participle, Verb past participle, Verb non-third person singular present,
    and Verb third-person singular present.

    For chinese the tags are VV, VA, VC, VE, for Other Verb, Predicative
    Adjective, Copula, and you3 as the main verb.
    """
    en_verb_pos = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    ch_verb_pos = {'VV', 'VC', 'VE'}
    lang = SupportedLang(article.lang)
    tags = en_verb_pos if lang is SupportedLang.ENGLISH else ch_verb_pos
    return _pos_extractor(article.corenlp_json, tags, lang)


def adjectives(article):
    """Extract all the words that are adjectives.
    """
    en_adj_pos = {'JJ', 'JJR', 'JJS'}
    ch_adj_pos = {'JJ'}
    lang = SupportedLang(article.lang)
    tags = en_adj_pos if lang is SupportedLang.ENGLISH else ch_adj_pos
    return _pos_extractor(article.corenlp_json, tags, lang)


def adverbs(article):
    """Extract all the words that are adverbs
    """
    en_adverb_pos = {'RB', 'RBR', 'RBS', 'WRB'}
    ch_adverb_pos = {'AD'}
    lang = SupportedLang(article.lang)
    tags = en_adverb_pos if lang is SupportedLang.ENGLISH else ch_adverb_pos
    return _pos_extractor(article.corenlp_json, tags, lang)


def people(article):
    """Extract the named entities that are people."""
    lang = SupportedLang(article.lang)
    yield from (word for word, _ in _ner_extractor(article.corenlp_json, 'PERSON', lang))


def locations(article):
    """Extract the named entities that are places."""
    lang = SupportedLang(article.lang)
    yield from (word for word, _ in _ner_extractor(article.corenlp_json, 'LOCATION', lang))


def dates(article):
    """Extract the named entities that are dates."""
    lang = SupportedLang(article.lang)
    if lang is SupportedLang.MAINLAND_CHINESE:
        yield from (word for word, pos in _ner_extractor(article.corenlp_json,
                                                       'MISC', lang) if pos == 'NT')
    else:
        yield from (word for word, _ in _ner_extractor(article.corenlp_json,
                                                       'DATE', lang))

def misc_ner(article):
    """Return misc. ners"""
    lang = SupportedLang(article.lang)
    yield from (word for word, _ in _ner_extractor(article.corenlp_json,
                                                   'MISC', lang))

def words(article):
    """Extracts all the 'word' elements from the response."""
    return _make_response_extractor(article.corenlp_json, 'word',
                                    SupportedLang(article.lang))


def lemmas(article):
    """Extracts all the 'lemma' elements from the response."""
    return _make_response_extractor(article.corenlp_json, 'lemma',
                                    SupportedLang(article.lang))



def synset_nouns(article):
    expander = WordNetExpander()
    n = nouns(article)
    return chain.from_iterable(map(expander.noun, n))


def synset_verbs(article):
    expander = WordNetExpander()
    v = verbs(article)
    return chain.from_iterable(map(expander.verb, v))


def synset_adj(article):
    expander = WordNetExpander()
    adj = adjectives(article)
    return chain.from_iterable(map(expander.adj, adj))


def synset_adv(article):
    expander = WordNetExpander()
    adv = adverbs(article)
    return chain.from_iterable(map(expander.adv, adv))
