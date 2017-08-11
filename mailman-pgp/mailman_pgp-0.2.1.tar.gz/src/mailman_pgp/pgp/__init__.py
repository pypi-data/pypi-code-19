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

from pgpy import PGPKeyring
from public import public

from mailman_pgp.config import config
from mailman_pgp.utils.config import key_spec


@public
class PGP:
    def __init__(self):
        self.primary_key_args = key_spec(
            config.get_value('keypairs', 'primary_key'))
        self.sub_key_args = key_spec(config.get_value('keypairs', 'sub_key'))
        # Make sure the keydir paths are directories and exist.
        self.keydirs = {keydir_name: config.get_value('keydirs', keydir_name)
                        for keydir_name in config.options('keydirs')}

        for keydir_path in self.keydirs.values():
            # TODO set a strict mode here
            keydir_path.mkdir(parents=True, exist_ok=True)

    def _keyring(self, keydir):
        directory = self.keydirs[keydir]
        return PGPKeyring(*map(str, directory.glob('*.asc')))

    @property
    def list_keyring(self):
        return self._keyring('list_keydir')

    @property
    def user_keyring(self):
        return self._keyring('user_keydir')

    @property
    def archive_keyring(self):
        return self._keyring('archive_keydir')
