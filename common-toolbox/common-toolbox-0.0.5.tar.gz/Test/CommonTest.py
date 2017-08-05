#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:27
# @Author  : Hou Rong
# @Site    : 
# @File    : CommonTest.py
# @Software: PyCharm
import unittest
from toolbox.Common import *


class TestCommon(unittest.TestCase):
    def test_dot_get(self):
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a.c'), '')
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a'), 2)

    def test_dot_get_multi(self):
        self.assertEqual(dot_get({'a': 2, 'b': {'a': 2}}, 'b.a.c', 'b.a'), 2)

    def test_i_do_not_care_list_or_dict(self):
        case = ['s', 'd', 'b']
        for index, res in enumerate(i_do_not_care_list_or_dict(case)):
            self.assertEqual(res, case[index])

        case = {'a': 123}
        for i in i_do_not_care_list_or_dict(case):
            self.assertDictEqual(i, case)

    def test_is_legal_false(self):
        self.assertEqual(is_legal(None), False)

    def test_is_legal_true(self):
        self.assertEqual(is_legal('test'), True)

    def test_key_modify(self):
        self.assertEqual(key_modify('  TeST  '), 'test')

    def test_is_chinese_true(self):
        self.assertEqual(is_chinese('我'), True)

    def test_is_chinese_false(self):
        self.assertEqual(is_chinese('a'), False)


if __name__ == '__main__':
    unittest.main()
