import pytest
import pytest
import pytest
import pytest
import pytest

from pywintypes import *


def test_ACL():
    ACL()


def test_CreateGuid():
    CreateGuid()


@pytest.mark.xfail
def test_DosDateTimeToTime():
    DosDateTimeToTime()


def test_HANDLE():
    HANDLE()


def test_HKEY():
    HKEY()


@pytest.mark.xfail
def test_IID():
    IID()


@pytest.mark.xfail
def test_IsTextUnicode():
    IsTextUnicode()


def test_OVERLAPPED():
    OVERLAPPED()


def test_SECURITY_ATTRIBUTES():
    SECURITY_ATTRIBUTES()


def test_SECURITY_DESCRIPTOR():
    SECURITY_DESCRIPTOR()


def test_SID():
    SID()


@pytest.mark.xfail
def test_Time():
    Time()


@pytest.mark.skip
def test_Unicode():
    Unicode()


@pytest.mark.skip
def test_UnicodeFromRaw():
    UnicodeFromRaw()


def test_WAVEFORMATEX():
    WAVEFORMATEX()
