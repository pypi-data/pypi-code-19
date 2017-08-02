"""
Base64 VLQ encoding and decoding routines.

This is different than MIDI VLQ encoding.  This encoding simply stores 5 bits of
data per character, least significant bytes first.

It also moves the sign bit to the LSB by:
* Take the absolute value
* Left shift by 1 to make room for the sign bit on the right
* Add the sign bit.
"""

from math import copysign

BASE64_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

VLQ_CONTINUATION = 0b100000
VLQ_VALUE_MASK   = 0b011111

def encode(fields):
    # For each number (field), break down into BASE64 characters.  Set the continuation bit for
    # each value except the final one.

    result = []
    for field in fields:
        n = ((field << 1) if field >= 0 else (-field << 1) + 1)
        while True:
            digit = n & VLQ_VALUE_MASK
            n >>= 5
            if n > 0:
                digit |= VLQ_CONTINUATION

            assert digit < len(BASE64_CHARS), 'invalid digit: digit=%s field=%s fields=%r' % (digit, field, fields)
            result.append(BASE64_CHARS[digit])

            if n == 0:
                break

    return ''.join(result)

def decode(segment):
    fields = []

    val   = 0
    shift = 0
    for ch in segment:
        n = BASE64_CHARS.index(ch)

        val += ((n & ~VLQ_CONTINUATION) << shift)
        shift += 5

        if (n & VLQ_CONTINUATION) == 0:
            # The LSB is the sign.  (I'm sure there is a good reason for this,
            # but it sure seems weird.)
            sign = val & 1
            val >>= 1
            if sign:
                val = -val
            fields.append(val)
            val = 0
            shift = 0

    assert shift == 0, 'Ended with a continuation bit?'
    assert len(fields) in (1,4,5)

    return fields
