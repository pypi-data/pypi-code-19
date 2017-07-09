"""This module coordinates the post-scraping text processing pipeline"""
from collections import namedtuple
from datetime import datetime
import logging
import json
import os

import requests
from dateutil.tz import tzlocal

from api import cache
from api.google.translate import TranslateClient as GoogleTranslate
from db.articles_db import Connection
from infrastructure.corenlp_local import NLPServerLocal
from .supported_lang import SupportedLang
from .extractors import words

_LOGGER = logging.getLogger(__name__)

class TranslationError(Exception):
    """An error with the translation process."""
    pass

class NLPClient: #pylint: disable=too-few-public-methods
    """Provides methods to interact with the CoreNLP Server."""

    # change this to use arbitrary positional args
    def __init__(self, ip_addr, *annotators):
        self.ip_addr = ip_addr
        self.annotators = annotators

    def process(self, lang, text):
        """Sends a request to the CoreNLP server to process the text.

        All of the annotators provided in the initialization method contribute
        to the options to the server via their 'name' property.

        args -
            text: the text to process
            lang: the language of the text.  Must be 'zh' or 'en'.
        """
        annotate_str = ','.join(annotator for annotator in self.annotators)

        """Makes a request to the IP address with the text and the default
        extractors"""
        props = {'annotators': annotate_str, 'outputFormat': 'json'}
        payload = {'properties': json.dumps(props), 'pipelineLanguage':lang}
        response = requests.post(self.ip_addr, data=text.encode('utf8'), params=payload)
        return response.text


def print_annotator_results(*annotators):
    """Helper function to print the parsed results of an annotator"""
    for annotator in annotators:
        _LOGGER.debug(10 * '*', annotator.name, 10 * '*')
        _LOGGER.debug(', '.join(annotator))


def setup_connection():
    """Sets up the connection to the database."""

    db_name = os.getenv('SCRAPER_POSTGRES_DB_NAME')
    user = os.getenv('SCRAPER_POSTGRES_USER')
    password = os.getenv('SCRAPER_POSTGRES_PASSWORD')
    host = os.getenv('SCRAPER_POSTGRES_HOST')
    port = os.getenv('SCRAPER_POSTGRES_PORT')

    settings = namedtuple('settings', 'db_name user password host port')
    settings_tup = settings(db_name, user, password, host, port)
    return Connection.setup(settings_tup)

def process_outstanding_articles(client, connection):
    """Looks up all of the articles that need to be processed and processes
    them.

    args:
        client - an NLPClient instance.
    """
    with connection as conn:
        articles = conn.get_unprocessed_articles()

        for article in articles:
            lang = SupportedLang(article.lang)
            resp = client.process(lang.value[:2], article.headline + ' ' + article.content)
            connection.set_corenlp_json_col(article[0], resp)


def add_corenlp_annotations(connection):
    """Adds annotation text for all articles that are lacking it."""
    server = NLPServerLocal()
    ip_addr = server.start()
    client = NLPClient(ip_addr, "tokenize", "lemma", "ner")
    process_outstanding_articles(client, connection)
    server.terminate()

def add_translations_to_article(corenlp_dict, translations):
    """Update the article dictionary json with the new translations."""
    # wrap words in an dictionary
    tup = namedtuple('ArticleStub', 'corenlp_json')
    article_stub = tup(corenlp_dict)
    article_words = list(words(article_stub))
    if len(translations) != len(article_words):
        raise TranslationError()

    trans_iter = iter(translations)

    sentences = corenlp_dict['sentences']
    for _, sentence in enumerate(sentences):
        for _, token  in enumerate(sentence['tokens']):
            next_trans = next(trans_iter)
            token['word_translation'] = next_trans

    corenlp_dict['translated_on'] = datetime.now(tzlocal()).isoformat()
    corenlp_dict['translated_by'] = 'google translate'

def add_cached_translations(trans_cache, word_list):
    """Looks in the cache for each word in word list, and preemptorily sets the
    translation if it exists.

    args:
        trans_cache - a cache with a get and set method.
        word_list - a list of 2-element (word, translation) lists. This
        function possibly overwrites the second element. """
    cache_hit = 0
    for trans in word_list:
        trans[1] = trans_cache.get(trans[0])
        if trans[1] is not None:
            cache_hit += 1

    msg = 'Of %d words, %d were cache hits (%f)'
    _LOGGER.warning(msg, len(word_list), cache_hit, cache_hit / len(word_list))


def cache_new_translations(trans_cache, word_list, new_trans):
    """Adds a group of new translations to the word list in an article.

    This function expects that the number of list in the word_list whose
    translation is None is exactly equal to the len of the new_trans list.

    args:
        trans_cache - a cache with get, set semantics
        word_list - a list of (original, translated) lists.
        new_trans - a list of translations."""

    missing_trans = [word for word in word_list if word[1] is None]
    if len(missing_trans) != len(new_trans):
        raise TranslationError("The number of new translations that came" \
                               "back exceeds the number of words in the" \
                               "article that need translations."
                              )

    for tup in zip(missing_trans, new_trans):
        word = tup[0][0]
        trans = tup[1]
        trans_cache.set(word, trans)
        tup[0][1] = trans


def add_translations(connection):
    """Tags the corenlp_json files as having been translated and adds
    translations to words and lemmas.

    args:
        connection - a database connection."""

    api_key = os.environ["GOOGLE_CLDS_TRANSLATE_API_KEY"]
    with connection as conn:
        needs_trans = conn.get_untranslated_articles()

    trans_cache = cache.Cache()

    def translate_tokens(tokens, from_lang):
        """Used to translate a token."""
        return GoogleTranslate(api_key).translate(tokens, SupportedLang.ENGLISH.value,
                                                  from_lang=from_lang)

    for art in needs_trans:
        word_list = [[word, None] for word in words(art)]
        add_cached_translations(trans_cache, word_list)
        non_cached = [word[0] for word in word_list if word[1] is None]
        translated_words = translate_tokens(non_cached, art.lang)
        cache_new_translations(trans_cache, word_list, translated_words)
        add_translations_to_article(art.corenlp_json,
                                    [word[1] for word in word_list])
        with connection as conn:
            conn.set_corenlp_json_col(art.id, json.dumps(art.corenlp_json))

def main():
    """Runs all of the pipeline."""
    connection = setup_connection()

    add_corenlp_annotations(connection)
    add_translations(connection)

    connection.teardown()

if __name__ == "__main__":
    main()
