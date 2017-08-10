"""Tests for format_char().

Since the format is for human consumption, we don't want to enforce a specific
format in these tests, we just want to make sure the function works for all
valid inputs.
"""

from mir.termdbg.format import format_char

ESC = 27  # ^[


def test_format_char():
    assert format_char(ord('a')) == ' 97, 0o141, 0x61, a'


def test_format_char_escape():
    assert format_char(ESC) == ' 27, 0o033, 0x1B, ESC, ␛, ^[, Escape'


def test_format_char_space():
    assert format_char(ord(' ')) == ' 32, 0o040, 0x20, SPC'


def test_format_char_tab():
    assert format_char(ord('\t')) == \
        '  9, 0o011, 0x09, HT, ␉, ^I, Horizontal Tab'
