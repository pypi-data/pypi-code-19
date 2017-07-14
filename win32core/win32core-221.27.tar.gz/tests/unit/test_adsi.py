import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
from adsi import *
@pytest.mark.xfail
def test_ADsBuildEnumerator():
    ADsBuildEnumerator()     



@pytest.mark.xfail
def test_ADsEnumerateNext():
    ADsEnumerateNext()     



def test_ADsGetLastError():
    ADsGetLastError()     



@pytest.mark.xfail
def test_ADsGetObject():
    ADsGetObject()     



@pytest.mark.xfail
def test_ADsOpenObject():
    ADsOpenObject()     



@pytest.mark.xfail
def test_DSOP_SCOPE_INIT_INFOs():
    DSOP_SCOPE_INIT_INFOs()     



@pytest.mark.xfail
def test_StringAsDS_SELECTION_LIST():
    StringAsDS_SELECTION_LIST()     


