# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni.
from unittest import TestCase

from pydenji._annotate import makeAnnotation

class Any(object):
    pass

class TestAnnotation(TestCase):
    def setUp(self):
        self.annotation, self.is_annotated = makeAnnotation("myname", "myprefix_")

    def test_annotated_object_is_set_with_prefix_and_name(self):
        o = self.annotation(Any())
        self.assertTrue(o.myprefix_myname)

    def test_annotated_object_can_be_checked_with_is_annotated(self):
        o = self.annotation(Any())
        self.assertTrue(self.is_annotated(o))

  
    def test_unannotated_object_returns_false_on_check(self):
        o = Any()
        self.assertFalse(self.is_annotated(o))