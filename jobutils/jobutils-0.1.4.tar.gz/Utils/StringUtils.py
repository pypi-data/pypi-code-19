#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import nltk

__author__ = 'laurynas@joberate.com'


def split_string_by_delimiters(text, delimiters=','):
    """

    :param text:
    :param delimiters:
    :return:
    """
    return [term.strip() for term in re.split(delimiters, text)]


def intersects(a, b):
    """
    Returns boolean indicator which defines whether two string intersect
    :param a:
    :param b:
    :return:
    """
    return len(list(set(a) & set(b))) > 0


def tokenize_words(text):
    """

    :param text:
    :return:
    """
    return re.findall(r'\w+', text)

def string_is_email(string):
    """

    :param string:
    :return:
    """
    return re.match(r'[^@]+@[^@]+\.[^@]+', string) is not None