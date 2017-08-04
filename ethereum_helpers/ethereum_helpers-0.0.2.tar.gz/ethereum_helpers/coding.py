import codecs
import string
from functools import partial

codes_by_bases = {
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
    codes = codes_by_base(base)
    result = bytes()
    while number > 0:
        code = codes[number % base]
        result = bytes([ord(code)]) + result
        number //= base

    pad_size = min_length - len(result)

    padding_element = b'\x00' if base == 256 else b'1' if base == 58 else b'0'
    if pad_size > 0:
        result = padding_element * pad_size + result

    return result


def decode_number(text: str,
                  *,
                  base: int) -> int:
    if base == 16:
        text = text.lower()

    if base == 256 and isinstance(text, str):
        text = bytes(bytearray.fromhex(text))

    if base == 256:
        def extract(byte: int) -> int:
            return byte
    else:
        codes = codes_by_base(base)
        codes_positions = {position: code
                           for position, code in enumerate(codes)}

        def extract(char_or_byte: int) -> int:
            char = (char_or_byte
                    if isinstance(char_or_byte, str)
                    else chr(char_or_byte))
            return codes_positions[char]

    result = 0
    for char_or_byte in text:
        result *= base
        result += extract(char_or_byte)
    return result


def codes_by_base(base: int) -> str:
    try:
        return codes_by_bases[base]
    except KeyError:
        raise ValueError(f'Invalid base: {base}.')


def hex_string_to_int(hex_string: str) -> int:
    return int(hex_string, 16)


def big_endian_to_int(big_endian: bytes) -> int:
    return int.from_bytes(big_endian.lstrip(bytes([0])),
                          byteorder='big')


decode_hex = partial(codecs.decode,
                     encoding='hex')
