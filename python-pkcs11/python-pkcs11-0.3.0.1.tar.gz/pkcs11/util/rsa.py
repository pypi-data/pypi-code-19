"""
Key handling utilities for RSA keys (PKCS#1).

These utilities depend on :mod:`pyasn1` and :mod:`pyasn1_modules`.
"""

from pyasn1.codec.der import encoder, decoder
from pyasn1_modules.rfc2437 import RSAPrivateKey, RSAPublicKey

from . import biginteger
from ..constants import Attribute, ObjectClass, MechanismFlag
from ..mechanisms import KeyType
from ..defaults import DEFAULT_KEY_CAPABILITIES


def decode_rsa_private_key(der, capabilities=None):
    """
    Decode a RFC2437 (PKCS#1) DER-encoded RSA private key into a dictionary of
    attributes able to be passed to :meth:`pkcs11.Session.create_object`.

    :param bytes der: DER-encoded key
    :param MechanismFlag capabilities: Optional key capabilities
    :rtype: dict(Attribute,*)
    """
    if capabilities is None:
        capabilities = DEFAULT_KEY_CAPABILITIES[KeyType.RSA]

    key, _ = decoder.decode(der, asn1Spec=RSAPrivateKey())
    return {
        Attribute.CLASS: ObjectClass.PRIVATE_KEY,
        Attribute.KEY_TYPE: KeyType.RSA,
        Attribute.MODULUS: biginteger(key['modulus']),
        Attribute.PUBLIC_EXPONENT: biginteger(key['publicExponent']),
        Attribute.PRIVATE_EXPONENT: biginteger(key['privateExponent']),
        Attribute.PRIME_1: biginteger(key['prime1']),
        Attribute.PRIME_2: biginteger(key['prime2']),
        Attribute.EXPONENT_1: biginteger(key['exponent1']),
        Attribute.EXPONENT_2: biginteger(key['exponent2']),
        Attribute.COEFFICIENT: biginteger(key['coefficient']),
        Attribute.DECRYPT: MechanismFlag.DECRYPT in capabilities,
        Attribute.SIGN: MechanismFlag.SIGN in capabilities,
        Attribute.UNWRAP: MechanismFlag.UNWRAP in capabilities,
    }


def decode_rsa_public_key(der, capabilities=None):
    """
    Decode a RFC2437 (PKCS#1) DER-encoded RSA public key into a dictionary of
    attributes able to be passed to :meth:`pkcs11.Session.create_object`.

    :param bytes der: DER-encoded key
    :param MechanismFlag capabilities: Optional key capabilities
    :rtype: dict(Attribute,*)
    """

    if capabilities is None:
        capabilities = DEFAULT_KEY_CAPABILITIES[KeyType.RSA]

    key, _ = decoder.decode(der, asn1Spec=RSAPublicKey())
    return {
        Attribute.CLASS: ObjectClass.PUBLIC_KEY,
        Attribute.KEY_TYPE: KeyType.RSA,
        Attribute.MODULUS: biginteger(key['modulus']),
        Attribute.PUBLIC_EXPONENT: biginteger(key['publicExponent']),
        Attribute.ENCRYPT: MechanismFlag.ENCRYPT in capabilities,
        Attribute.VERIFY: MechanismFlag.VERIFY in capabilities,
        Attribute.WRAP: MechanismFlag.WRAP in capabilities,
    }


def encode_rsa_public_key(key):
    """
    Encode an RSA public key into PKCS#1 DER-encoded format.

    :param PublicKey key: RSA public key
    :rtype: bytes
    """
    asn1 = RSAPublicKey()
    asn1['modulus'] = int.from_bytes(key[Attribute.MODULUS],
                                     byteorder='big')
    asn1['publicExponent'] = int.from_bytes(key[Attribute.PUBLIC_EXPONENT],
                                            byteorder='big')
    return encoder.encode(asn1)
