import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest

from win32ts import *


@pytest.mark.xfail
def test_ProcessIdToSessionId():
    ProcessIdToSessionId()


@pytest.mark.xfail
def test_WTSCloseServer():
    WTSCloseServer()


@pytest.mark.xfail
def test_WTSDisconnectSession():
    WTSDisconnectSession()


def test_WTSEnumerateProcesses():
    WTSEnumerateProcesses()


@pytest.mark.xfail
def test_WTSEnumerateServers():
    WTSEnumerateServers()


def test_WTSEnumerateSessions():
    WTSEnumerateSessions()


def test_WTSGetActiveConsoleSessionId():
    WTSGetActiveConsoleSessionId()


@pytest.mark.xfail
def test_WTSLogoffSession():
    WTSLogoffSession()


@pytest.mark.xfail
def test_WTSOpenServer():
    WTSOpenServer()


@pytest.mark.xfail
def test_WTSQuerySessionInformation():
    WTSQuerySessionInformation()


@pytest.mark.xfail
def test_WTSQueryUserConfig():
    WTSQueryUserConfig()


@pytest.mark.xfail
def test_WTSQueryUserToken():
    WTSQueryUserToken()


@pytest.mark.xfail
def test_WTSRegisterSessionNotification():
    WTSRegisterSessionNotification()


@pytest.mark.xfail
def test_WTSSendMessage():
    WTSSendMessage()


@pytest.mark.xfail
def test_WTSSetUserConfig():
    WTSSetUserConfig()


@pytest.mark.xfail
def test_WTSShutdownSystem():
    WTSShutdownSystem()


@pytest.mark.xfail
def test_WTSTerminateProcess():
    WTSTerminateProcess()


@pytest.mark.xfail
def test_WTSUnRegisterSessionNotification():
    WTSUnRegisterSessionNotification()


@pytest.mark.skip
def test_WTSWaitSystemEvent():
    WTSWaitSystemEvent()
