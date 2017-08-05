from ethereum_helpers import recover


def test_verifying_key_hex_bytes(message: str,
                                 signature: str,
                                 verifying_key_hex_bytes: bytes) -> None:
    assert recover.verifying_key_hex_bytes(signature,
                                           message=message
                                           ) == verifying_key_hex_bytes
