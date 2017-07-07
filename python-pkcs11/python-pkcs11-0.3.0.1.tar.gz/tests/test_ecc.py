"""
PKCS#11 Elliptic Curve Cryptography.
"""

import base64

from pyasn1_modules.rfc3279 import prime256v1

import pkcs11
from pkcs11 import Attribute, KeyType, KDF, Mechanism
from pkcs11.util.ec import (
    encode_named_curve_parameters,
    decode_ec_public_key,
    encode_ec_public_key,
    decode_ecdsa_signature,
)

from . import TestCase, requires


class ECCTests(TestCase):
    @requires(Mechanism.EC_KEY_PAIR_GEN, Mechanism.ECDSA)
    def test_sign_ecdsa(self):
        parameters = self.session.create_domain_parameters(KeyType.EC, {
            Attribute.EC_PARAMS: encode_named_curve_parameters(prime256v1)
        }, local=True)

        pub, priv = parameters.generate_keypair()

        mechanism = Mechanism.ECDSA
        data = b'HI BOB!'
        ecdsa = priv.sign(data, mechanism=mechanism)
        self.assertTrue(pub.verify(data, ecdsa, mechanism=mechanism))

    @requires(Mechanism.EC_KEY_PAIR_GEN, Mechanism.ECDH1_DERIVE)
    def test_derive_key(self):
        # DER encoded EC params from OpenSSL
        # openssl ecparam -out ec_param.der -name prime192v1
        ecparams = base64.b64decode(b'BggqhkjOPQMBAQ==')

        parameters = self.session.create_domain_parameters(KeyType.EC, {
            Attribute.EC_PARAMS: ecparams,
        }, local=True)
        alice_pub, alice_priv = parameters.generate_keypair()
        alice_value = alice_pub[Attribute.EC_POINT]

        bob_pub, bob_priv = parameters.generate_keypair()
        bob_value = bob_pub[Attribute.EC_POINT]

        self.assertNotEqual(alice_value, bob_value)

        alice_session = alice_priv.derive_key(
            KeyType.AES, 128,
            mechanism_param=(KDF.NULL, None, bob_value))

        bob_session = bob_priv.derive_key(
            KeyType.AES, 128,
            mechanism_param=(KDF.NULL, None, alice_value))

        iv = self.session.generate_random(128)
        crypttext = alice_session.encrypt('HI BOB!', mechanism_param=iv)
        plaintext = bob_session.decrypt(crypttext, mechanism_param=iv)
        self.assertEqual(plaintext, b'HI BOB!')

    @requires(Mechanism.ECDSA)
    def test_import_key_params(self):
        der = base64.b64decode("""
        MIICXDCCAc8GByqGSM49AgEwggHCAgEBME0GByqGSM49AQECQgH/////////////
        ////////////////////////////////////////////////////////////////
        /////////zCBngRCAf//////////////////////////////////////////////
        ///////////////////////////////////////8BEFRlT65YY4cmh+SmiGgtoVA
        7qLacluZsxXzuLSJkY7xCeFWGTlR7H6TexZSwL07sb8HNXPfiD0sNPHvRR/Ua1A/
        AAMVANCeiAApHLhTlsxnFzkyhKqg2mS6BIGFBADGhY4GtwQE6c2ePstmI5W0Qpxk
        gTkFP7Uh+CivYGtNPbqhS1537+dZKP4dwSei/6jeM0izwYVqQpv5fn4xwuW9ZgEY
        OSlqeJo7wARcil+0LH0b2Zj1RElXm0RoF6+9Fyc+ZiyX7nKZXvQmQMVQuQE/rQdh
        NTxwhqJywkCIvpR2n9FmUAJCAf//////////////////////////////////////
        ////+lGGh4O/L5Zrf8wBSPcJpdA7tcm4iZxHrrtvtx6ROGQJAgEBA4GGAAQBMLgt
        gTFBGr0f7YrWwZsCPpLxaUQvUKvz2C6ghiFmxc2EzBgxDY+ywnmG4T++EVZhJHTP
        eIOnVRcHXXivkRe+YMQBbH/fZyqfCe41vIl39bwhqli839AAj/WoxXZuilpKaXBp
        vGbx2380UIhrec1jFjItOOg/Xp9dOecjQZK7Z0wVq1U=
        """)
        key = self.session.create_object(decode_ec_public_key(der))
        self.assertIsInstance(key, pkcs11.PublicKey)

        # We should get back to identity
        self.assertEqual(encode_ec_public_key(key), der)

    @requires(Mechanism.ECDSA_SHA1)
    def test_import_key_named_curve(self):
        der = base64.b64decode("""
        MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEa6Q5Hs+j71J1lc+VziafH+uL6603
        R8gTAphQD0iLG9Q9RgAvDQdFFpzkvXI+mEGVNRMmT/BA1OtficHcAXTdXA==
        """)
        key = self.session.create_object(decode_ec_public_key(der))
        self.assertIsInstance(key, pkcs11.PublicKey)

        # Something signed with OpenSSL
        signature = base64.b64decode("""
        MEYCIQD1nDlli+uLuGX3eobKJe7PsRYkYJ4F15bjqbbB+MHewwIhAPGFRwyuFOvH
        zuj+sxXwk1CsDWN7AXbmHufOlOarXpiq
        """)
        signature = decode_ecdsa_signature(signature)

        self.assertTrue(key.verify(b'Data to sign', signature,
                                   mechanism=Mechanism.ECDSA_SHA1))

        # We should get back to identity
        self.assertEqual(encode_ec_public_key(key), der)
