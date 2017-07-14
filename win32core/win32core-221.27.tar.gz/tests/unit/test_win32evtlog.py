import pytest

from win32evtlog import *


@pytest.mark.xfail
def test_BackupEventLog():
    BackupEventLog()


@pytest.mark.xfail
def test_ClearEventLog():
    ClearEventLog()


@pytest.mark.xfail
def test_CloseEventLog():
    CloseEventLog()


@pytest.mark.xfail
def test_DeregisterEventSource():
    DeregisterEventSource()


@pytest.mark.xfail
def test_GetNumberOfEventLogRecords():
    GetNumberOfEventLogRecords()


@pytest.mark.xfail
def test_GetOldestEventLogRecord():
    GetOldestEventLogRecord()


@pytest.mark.xfail
def test_NotifyChangeEventLog():
    NotifyChangeEventLog()


@pytest.mark.xfail
def test_OpenBackupEventLog():
    OpenBackupEventLog()


@pytest.mark.xfail
def test_OpenEventLog():
    OpenEventLog()


@pytest.mark.xfail
def test_ReadEventLog():
    ReadEventLog()


@pytest.mark.xfail
def test_RegisterEventSource():
    RegisterEventSource()


@pytest.mark.xfail
def test_ReportEvent():
    ReportEvent()
