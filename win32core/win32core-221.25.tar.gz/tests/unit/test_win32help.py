import pytest
import pytest
from win32help import *
def test_HHNTRACK():
    HHNTRACK()     



def test_HHN_NOTIFY():
    HHN_NOTIFY()     



def test_HH_AKLINK():
    HH_AKLINK()     



def test_HH_FTS_QUERY():
    HH_FTS_QUERY()     



def test_HH_POPUP():
    HH_POPUP()     



def test_HH_WINTYPE():
    HH_WINTYPE()     



@pytest.mark.xfail
def test_HtmlHelp():
    HtmlHelp()     



def test_NMHDR():
    NMHDR()     



@pytest.mark.xfail
def test_WinHelp():
    WinHelp()     


