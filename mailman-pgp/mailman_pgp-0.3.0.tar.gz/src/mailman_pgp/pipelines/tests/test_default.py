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

import unittest

from mailman_pgp.config import mm_config
from mailman_pgp.handlers.signature_strip import SignatureStrip
from mailman_pgp.pipelines.default import PGPPostingPipeline
from mailman_pgp.testing.layers import PGPConfigLayer


class TestPGPPostingPipeline(unittest.TestCase):
    layer = PGPConfigLayer

    def test_has_pipeline(self):
        self.assertIn(PGPPostingPipeline.name, mm_config.pipelines.keys())

    def test_has_handler(self):
        pipeline = PGPPostingPipeline()
        self.assertEqual(SignatureStrip, type(next(iter(pipeline))))
