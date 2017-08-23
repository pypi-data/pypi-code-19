# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

""""""
import unittest

from mailman_pgp.config.config import Config
from mailman_pgp.config.converter import ConfigConverter
from mailman_pgp.testing.layers import PGPLayer


class TestConverter(unittest.TestCase):
    layer = PGPLayer

    def test_builtins(self):
        schema = """\
        [test]
        test_option: int
        """
        converter = ConfigConverter(schema)
        valid = Config()
        valid.read_string("""\
        [test]
        test_option: 5
        """)
        invalid = Config()
        invalid.read_string("""\
        [test]
        test_option: xyz
        """)
        out = converter.convert(valid)
        self.assertEqual(out['test']['test_option'], 5)
        self.assertRaises(ValueError, converter.convert, invalid)

    def test_callable(self):
        schema = """\
        [test]
        test_option: lazr.config.as_boolean
        """
        converter = ConfigConverter(schema)
        valid = Config()
        valid.read_string("""\
        [test]
        test_option: yes
        """)
        invalid = Config()
        invalid.read_string("""\
        [test]
        test_option: xyz
        """)
        out = converter.convert(valid)
        self.assertEqual(out['test']['test_option'], True)
        self.assertRaises(ValueError, converter.convert, invalid)

    def test_regex(self):
        schema = """\
        [test]
        test_option: 29*4
        """
        converter = ConfigConverter(schema)
        valid = Config()
        valid.read_string("""\
        [test]
        test_option: 2999999994
        """)
        invalid = Config()
        invalid.read_string("""\
        [test]
        test_option: xyz
        """)
        out = converter.convert(valid)
        self.assertEqual(out['test']['test_option'], '2999999994')
        self.assertRaises(ValueError, converter.convert, invalid)

    def test_none(self):
        schema = """\
        [test]
        test_option:
        """
        converter = ConfigConverter(schema)
        cfg = Config()
        cfg.read_string("""\
        [test]
        test_option: something
        """)
        self.assertRaises(ValueError, converter.convert, cfg)
