# -*- coding: utf-8 -*-

# MIT License
# Copyright (c) 2017 David Betz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

import os

try:
    import etitle
except:
    from . import etitle

class TestApp(unittest.TestCase):

    def test_create_selector(self):
         selector = etitle.create_selector('{=s.=b. }smith/lectures/{On the }2nd Person')
         self.assertEqual(selector,'smith/lectures/2ndperson')

    def test_create_selector_with_deepDot(self):
        selector = etitle.create_selector('mongodb/basic{=setup}/configure.sh', False, True)
        self.assertEqual(selector,'mongodb/basic/configure.sh')

    def test_create_selector_with_deepDot_but_not_set(self):
        selector = etitle.create_selector('mongodb/basic{=setup}/configure.sh', False, False)
        self.assertNotEqual(selector,'mongodb/basic/configure.sh')

    def test_create_selector_with_allowHyphensInSelector(self):
        selector = etitle.create_selector('s{cott }james/fundamental-process-of-behavior', True)
        self.assertEqual(selector,'sjames/fundamental-process-of-behavior')

    def test_create_selector(self):
        key = 's{cott }james'
        expected = 'sjames'
        self.assertEqual(etitle.create_selector(key, True), expected)

    def test_create_selector2(self):
        key = '{On the }2nd Person'
        expected = '2ndperson'
        self.assertEqual(etitle.create_selector(key), expected)

    def test_create_selector3(self):
        key = '{=s.=b. }smith/lectures'
        expected = 'smith/lectures'
        self.assertEqual(etitle.create_selector(key), expected)

    def test_create_selector4(self):
        key = 'fundamental-process-of-behavior'
        expected = 'fundamental-process-of-behavior'
        self.assertEqual(etitle.create_selector(key, True), expected)

    def test_create_selector5(self):
        key = 'fundamental-process-of-behavior'
        expected = 'fundamentalprocessofbehavior'
        self.assertEqual(etitle.create_selector(key, False), expected)

    def test_create_selector6(self):
        key = 'fundamental-process-of-behavior'
        expected = 'fundamentalprocessofbehavior'
        self.assertEqual(etitle.create_selector(key), expected)

    def test_create_effective_title_data(self):
        rootTitleData=[{'key': 'sjames/fundamental-process-of-behavior', 'title': 'Fundamental Process of Behavior'}, {'key': 'sjames/resume', 'title': "Resume (you won't see this; you will see the accented one)"}]
        relativeTitleData=[{'key': 'sjames/resume', 'title': 'Résumé'}, {'key': 'sjames/cv', 'title': 'Curriculum Vitae'}]
        key = 'fundamental-process-of-behavior'
        expected = [{'key': 'sjames/fundamental-process-of-behavior', 'title': 'Fundamental Process of Behavior'}, {'key': 'sjames/resume', 'title': 'Résumé'}, {'key': 'sjames/cv', 'title': 'Curriculum Vitae'}]
        self.assertEqual(etitle.create_effective_title_data(rootTitleData, relativeTitleData), expected)

    def test_transform_title_data(self):
        data = """sjames/fundamental-process-of-behavior, Fundamental Process of Behavior
sjames/resume, Resume (you won't see this; you will see the accented one)"""
        expected = [{'key': 'sjames/fundamental-process-of-behavior', 'title': 'Fundamental Process of Behavior'}, {'key': 'sjames/resume', 'title': "Resume (you won't see this; you will see the accented one)"}]
        self.assertEqual(etitle.transform_title_data(data), expected)

    def test_transform_title_data2(self):
        data = """sjames/resume, Résumé
sjames/cv, Curriculum Vitae"""
        expected = [{'key': 'sjames/resume', 'title': 'Résumé'}, {'key': 'sjames/cv', 'title': 'Curriculum Vitae'}]
        self.assertEqual(etitle.transform_title_data(data), expected)

    def test_clean(self):
        input = '/billy {_of=chicago}/{The Importance of} Continual Regression Analysis;mathematics.txt'
        expected = 'billy {_of=chicago}/{The Importance of} Continual Regression Analysis;mathematics.txt'
        self.assertEqual(etitle.clean(input), expected)

    def test_clean2(self):
        input = 'billy {_of=chicago}/'
        expected = 'billy {_of=chicago}'
        self.assertEqual(etitle.clean(input), expected)

    def test_process_selector(self):
        input = '/srv/etitle/content/project/sample/{=s.=b. }smith/lectures/{On the }2nd Person;2nd=person;mathematics;psychology.txt'
        base = '/srv/etitle/content/project/sample'
        options = {'labelMode': 'root'}
        expected = ('smith/lectures/2ndperson', 'smith', 'On the 2nd Person', 'S. B. Smith', ['2ndperson', 'mathematics', 'psychology', 'smith'])
        self.assertEqual(etitle.process_selector(input, base, options), expected)

    def test_process_selector2(self):
        input = '/srv/etitle/content/project/sample/s{cott }james/fundamental-process-of-behavior.txt'
        base = '/srv/etitle/content/project/sample'
        options = {'allowHyphensInSelector': True, 'titleData': [{'key': 'sjames/fundamental-process-of-behavior', 'title': 'Fundamental Process of Behavior'}, {'key': 'sjames/resume', 'title': 'R\xc3\xa9sum\xc3\xa9'}, {'key': 'sjames/cv', 'title': 'Curriculum Vitae'}], 'labelMode': 'root'}
        expected = ('sjames/fundamental-process-of-behavior', 'sjames', 'Fundamental Process of Behavior', 'Scott James', ['sjames'])
        self.assertEqual(etitle.process_selector(input, base, options), expected)

    def test_clean_title(self):
        key = 'sjames/cv'
        title = '$'
        titleData = [{'key': 'sjames/fundamental-process-of-behavior', 'title': 'Fundamental Process of Behavior'}, {'key': 'sjames/resume', 'title': 'Résumé'}, {'key': 'sjames/cv', 'title': 'Curriculum Vitae'}]
        expected = 'Curriculum Vitae'
        self.assertEqual(etitle.clean_title(key, title, titleData), expected)

    def test_clean_title2(self):
        key = 'smith/lectures/2ndperson'
        title = '{On the }2nd Person'
        titleData = None
        expected = 'On the 2nd Person'
        self.assertEqual(etitle.clean_title(key, title, titleData), expected)

    def test_get_key_and_title(self):
        path = '{The Importance of} Continual Regression Analysis;mathematics'
        expected = ['continualregressionanalysis', '{The Importance of} Continual Regression Analysis']
        self.assertEqual(etitle.get_key_and_title(path, ''), expected)

    def test_get_key_and_title2(self):
        path = 'fundamental-process-of-behavior'
        expected = ['fundamental-process-of-behavior', 'fundamental-process-of-behavior']
        self.assertEqual(etitle.get_key_and_title(path, True), expected)

    def test_remove_each_exception(self):
        text = 's{cott}james'
        expected = 'sjames'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_remove_each_exception2(self):
        text = 's{cott}james/cv'
        expected = 'sjames/cv'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_remove_each_exception3(self):
        text = '{onthe}2ndperson'
        expected = '2ndperson'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_remove_each_exception4(self):
        text = '{=s.=b.}smith/lectures'
        expected = 'smith/lectures'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_remove_each_exception5(self):
        text = '{=s.=b.}smith/lectures/2ndperson'
        expected = 'smith/lectures/2ndperson'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_remove_each_exception6(self):
        text = 'psychology'
        expected = 'psychology'
        self.assertEqual(etitle.remove_each_exception(text), expected)

    def test_format_branch_name(self):
        name = 's{cott }james'
        expected = 'Scott James'
        self.assertEqual(etitle.format_branch_name(name), expected)

    def test_format_branch_name2(self):
        name = '{=s.=b. }smith'
        expected = 'S. B. Smith'
        self.assertEqual(etitle.format_branch_name(name), expected)

    def test_format_branch_name2(self):
        name = 'billy {_of=chicago}'
        expected = 'Billy of Chicago'
        self.assertEqual(etitle.format_branch_name(name), expected)


if __name__ == '__main__':
    unittest.main()
