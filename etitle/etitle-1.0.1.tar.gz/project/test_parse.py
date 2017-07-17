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

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
SAMPLE_ROOT = os.path.join(CURRENT_PATH, 'sample')
ITEM01_PATH = os.path.join(SAMPLE_ROOT, 'item01.txt')
MANIFEST_PATH = os.path.join(SAMPLE_ROOT, '.manifest')

basic_test = {
    "file": os.path.join(SAMPLE_ROOT, '{=s.=b. }smith/lectures/{On the }2nd Person;2nd=person;mathematics;psychology.txt'),
    "path_expected": 'smith/lectures/2ndperson',
    "branch_expected": 'smith',
    "branch_title_expected":  'S. B. Smith',
    "title_expected": 'On the 2nd Person',
    "labels": ['smith', '2ndperson', 'mathematics', 'psychology']
}

special_character_test1 = {
    "file": os.path.join(SAMPLE_ROOT, 'billy {_of=chicago}/{%quotes%}inner{%quotes% and %quotes%}outer{%quotes% of }Psychological Analysis.txt'),
    "path_expected": 'billy/innerouterpsychologicalanalysis',
    "branch_expected": 'billy',
    "branch_title_expected":  'Billy of Chicago',
    "title_expected": '"inner" and "outer" of Psychological Analysis',
    "labels": ['billy']
}

special_character_test2 = {
    "file": os.path.join(SAMPLE_ROOT, 'billy {_of=chicago}/Section 5{%colon%}10{%colon% Behavior for }Introspection.txt'),
    "path_expected": 'billy/section510introspection',
    "branch_expected": 'billy',
    "branch_title_expected":  'Billy of Chicago',
    "title_expected": 'Section 5:10: Behavior for Introspection',
    "labels": ['billy']
}

fairly_boring_test = {
    "file": os.path.join(SAMPLE_ROOT, 'billy {_of=chicago}/{The Importance of} Continual Regression Analysis;mathematics.txt'),
    "path_expected": 'billy/continualregressionanalysis',
    "branch_expected": 'billy',
    "branch_title_expected":  'Billy of Chicago',
    "title_expected": 'The Importance of Continual Regression Analysis',
    "labels": ['billy', 'mathematics']
}

branch_casing_test = {
    "file": os.path.join(SAMPLE_ROOT, 'james==king/Topological Analysis;mathematics.txt'),
    "path_expected": 'king/topologicalanalysis',
    "branch_expected": 'king',
    "branch_title_expected":  'James King',
    "title_expected": 'Topological Analysis',
    "labels": ['king', 'mathematics']
}

exceptions_in_branch_test = {
    "file": os.path.join(SAMPLE_ROOT, 's{cott }james/{What is }Illustrative{ and Analytic Economics%questionmark%}.txt'),
    "path_expected": 'sjames/illustrative',
    "branch_expected": 'sjames',
    "branch_title_expected":  'Scott James',
    "title_expected": 'What is Illustrative and Analytic Economics?',
    "labels": ['sjames']
}

labelmode_branch_test = {
    "file": os.path.join(SAMPLE_ROOT, '{=s.=b. }smith/lectures/{On the }2nd Person;2nd=person;mathematics;psychology.txt'),
    "path_expected": 'smith/lectures/2ndperson',
    "branch_expected": 'smith',
    "branch_title_expected":  'S. B. Smith',
    "title_expected": 'On the 2nd Person',
    "labels": ['smith/lectures', '2ndperson', 'mathematics', 'psychology']
}

labelmode_each_test = {
    "file": os.path.join(SAMPLE_ROOT, '{=s.=b. }smith/lectures/{On the }2nd Person;2nd=person;mathematics;psychology.txt'),
    "path_expected": 'smith/lectures/2ndperson',
    "branch_expected": 'smith',
    "branch_title_expected":  'S. B. Smith',
    "title_expected": 'On the 2nd Person',
    "labels": ['smith', 'lectures', '2ndperson', 'mathematics', 'psychology']
}

labelmode_explicit_test = {
    "file": os.path.join(SAMPLE_ROOT, '{=s.=b. }smith/lectures/{On the }2nd Person;2nd=person;mathematics;psychology.txt'),
    "path_expected": 'smith/lectures/2ndperson',
    "branch_expected": 'smith',
    "branch_title_expected":  'S. B. Smith',
    "title_expected": 'On the 2nd Person',
    "labels": ['2ndperson', 'mathematics', 'psychology']
}

title_test = {
    "file": os.path.join(SAMPLE_ROOT, 's{cott }james/fundamental-process-of-behavior.txt'),
    "path_expected": 'sjames/fundamental-process-of-behavior',
    "branch_expected": 'sjames',
    "branch_title_expected":  'Scott James',
    "title_expected": 'Fundamental Process of Behavior',
    "labels": ['sjames']
}

