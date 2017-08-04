from typing import (Union,
                    Dict,
                    Tuple)

from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter

from . import aes
from .coding import (big_endian_to_int,
                     decode_hex)
from .hashes import (keccak_256_hash,
                     scrypt_hash)


def decode_keystore_json(key_json: Dict[str, Union[str, int, dict]],
                         password: str) -> bytes:
    crypto = key_json['crypto']
    aes_key, mac_bytes_head = derived_key_parts(password=password,
                                                kdf_params=crypto['kdfparams'])
    cipher_text = decode_hex(crypto['ciphertext'])
    validate_mac(cipher_text=cipher_text,
                 mac_bytes_head=mac_bytes_head,
                 predicted_mac=decode_hex(crypto['mac']))

    cipher_params = crypto['cipherparams']
    initial_value = initial_value_str_to_int(string=cipher_params['iv'])
    counter = Counter.new(nbits=128,
                          initial_value=initial_value,
                          allow_wraparound=True)
    return aes.decrypt(text=cipher_text,
                       key=aes_key,
                       counter=counter,
                       mode=AES.MODE_CTR)


def derived_key_parts(*,
                      password: str,
                      kdf_params: Dict[str, Union[int, str]]
                      ) -> Tuple[bytes, bytes]:
    derived_key = scrypt_hash(password,
                              salt=decode_hex(kdf_params['salt']),
                              buffer_length=kdf_params['dklen'],
                              p=kdf_params['p'],
                              r=kdf_params['r'],
                              n=kdf_params['n'])
    if len(derived_key) < 32:
        raise ValueError('Derived key must be at least 32 bytes long')
    return derived_key[:16], derived_key[16:32]


def validate_mac(*,
                 cipher_text: bytes,
                 mac_bytes_head: bytes,
                 predicted_mac: bytes) -> None:
    mac_bytes = mac_bytes_head + cipher_text
    mac = keccak_256_hash(mac_bytes).digest()
    if mac != predicted_mac:
        raise ValueError('MAC mismatch. '
                         'Password seems to be incorrect.')


def initial_value_str_to_int(string: str) -> int:
    return big_endian_to_int(decode_hex(string))
