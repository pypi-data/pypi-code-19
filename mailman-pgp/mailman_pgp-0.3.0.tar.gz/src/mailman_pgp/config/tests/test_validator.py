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
from mailman_pgp.config.validator import ConfigValidator
from mailman_pgp.testing.layers import PGPLayer


class TestValidator(unittest.TestCase):
    layer = PGPLayer

    def test_missing_section(self):
        schema = """\
        [test]
        test_option: something
        """
        validator = ConfigValidator(schema)
        cfg = Config()
        cfg.read_string("""\
        [other_section]
        some_option: something else
        """)
        self.assertRaises(ValueError, validator.validate, cfg)

    def test_additional_section(self):
        schema = """\
        [test]
        test_option: something
        """
        validator = ConfigValidator(schema)
        cfg = Config()
        cfg.read_string("""\
        [test]
        test_option: something
        [other_section]
        some_option: something else
        """)
        self.assertRaises(ValueError, validator.validate, cfg)

    def test_missing_option(self):
        schema = """\
        [test]
        test_option: something
        """
        validator = ConfigValidator(schema)
        cfg = Config()
        cfg.read_string("""\
        [test]
        """)
        self.assertRaises(ValueError, validator.validate, cfg)

    def test_additional_option(self):
        schema = """\
        [test]
        test_option: something
        """
        validator = ConfigValidator(schema)
        cfg = Config()
        cfg.read_string("""\
        [test]
        test_option: something
        other_option: something else
        """)
        self.assertRaises(ValueError, validator.validate, cfg)
