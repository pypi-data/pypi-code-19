import codecs
import string
from functools import partial

code_strings = {
    2: '01',
    8: string.octdigits,
    10: string.digits,
    16: string.digits + 'abcdef',
    32: 'abcdefghijklmnopqrstuvwxyz234567',
    58: '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    256: ''.join(map(chr, range(256)))
}


def encode_number(number: int,
                  base: int,
                  min_length: int) -> bytes:
    try:
        code_string = code_strings[base]
    except KeyError:
        raise ValueError(f'Invalid base: {base}.')

    result = bytes()
    while number > 0:
        code = code_string[number % base]
        result = bytes([ord(code)]) + result
        number //= base

    pad_size = min_length - len(result)

    padding_element = b'\x00' if base == 256 else b'1' if base == 58 else b'0'
    if pad_size > 0:
        result = padding_element * pad_size + result

    return result


def hex_string_to_int(hex_string: str) -> int:
    return int(hex_string, 16)


def big_endian_to_int(big_endian: bytes) -> int:
    return int.from_bytes(big_endian.lstrip(bytes([0])),
                          byteorder='big')


decode_hex = partial(codecs.decode,
                     encoding='hex')
