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

from glob import glob
from os import makedirs
from os.path import join

from mailman.config import config as mailman_config
from mailman.utilities.string import expand
from pgpy import PGPKeyring
from pgpy.constants import PubKeyAlgorithm
from public import public

from mailman_pgp.config import config

KEYDIR_CONFIG_PATHS = ['list_keydir', 'user_keydir', 'archive_keydir']
KEYPAIR_CONFIG_VARIABLES = ['autogenerate', 'key_type', 'key_length',
                            'subkey_type', 'subkey_length']

# The main key needs to support signing.
KEYPAIR_KEY_TYPE_VALID = ['RSA', 'DSA', 'ECDSA']
# The subkey needs to support encryption.
KEYPAIR_SUBKEY_TYPE_VALID = ['RSA', 'ECDH']
KEYPAIR_TYPE_MAP = {
    'RSA': PubKeyAlgorithm.RSAEncryptOrSign,
    'DSA': PubKeyAlgorithm.DSA,
    'ECDSA': PubKeyAlgorithm.ECDSA,
    'ECDH': PubKeyAlgorithm.ECDH
}


@public
class PGP:
    def __init__(self):
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """
        Load [keypairs] and [keydirs] config sections. Expand paths in them.
        """
        # Get all the [keypairs] config variables.
        self.keypair_config = dict(
                (k, config.get('keypairs', k)) for k in
                KEYPAIR_CONFIG_VARIABLES)

        # Get and expand all [keydirs] config paths against Mailman's paths.
        self.keydir_config = dict(
                (k,
                 expand(config.get('keydirs', k), None, mailman_config.paths))
                for k in KEYDIR_CONFIG_PATHS)

    def _validate_config(self):
        """
        Validate [keypairs] and [keydirs] config sections. And create
        keydirs if necessary.
        """
        # Validate keypair config.
        key_type = self.keypair_config['key_type'].upper()
        if key_type not in KEYPAIR_KEY_TYPE_VALID:
            raise ValueError('Invalid key_type. {}'.format(key_type))
        self.keypair_config['key_type'] = KEYPAIR_TYPE_MAP[key_type]
        self.keypair_config['key_length'] = int(
                self.keypair_config['key_length'])

        subkey_type = self.keypair_config['subkey_type'].upper()
        if subkey_type not in KEYPAIR_SUBKEY_TYPE_VALID:
            raise ValueError('Invalid subkey_type. {}'.format(subkey_type))
        self.keypair_config['subkey_type'] = KEYPAIR_TYPE_MAP[subkey_type]
        self.keypair_config['subkey_length'] = int(
                self.keypair_config['subkey_length'])

        # Make sure the keydir paths are directories and exist.
        for keydir in self.keydir_config.values():
            # TODO set a strict mode here
            makedirs(keydir, exist_ok=True)

    def _keyring(self, keydir):
        directory = self.keydir_config[keydir]
        return PGPKeyring(*glob(join(directory, '*.asc')))

    @property
    def list_keyring(self):
        return self._keyring('list_keydir')

    @property
    def user_keyring(self):
        return self._keyring('user_keydir')

    @property
    def archive_keyring(self):
        return self._keyring('archive_keydir')
