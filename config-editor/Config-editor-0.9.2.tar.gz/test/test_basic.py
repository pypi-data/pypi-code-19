#    Copyright 2017 Alexey Stepanov aka penguinolog

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# pylint: disable=missing-docstring

from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import fcntl
import json
import unittest

import six
from six.moves import configparser
import yaml

import config_editor

# pylint: disable=import-error
if six.PY2:
    # noinspection PyUnresolvedReferences
    import mock
else:
    # noinspection PyUnresolvedReferences
    from unittest import mock


class TestJson(unittest.TestCase):
    def setUp(self):
        self.original_value = ""
        self.new_value = {'New': True}
        self.stream = six.StringIO(json.dumps(self.original_value))

    def test_00_no_context(self):
        editor = config_editor.JsonEditor(self.stream)

        self.assertEqual(editor.content, self.original_value)
        self.assertEqual(editor.original_content, self.original_value)
        self.assertEqual(editor.text, json.dumps(self.original_value))
        self.assertFalse(editor.no_block)
        self.assertFalse(editor.lock_descriptor)
        self.assertTrue(editor.revert_on_exception)
        self.assertTrue(editor.ensure_ascii)
        self.assertTrue(editor.allow_nan)
        self.assertIsNone(editor.indent)
        self.assertFalse(editor.sort_keys)
        self.assertIsNone(editor.object_pairs_hook)

    def test_01_context_positive(self):
        with config_editor.JsonEditor(self.stream) as editor:
            self.assertEqual(editor.content, self.original_value)
            self.assertEqual(editor.text, json.dumps(self.original_value))

            editor.content = self.new_value
            self.assertEqual(editor.text, json.dumps(self.new_value))
            self.assertEqual(editor.original_content, self.original_value)

        self.stream.seek(0)
        self.assertEqual(self.stream.read(), json.dumps(self.new_value))

    def test_02_context_negative(self):
        with self.assertRaises(Exception):
            with config_editor.JsonEditor(self.stream) as editor:
                self.assertEqual(editor.content, self.original_value)
                self.assertEqual(editor.text, json.dumps(self.original_value))

                editor.content = self.new_value
                self.assertEqual(editor.text, json.dumps(self.new_value))

                raise Exception()

        self.stream.seek(0)
        self.assertEqual(self.stream.read(), json.dumps(self.original_value))

    def test_03_context_negative(self):
        with self.assertRaises(Exception):
            with config_editor.JsonEditor(
                self.stream,
                revert_on_exception=False
            ) as editor:
                self.assertEqual(editor.content, self.original_value)
                self.assertEqual(editor.text, json.dumps(self.original_value))

                editor.content = self.new_value
                self.assertEqual(editor.text, json.dumps(self.new_value))

                raise Exception()

        self.stream.seek(0)
        self.assertEqual(self.stream.read(), json.dumps(self.new_value))


class TestYaml(unittest.TestCase):
    def setUp(self):
        self.original_value = ""
        self.new_value = {'New': True}
        self.stream = six.StringIO(yaml.safe_dump(self.original_value))

    def test_00_no_context(self):
        editor = config_editor.YamlEditor(self.stream)

        self.assertEqual(editor.content, self.original_value)
        self.assertEqual(editor.text, yaml.safe_dump(self.original_value))
        self.assertFalse(editor.no_block)
        self.assertFalse(editor.lock_descriptor)
        self.assertTrue(editor.revert_on_exception)

        self.assertIsNone(editor.canonical)
        self.assertIsNone(editor.indent)
        self.assertIsNone(editor.width)
        self.assertIsNone(editor.allow_unicode)


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.original_value = collections.OrderedDict(
            section=collections.OrderedDict(option='value')
        )
        self.new_value = {'New': True}
        self.stream = six.StringIO()
        parser = configparser.ConfigParser()
        for section, content in self.original_value.items():
            parser.add_section(section)
            for option, value in content.items():
                parser.set(section, option, value)
        parser.write(self.stream)

    def test_00_no_context(self):
        editor = config_editor.ConfigEditor(self.stream)
        # tmp_io = six.StringIO()

        self.assertEqual(editor.content, self.original_value)
        self.stream.seek(0)
        self.assertEqual(editor.text, self.stream.read())
        self.assertFalse(editor.no_block)
        self.assertFalse(editor.lock_descriptor)
        self.assertTrue(editor.revert_on_exception)

        self.assertIsNone(editor.defaults)
        self.assertEqual(editor.dict_type, collections.OrderedDict)
        self.assertFalse(editor.allow_no_value)


