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
import contextlib
import os
from os.path import isfile

from mailman.testing.layers import (ConfigLayer, RESTLayer, SMTPLayer)

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.model.base import Base


def reset_rollback():
    config.db.session.rollback()


def reset_pgp_dirs():
    for keydir in (config.pgp.keydir_config.values()):
        for path in os.listdir(keydir):
            full_path = os.path.join(keydir, path)
            if isfile(full_path):
                os.remove(full_path)


def reset_pgp_hard():
    reset_rollback()
    reset_pgp_dirs()
    with transaction():
        Base.metadata.drop_all(config.db.engine)
        Base.metadata.create_all(config.db.engine)


def reset_pgp_soft():
    reset_rollback()
    reset_pgp_dirs()
    with contextlib.closing(config.db.engine.connect()) as con:
        trans = con.begin()
        for table in reversed(Base.metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


# It's weird that ws have to do this, but for some reason nose2 test layers
# don't work when ws create a mixin class with the two classmethods
# and subclass both it and the respective Mailman Core test layer.
class PGPConfigLayer(ConfigLayer):
    @classmethod
    def setUp(cls):
        config.set('keypairs', 'autogenerate', 'no')

    @classmethod
    def tearDown(cls):
        reset_pgp_soft()

    @classmethod
    def testTearDown(cls):
        reset_pgp_soft()


class PGPMigrationLayer(ConfigLayer):
    @classmethod
    def tearDown(cls):
        reset_pgp_hard()

    @classmethod
    def testTearDown(cls):
        reset_pgp_hard()


class PGPSMTPLayer(SMTPLayer):
    @classmethod
    def tearDown(cls):
        reset_pgp_soft()

    @classmethod
    def testTearDown(cls):
        reset_pgp_soft()


class PGPRESTLayer(RESTLayer):
    @classmethod
    def tearDown(cls):
        reset_pgp_soft()

    @classmethod
    def testTearDown(cls):
        reset_pgp_soft()
