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
def expired(verifications):
    """

    :param verifications:
    :return:
    """
    return any(any(sigsubj.signature.is_expired or sigsubj.by.is_expired
                   for sigsubj in verification.good_signatures)
               for verification in verifications)


@public
def revoked(verifications):
    """

    :param verifications:
    :return:
    """
    return any(any(key_revoked(sigsubj.by)
                   for sigsubj in verification.good_signatures)
               for verification in verifications)


@public
def verifies(verifications):
    """

    :param verifications:
    :type verifications: typing.Sequence[pgpy.types.SignatureVerification]
    :return: bool
    """
    return all(bool(verification) and
               all(not sigsubj.signature.is_expired
                   for sigsubj in verification.good_signatures)
               for verification in verifications)


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
def key_revoked(key):
    """

    :param key:
    :type key: pgpy.PGPKey
    :return:
    :rtype: bool
    """
    if key.is_primary:
        verifier = key
    else:
        verifier = key.parent

    for revoc in key.revocation_signatures:
        try:
            verified = verifier.verify(key, revoc)
        except PGPError:
            continue
        if bool(verified):
            return True

    return False


@public
def key_flags(key):
    """

    :param key:
    :type key: pgpy.PGPKey
    :return:
    :rtype: Set[pgpy.constants.KeyFlags]
    """
    if key.is_expired:
        return set()
    if key_revoked(key):
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

        if not key_revoked(subkey):
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
    if key_revoked(key):
        return False
    return flags_required.issubset(key_flags(key))


@public
def key_merge(privkey, new_key, signer_key=None):
    """

    :param privkey:
    :type privkey: pgpy.PGPKey
    :param new_key:
    :type new_key: pgpy.PGPKey
    :param signer_key:
    :type signer_key: pgpy.PGPKey
    """
    if privkey.pubkey.key_material != new_key.key_material:
        raise ValueError('You sent a wrong key.')

    uid_map = {}
    for uid in privkey.userids:
        for uid_other in new_key.userids:
            if uid == uid_other:
                uid_map[uid] = uid_other

    if len(uid_map) == 0:
        raise ValueError('No signed UIDs found.')

    uid_sigs = {}
    for uid, uid_other in uid_map.items():
        for sig in uid_other.signatures:
            if sig in uid.signatures:
                continue
            if signer_key is None:
                uid_sigs.setdefault(uid, []).append(sig)
                continue
            if sig.signer != signer_key.fingerprint.keyid:
                continue
            # sig is a new signature, not currently on uid, and seems to
            # be made by the signer_key
            try:
                verification = signer_key.verify(uid, sig)
                if bool(verification):
                    uid_sigs.setdefault(uid, []).append(sig)
            except PGPError:
                pass

    if len(uid_sigs) == 0:
        raise ValueError('No new certifications found.')

    for uid, sigs in uid_sigs.items():
        for sig in sigs:
            uid |= sig
