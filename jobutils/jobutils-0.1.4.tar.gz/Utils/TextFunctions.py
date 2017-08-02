#!/usr/bin/env python
import re

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import EnglishStemmer


def remove_punctuation(bio):
    """

    :param bio:
    :return:
    """
    return ''.join([c for c in bio if c not in ['-', '(', ')', ',', ';', ':', '.', '.', '/', '\'']])


def clean_bio(bio):
    """

    :param bio:
    :return:
    """
    bio = remove_punctuation(bio)
    bio = remove_stop_words(bio).split()
    bio = stem_word_list(bio)
    return ' '.join(bio)


def stem_word_list(terms):
    """

    :param terms:
    :return:
    """
    p_stemmer = EnglishStemmer()
    result = []


    for term in terms:
        stemmed_term = p_stemmer.stem(term)
        if len(term) > 0:
            result.append(stemmed_term)

    return result


def remove_stop_words(text):
    """

    :param text:
    :return:
    """
    text = text.lower()
    stopset = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(text)
    words =  [w for w in tokens if not w in stopset]
    return ' '.join(words)


def remove_non_alphabetical_characters_from_text(text):
    """

    :param text:
    :return:
    """
    pattern = re.compile('[^a-zA-Z]')
    return pattern.sub(r' ', text)


def remove_non_alphanumeric_characters_from_text(text):
    """
    
    :param text: 
    :return: 
    """
    pattern = re.compile('[^a-zA-Z0-9]')
    return pattern.sub(r' ', text)


def process_text(bio):
    """

    :param bio:
    :return:
    """
    pattern = re.compile('[\W_]+')
    bio = remove_stop_words(pattern.sub(r' ', bio))
    return bio


def return_text_as_set(text):
    """

    :param text:
    :return:
    """
    if text is None:
        text = ''

    return set(text.lower().split())


def extract_nth_word(fullname, position):
    """

    :param fullname:
    :param position:
    :return:
    """
    try:
        if fullname is None or len(fullname) == 0:
            return ''

        return fullname.lower().split()[position]
    except:
        return ''


def try_get_first_text_letter(text):
    """
    
    :param text: 
    :return: 
    """
    try:
        return text[0]
    except:
        return ""


def remove_text_in_brackets(text):
    """

    :param text:
    :return:
    """
    return re.sub("([\(\[]).*?([\)\]])", "", text).strip()


def sort_strings_by_length(url_a, url_b):
    """

    :param url_a:
    :param url_b:
    :return:
    """
    if len(url_a) > len(url_b):
        return 1
    elif len(url_a) < len(url_b):
        return -1
    else:
        return 0