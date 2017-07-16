""" Import Tests
"""
from nose.tools import assert_true


def test_import_murphy():
    import murphy
    assert_true(murphy, msg="Failed to import murphy")


def test_import_attributehandler():
    from murphy import attributehandler
    assert_true(attributehandler, msg="Failed to import attributehandler")


def test_import_parsegtf():
    from murphy import parsegtf
    assert_true(parsegtf, msg="Failed to import parsegtf")


def test_import_arghandler():
    from murphy import arghandler
    assert_true(arghandler, msg="Failed to import arghandler")


def test_import_intervaltree():
    from murphy.Tree import intervalTree
    assert_true(intervalTree, msg="Failed to import intervalTree")
