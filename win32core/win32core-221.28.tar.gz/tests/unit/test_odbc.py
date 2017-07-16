import pytest
import pytest
from odbc import *
@pytest.mark.xfail
def test_SQLDataSources():
    SQLDataSources()     



@pytest.mark.xfail
def test_odbc():
    odbc()     


