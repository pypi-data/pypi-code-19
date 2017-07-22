#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod
from copy import deepcopy as copy
from typing import Union

class Base_sha256(metaclass=ABCMeta):
    block_size = 64
    digest_size = 32
    name = 'sha256neon'
    _buffer = bytearray(b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U")
    
    def __init__(self, buf=None):
        """Returns a sha256 hash object; optionally initialized with a string"""
        if buf:
            self.update(buf)

    @abstractmethod
    def update(self, data) -> None:
        """Update this hash object's state with the provided string."""

    def copy(self) -> 'Base_sha256':
        """Return a copy of the hash object."""
        return copy(self)

    def hexdigest(self) -> str:
        """Return the digest value as a string of hexadecimal digits."""
        return self._buffer.hex()

    def digest(self) -> Union[bytes, bytearray]:
        """Return the digest value as a string of binary data."""
        return self._buffer
                         
class sha256_neon(Base_sha256):
    def update(self, data):
        pass
