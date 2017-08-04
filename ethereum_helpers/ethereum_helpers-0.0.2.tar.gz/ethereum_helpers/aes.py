from typing import (Union,
                    Dict)

from Cryptodome.Cipher import AES


def decrypt(*,
            text: str,
            key: bytes,
            counter: Dict[str, Union[int, bool, bytes]] = None,
            mode: int = AES.MODE_CTR) -> bytes:
    encryptor = AES.new(key,
                        mode,
                        counter=counter)
    return encryptor.decrypt(text)
