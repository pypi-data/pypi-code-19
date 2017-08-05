from ethereum_helpers.messages import sign_message


def test_sign_message(hex_characters: str,
                      message: str,
                      signing_key_hex_string: str) -> None:
    signature = sign_message(message,
                             signing_key_hex_string=signing_key_hex_string)
    assert isinstance(signature, str)
    assert not signature.startswith('0x')
    assert all(character in hex_characters
               for character in signature)
