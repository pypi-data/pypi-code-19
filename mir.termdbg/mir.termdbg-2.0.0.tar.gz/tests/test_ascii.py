import mir.termdbg.ascii as asciilib

ESC = 27  # ^[


def test_is_printable():
    assert asciilib.is_printable(ord('a'))


def test_is_printable_space():
    assert asciilib.is_printable(ord(' '))


def test_not_is_printable_tab():
    assert not asciilib.is_printable(ord('\t'))


def test_not_is_printable_newline():
    assert not asciilib.is_printable(ord('\n'))


def test_not_is_printable_escape():
    assert not asciilib.is_printable(ESC)
