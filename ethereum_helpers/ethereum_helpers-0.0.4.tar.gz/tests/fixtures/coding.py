import pytest
from ethereum_helpers.coding import characters_by_base


@pytest.fixture(scope='session')
def hex_characters() -> str:
    return characters_by_base(16)
