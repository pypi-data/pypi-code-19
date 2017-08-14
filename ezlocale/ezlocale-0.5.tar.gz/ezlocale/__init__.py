"""
Copyright (c) 2017 James Patrick Dill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import faste
import googletrans

from .langs import language, get_language

__author__ = "Patrick Dill"
__version__ = "0.5"

DEST = language.EN

_translators = {}


class Translator(object):
    def __init__(self, dest, src="en", max_cache_size=128):
        if dest is None:
            raise TypeError("No destination language specified.")

        self.translator = googletrans.Translator()

        self.src = src
        self.dest = dest

        self.cache = faste.caches.LFUCache(max_cache_size)

    def translate(self, text):
        if not isinstance(text, str):
            raise TypeError("Text to translate must be str")

        if text not in self.cache:
            self.cache[text] = self.translator.translate(text, dest=self.dest, src=self.src).text

        return self.cache[text]


def gettext(text, dest=None, src=language.EN):
    """
    Gets text in specified language.

    :param text: Text to translate
    :param dest: (keyword) Destination language. Defaults to ezlocale.DEST
    :param src: (keyword) Source language. Defaults to English
    :returns: Translated text
    """
    dest = dest or DEST

    key = (src, dest)

    if key not in _translators:
        _translators[key] = Translator(dest.value, src=src.value)

    return _translators[key].translate(str(text))


def clear_cache():
    """
    Clears translator caches.
    """
    for name in list(_translators.keys()):
        del _translators[name]
