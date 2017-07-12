from base64 import urlsafe_b64decode, urlsafe_b64encode


class B64:
    @staticmethod
    def decode(data: bytes) -> bytes:
        return urlsafe_b64decode(data + (b'=' * (len(data) % 4)))

    @staticmethod
    def encode(data: bytes) -> bytes:
        return urlsafe_b64encode(data).rstrip(b'=')
