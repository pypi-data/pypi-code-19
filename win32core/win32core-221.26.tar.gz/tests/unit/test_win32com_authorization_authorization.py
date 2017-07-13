import pytest

from win32com.authorization.authorization import *


@pytest.mark.xfail
def test_EditSecurity():
    EditSecurity()
