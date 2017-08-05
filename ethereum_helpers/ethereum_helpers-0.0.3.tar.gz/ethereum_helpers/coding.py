import codecs
import string
from functools import partial
from typing import Union

characters_by_bases = {
    2: '01',
    8: string.octdigits,
    10: string.digits,
    16: string.digits + 'abcdef',
    32: string.ascii_lowercase + '234567',
    58: '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    256: ''.join(map(chr, range(256)))
}


def encode_number(number: int,
                  *,
                  base: int,
                  min_length: int) -> bytes:
    characters = characters_by_base(base)
    result = bytes()
    while number > 0:
        character = characters[number % base]
        result = bytes([ord(character)]) + result
        number //= base

    pad_size = min_length - len(result)

    padding_element = b'\x00' if base == 256 else b'1' if base == 58 else b'0'
    if pad_size > 0:
        result = padding_element * pad_size + result

    return result


def decode_number(bytes_or_string: Union[str, bytes],
                  *,
                  base: int) -> int:
    if base == 16:
        bytes_or_string = bytes_or_string.lower()

    if base == 256 and isinstance(bytes_or_string, str):
        bytes_or_string = bytes(bytearray.fromhex(bytes_or_string))

    if base == 256:
        def position(byte: int) -> int:
            return byte
    else:
        characters = characters_by_base(base)
        characters_positions = {position: character
                                for (position,
                                     character) in enumerate(characters)}

        def position(byte_or_character: Union[int, str]) -> int:
            char = (byte_or_character
                    if isinstance(byte_or_character, str)
                    else chr(byte_or_character))
            return characters_positions[char]

    result = 0
    for byte_or_character in bytes_or_string:
        result *= base
        result += position(byte_or_character)
    return result


def characters_by_base(base: int) -> str:
    try:
        return characters_by_bases[base]
    except KeyError:
        raise ValueError(f'Invalid base: {base}.')


def hex_string_to_int(hex_string: str) -> int:
    return int(hex_string, 16)


def big_endian_to_int(big_endian: bytes) -> int:
    return int.from_bytes(big_endian.lstrip(bytes([0])),
                          byteorder='big')


decode_hex = partial(codecs.decode,
                     encoding='hex')
