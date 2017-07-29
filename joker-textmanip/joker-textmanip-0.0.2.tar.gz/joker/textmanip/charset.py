#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import random


# copied from the string module
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
alnums = digits + ascii_letters
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace

# http://www.garykessler.net/library/base64.html
b64_chars = digits + ascii_letters + '+/'
b64_urlsafe_chars = ascii_letters + digits + '_-'
b32_chars = ascii_uppercase + '234567'


cjk_unicode_ranges = [
    (0x2E80, 0x2EFF, "CJK Radicals Supplement"),
    (0x3000, 0x303F, "CJK Symbols & Punctuation"),
    (0x31C0, 0x31EF, "CJK Strokes"),
    (0x3200, 0x32FF, "CJK Enclosed Letters and Months"),
    (0x3300, 0x33FF, "CJK Compatibility"),
    (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A"),
    (0x4E00, 0x9FFF, "CJK Unified Ideographs"),
    (0xF900, 0xFAFF, "CJK Compatibility Ideographs"),
    (0xFE30, 0xFE4F, "CJK Compatibility Forms"),
]


def random_string(length, chars=None):
    if not chars:
        chars = alnums
    return ''.join(random.choice(chars) for _ in range(length))


