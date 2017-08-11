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
import pathlib

from mailman.utilities.string import expand
from pgpy.constants import EllipticCurveOID, PubKeyAlgorithm

from mailman_pgp.config import mm_config


def expandable_str(value):
    return expand(value, None, mm_config.paths)


def expandable_path(value):
    return pathlib.Path(expandable_str(value))


def key_spec(value):
    KEYPAIR_TYPE_MAP = {
        'RSA': PubKeyAlgorithm.RSAEncryptOrSign,
        'DSA': PubKeyAlgorithm.DSA,
        'ECDSA': PubKeyAlgorithm.ECDSA,
        'ECDH': PubKeyAlgorithm.ECDH
    }
    ECC_OID_MAP = {
        'nistp256': EllipticCurveOID.NIST_P256,
        'nistp384': EllipticCurveOID.NIST_P384,
        'nistp521': EllipticCurveOID.NIST_P521,
        'brainpoolP256r1': EllipticCurveOID.Brainpool_P256,
        'brainpoolP384r1': EllipticCurveOID.Brainpool_P384,
        'brainpoolP512r1': EllipticCurveOID.Brainpool_P512,
        'secp256k1': EllipticCurveOID.SECP256K1
    }
    key_type, key_length = value.split(':')
    key_type = key_type.upper()
    key_length = key_length.lower()

    if key_type not in KEYPAIR_TYPE_MAP:
        raise ValueError('Invalid key type: {}.'.format(key_type))

    out_type = KEYPAIR_TYPE_MAP[key_type]
    if key_type in ('ECDSA', 'ECDH'):
        if key_length not in ECC_OID_MAP:
            raise ValueError('Invalid key length: {}.'.format(key_length))
        out_length = ECC_OID_MAP[key_length]
    else:
        out_length = int(key_length)
    return (out_type, out_length)
