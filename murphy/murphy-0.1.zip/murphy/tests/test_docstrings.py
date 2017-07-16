""" Docstring testsx
"""
from nose.tools import assert_is_not_none, assert_true


def test_murphy_docstring():
    import murphy
    assert_is_not_none(murphy.__doc__,
                       msg="Murphy docstring is None")
    assert_true(murphy.__doc__.strip(),
                msg="Muphy docstring is blank")


def test_arghandler_docstring():
    from murphy import arghandler
    assert_is_not_none(arghandler.__doc__,
                       msg="Arghandler docstring is None")
    assert_true(arghandler.__doc__.strip(),
                msg="Arghandler docstring is blank")


def test_attributehandler_docstring():
    from murphy import attributehandler
    assert_is_not_none(attributehandler.__doc__,
                       msg="Attributehandler docstring is None")
    assert_true(attributehandler.__doc__.strip(),
                msg="Attributehandler docstring is blank")


def test_parsegtf_docstring():
    from murphy import parsegtf
    assert_is_not_none(parsegtf.__doc__,
                       msg="Parsegtf docstring is None")
    assert_true(parsegtf.__doc__.strip(),
                msg="Parsegtf docstring is blank")


def test_intervaltree_docstring():
    from murphy.Tree import intervalTree
    assert_is_not_none(intervalTree.__doc__,
                       msg="intervalTree docstring is None")
    assert_true(intervalTree.__doc__.strip(),
                msg="intervalTree docstring is blank")
