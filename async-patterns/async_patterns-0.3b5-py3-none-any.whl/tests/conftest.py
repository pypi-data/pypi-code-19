import asyncio

import pytest

@pytest.fixture(scope='module')
def loop():
    return asyncio.get_event_loop()