class TestConversion(unittest.TestCase):
    def setUp(self):
        self.original_value = collections.OrderedDict(
            section=collections.OrderedDict(option='value')
        )

    def test_00_config_to_json(self):
        source_stream = six.StringIO()
        target_stream = six.StringIO('""')  # JSON does not allows empty
        parser = configparser.ConfigParser()
        for section, content in self.original_value.items():
            parser.add_section(section)
            for option, value in content.items():
                parser.set(section, option, value)
        parser.write(source_stream)

        src = config_editor.ConfigEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.JsonEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        target_stream.seek(0)
        self.assertEqual(
            target_stream.read(),
            json.dumps(self.original_value)
        )

    def test_01_config_to_yaml(self):
        source_stream = six.StringIO()
        target_stream = six.StringIO()
        parser = configparser.ConfigParser()
        for section, content in self.original_value.items():
            parser.add_section(section)
            for option, value in content.items():
                parser.set(section, option, value)
        parser.write(source_stream)

        src = config_editor.ConfigEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.YamlEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        target_stream.seek(0)
        self.assertEqual(
            target_stream.read(),
            yaml.safe_dump(self.original_value)
        )

    def test_02_json_to_config(self):
        source_stream = six.StringIO(json.dumps(self.original_value))
        expected_stream = six.StringIO()
        target_stream = six.StringIO()
        parser = configparser.ConfigParser()
        for section, content in self.original_value.items():
            parser.add_section(section)
            for option, value in content.items():
                parser.set(section, option, value)
        parser.write(expected_stream)

        src = config_editor.JsonEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.ConfigEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        expected_stream.seek(0)
        target_stream.seek(0)
        self.assertEqual(target_stream.read(), expected_stream.read())

    def test_03_yaml_to_config(self):
        source_stream = six.StringIO(yaml.safe_dump(self.original_value))
        expected_stream = six.StringIO()
        target_stream = six.StringIO()
        parser = configparser.ConfigParser()
        for section, content in self.original_value.items():
            parser.add_section(section)
            for option, value in content.items():
                parser.set(section, option, value)
        parser.write(expected_stream)

        src = config_editor.YamlEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.ConfigEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        expected_stream.seek(0)
        target_stream.seek(0)
        self.assertEqual(target_stream.read(), expected_stream.read())

    def test_04_json_to_yaml(self):
        source_stream = six.StringIO(json.dumps(self.original_value))
        target_stream = six.StringIO()

        src = config_editor.JsonEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.YamlEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        target_stream.seek(0)
        self.assertEqual(
            target_stream.read(),
            yaml.safe_dump(self.original_value)
        )

    def test_05_yaml_to_json(self):
        source_stream = six.StringIO(yaml.safe_dump(self.original_value))
        target_stream = six.StringIO('""')  # JSON does not allows empty

        src = config_editor.YamlEditor(source_stream).content
        self.assertEqual(src, self.original_value)
        with config_editor.JsonEditor(target_stream) as tgt_editor:
            tgt_editor.content = src

        target_stream.seek(0)
        self.assertEqual(
            target_stream.read(),
            json.dumps(self.original_value)
        )


@mock.patch('fcntl.lockf', autospec=True)
class TestLock(unittest.TestCase):
    def setUp(self, *args):
        self.original_value = ""
        self.new_value = {'New': True}
        self.stream = six.StringIO(json.dumps(self.original_value))

    def test_00_simple(self, fcntl_mock):
        with config_editor.JsonEditor(
            self.stream,
            lock_descriptor=True
        ) as editor:
            self.assertEqual(editor.content, self.original_value)
            self.assertEqual(editor.text, json.dumps(self.original_value))

        self.assertEqual(
            fcntl_mock.mock_calls,
            [
                mock.call(self.stream, fcntl.LOCK_EX),
                mock.call(self.stream, fcntl.LOCK_UN),
            ]
        )

    def test_01_nb(self, fcntl_mock):
        with config_editor.JsonEditor(
            self.stream,
            lock_descriptor=True,
            no_block=True
        ) as editor:
            self.assertEqual(editor.content, self.original_value)
            self.assertEqual(editor.text, json.dumps(self.original_value))

        self.assertEqual(
            fcntl_mock.mock_calls,
            [
                mock.call(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB),
                mock.call(self.stream, fcntl.LOCK_UN),
            ]
        )