title_single_relative_test = {
    "file": os.path.join(SAMPLE_ROOT, 's{cott }james/$ - cv.txt'),
    "path_expected": 'sjames/cv',
    "branch_expected": 'sjames',
    "branch_title_expected":  'Scott James',
    "title_expected": 'Curriculum Vitae',
    "labels": ['sjames']
}

title_single_override_test = {
    "file": os.path.join(SAMPLE_ROOT, 's{cott }james/$ - resume.txt'),
    "path_expected": 'sjames/resume',
    "branch_expected": 'sjames',
    "branch_title_expected":  'Scott James',
    "title_expected": 'Résumé',
    "labels": ['sjames']
}

class TestApp(unittest.TestCase):
    def check(self, item, result):
        selector, branch, title, branch_title, labels = result
        self.assertEqual(selector, item['path_expected'])
        self.assertEqual(branch, item['branch_expected'])
        self.assertEqual(branch_title, item['branch_title_expected'])
        self.assertEqual(title, item['title_expected'])
        self.assertEqual(len(labels), len(item['labels']))
        for v in item['labels']:
            self.assertTrue(v in labels)

    def test_passargs(self):
        SELECTOR = 'taco'
        BRANCH = 'elephant'

        def check(*args):
            selector, branch = args
            self.assertEqual(selector, SELECTOR)
            self.assertEqual(branch, BRANCH)

        check(SELECTOR, BRANCH)

    def test_root_default_labelMode(self):
        self.check(basic_test, etitle.parse(basic_test['file'], SAMPLE_ROOT))

    def test_branch_labelMode(self):
        self.check(labelmode_branch_test, etitle.parse(labelmode_branch_test['file'], SAMPLE_ROOT, { "labelMode": 'branch'} ))

    def test_each_labelMode(self):
        self.check(labelmode_each_test, etitle.parse(labelmode_each_test['file'], SAMPLE_ROOT, { "labelMode": 'each'} ))

    def test_explicit_labelMode(self):
        self.check(labelmode_explicit_test, etitle.parse(labelmode_explicit_test['file'], SAMPLE_ROOT, { "labelMode": 'explicit'} ))

    def test_special_characters(self):
        self.check(special_character_test1, etitle.parse(special_character_test1['file'], SAMPLE_ROOT))

    def test_more_special_characters(self):
        self.check(special_character_test2, etitle.parse(special_character_test2['file'], SAMPLE_ROOT))

    def test_branch_casing(self):
        self.check(branch_casing_test, etitle.parse(branch_casing_test['file'], SAMPLE_ROOT))

    def test_root_titles(self):
        v = etitle.parse_using_title_data(title_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True } )
        self.check(title_test, v)

    def test_root_titles_with_wrong_allowHyphensInSelector_setting(self):
        v = etitle.parse_using_title_data(title_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": False } )
        selector, branch, title, branch_title, labels = v
        self.assertNotEqual(selector, title_test['path_expected'])

    def test_relative_titles(self):
        v = etitle.parse_using_title_data(title_single_relative_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True } )
        self.check(title_single_relative_test, v)

    def test_relative_override_titles(self):
        v = etitle.parse_using_title_data(title_single_override_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True } )
        self.check(title_single_override_test, v)

    def test_root_titles_sync(self):
        self.check(title_test, etitle.parse_using_title_data(title_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True } ))

    def test_root_titles_with_wrong_allowHyphensInSelector_setting_sync(self):
        selector, branch, title, branch_title, labels = etitle.parse_using_title_data(title_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": False } )
        self.assertNotEqual(selector, title_test['path_expected'])

    def test_relative_titles_sync(self):
        self.check(title_single_relative_test, etitle.parse_using_title_data(title_single_relative_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True} ))

    def test_relative_override_titles_sync(self):
        self.check(title_single_override_test, etitle.parse_using_title_data(title_single_override_test['file'], SAMPLE_ROOT, { "allowHyphensInSelector": True} ))

    def test_with_provided_titles(self):
        options = {
            "allowHyphensInSelector": True,
            "titleData": [{
                "key": "sjames/fundamental-process-of-behavior",
                "title": "Fundamental Process of Behavior"
            }]
        }
        result = etitle.parse_using_title_data(title_test['file'], SAMPLE_ROOT, options)
        self.check(title_test, result)

    def test_exceptions_in_branch(self):
        self.check(exceptions_in_branch_test, etitle.parse(exceptions_in_branch_test['file'], SAMPLE_ROOT))

    def test_the_most_common_usage(self):
        self.check(fairly_boring_test, etitle.parse(fairly_boring_test['file'], SAMPLE_ROOT))


if __name__ == '__main__':
    unittest.main()
