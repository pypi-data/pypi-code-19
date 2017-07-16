import functools
import unicodedata

import iso639
import langdetect
import neologdn


__all__ = ['normalize']


def normalize(document, language=None):
    if language is not None and not iso639.is_valid639_1(language):
        raise ValueError('"{}" is not a valid ISO 639-1 code.'
                         .format(language))

    return {
        'en': normalize_english,
        'ja': normalize_japanese,
    }.get(language or detect_language(document), normalize_english)(document)


def detect_language(document):
    try:
        return langdetect.detect(document)
    except:
        return None


def common_normalization(func):
    @functools.wraps(func)
    def wrapper(document):
        return func(unicodedata.normalize('NFKC', document.strip()))
    return wrapper


@common_normalization
def normalize_english(document):
    return document


@common_normalization
def normalize_japanese(document):
    return neologdn.normalize(document)
