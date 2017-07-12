import pytest

from win2kras import *


@pytest.mark.xfail
def test_RasGetEapUserIdentity():
    RasGetEapUserIdentity()
