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

"""Miscellaneous PGP utilities."""
from pgpy import PGPKey, PGPSignature
from pgpy.constants import SignatureType
from pgpy.errors import PGPError
from pgpy.packet import Packet, Signature
from pgpy.types import Armorable
from public import public


@public
def verifies(verifications):
    """

    :param verifications:
    :type verifications: typing.Sequence[pgpy.types.SignatureVerification]
    :return: bool
    """
    return all(bool(verification) and
               all(not sigsubj.signature.is_expired
                   for sigsubj in verification.good_signatures) for
               verification in verifications)


@public
def hashes(verifications):
    """

    :param verifications:
    :return:
    :rtype: typing.Generator[bytes]
    """
    for verification in verifications:
        for sigsubj in verification.good_signatures:
            data = sigsubj.signature.hashdata(sigsubj.subject)
            hasher = sigsubj.signature.hash_algorithm.hasher
            hasher.update(data)
            yield hasher.digest()


@public
def key_from_blob(blob):
    """

    :param blob:
    :return:
    :rtype: pgpy.PGPKey
    """
    key, _ = PGPKey.from_blob(blob)
    return key


@public
def key_from_file(file):
    """

    :param file:
    :return:
    :rtype: pgpy.PGPKey
    """
    key, _ = PGPKey.from_file(file)
    return key


@public
def revoc_from_blob(blob):
    """
    Load a key revocation signature from an ASCII-Armored blob.

    :param blob:
    :return:
    :rtype: pgpy.PGPSignature
    """
    dearm = Armorable.ascii_unarmor(blob)
    p = Packet(dearm['body'])

    if not isinstance(p, Signature):
        raise ValueError('Not a key revocation signature.')
    if p.sigtype not in (SignatureType.KeyRevocation,
                         SignatureType.SubkeyRevocation):
        raise ValueError('Not a key revocation.')

    sig = PGPSignature()
    sig |= p
    return sig


@public
def key_flags(key):
    if key.is_expired:
        return set()
    for revoc in key.revocation_signatures:
        try:
            verified = key.verify(key, revoc)
        except PGPError:
            continue
        if bool(verified):
            return set()

    usage_flags = set()
    uids = (uid for uid in key.userids if uid.is_primary)
    uids = list(uids)
    if len(uids) == 0:
        uids = key.userids

    for uid in uids:
        revoked = False
        for sig in uid.signatures:
            if sig.type is not SignatureType.CertRevocation:
                continue
            if sig.signer == key.fingerprint.keyid:
                try:
                    verified = key.verify(uid, sig)
                except PGPError:
                    continue
                if bool(verified):
                    revoked = True
        if not revoked:
            usage_flags |= uid.selfsig.key_flags
            break

    for subkey in key.subkeys.values():
        if subkey.is_expired:
            continue

        valid = True
        for revoc in subkey.revocation_signatures:
            try:
                verified = key.verify(subkey, revoc)
            except PGPError:
                continue
            if bool(verified):
                valid = False
                break

        if valid:
            usage_flags |= subkey.usage_flags()
    return usage_flags


@public
def key_usable(key, flags_required):
    """
    Check that the `key` has the `flags_required` set of KeyFlags.

    Checks only non-expired, non-revoked key/subkeys. Validates revocations it
    can, so not those made with some other designated revocation key.

    :param key: The key to check.
    :type key: pgpy.PGPKey
    :param flags_required: The set of flags required.
    :type flags_required: set
    :return: Whether the key has the flags_required.
    :rtype: bool
    """
    if key.is_expired:
        return False
    for revoc in key.revocation_signatures:
        try:
            verified = key.verify(key, revoc)
        except PGPError:
            continue
        if bool(verified):
            return False
    return flags_required.issubset(key_flags(key))
