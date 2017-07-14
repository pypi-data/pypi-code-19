import pytest
import pytest
from win32crypt import *
@pytest.mark.xfail
def test_CryptProtectData():
    CryptProtectData()     



@pytest.mark.xfail
def test_CryptUnprotectData():
    CryptUnprotectData()     


