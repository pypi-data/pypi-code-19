import pytest
from ethereum_helpers.messages import sign_message
from tests.strategies import messages_strategy
from tests.utils import example


@pytest.fixture(scope='function')
def message() -> str:
    return example(messages_strategy)


@pytest.fixture(scope='function')
def signature(message: str,
              signing_key_hex_string: str) -> str:
    return sign_message(message,
                        signing_key_hex_string=signing_key_hex_string)
