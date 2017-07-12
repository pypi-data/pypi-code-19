from typing import Tuple, Any, Union

from nacl.utils import random
from nacl.secret import SecretBox
from nacl.exceptions import CryptoError

from .b64 import B64
from .exceptions import CompromisedToken, UnexpectedDataValue


class Tokenizer:
    def __init__(self, nonce_size: int = SecretBox.NONCE_SIZE, secret_size: int = SecretBox.KEY_SIZE):
        # Amount of bytes the randomly generated nonces
        self.nonce_size = nonce_size

        # Amount of bytes for the randomly generated secret keys
        self.secret_size = secret_size

    async def generate(self, data: Union[list, tuple]) -> Tuple[bytes, bytes]:
        # Parse data to json
        data = await Packer.pack(data)

        # Generate a random secret key and make a secret box from it
        box, secret = await self.make_box()

        # Generate a random nonce
        nonce = random(self.nonce_size)

        # Encrypt data
        encrypted_data = box.encrypt(data, nonce, B64)

        # No longer needed
        del data, nonce

        # Return a tuple with the encrypted data encoded in base64 and the secret to decrypt the data in the future
        return encrypted_data, B64.encode(secret)

    async def extract(self, token: bytes, secret: bytes) -> Any:
        # Create an instance of SecretBox with the provided secret key
        box = (await self.make_box(secret_key=B64.decode(secret)))[0]

        try:
            # Decrypt contents
            data = box.decrypt(token, encoder=B64)
        except CryptoError:
            # If the decryption fails, the token has been compromised
            raise CompromisedToken

        # Return decoded data
        return await Packer.unpack(data)

    async def make_box(self, secret_key: bytes = None) -> Tuple[SecretBox, bytes]:
        if not secret_key:
            # If a secret key isn't provided then create a random one
            secret_key = random(self.secret_size)

        # Return a tuple with the instance of SecretBox and the secret key itself
        return SecretBox(secret_key), secret_key


class Packer:
    @staticmethod
    async def unpack(data: bytes, separator: str = '.') -> tuple:
        return tuple(map(lambda packed: int(packed), data.decode('utf-8').split(separator)))

    @staticmethod
    async def pack(data: Union[list, tuple], separator: str = '.') -> bytes:
        if not isinstance(data, (list, tuple)):
            raise UnexpectedDataValue

        def _convert_to_str(e: Any) -> str:
            return e if isinstance(e, str) else str(e)
        return separator.join(list(map(_convert_to_str, data))).encode('utf-8')
