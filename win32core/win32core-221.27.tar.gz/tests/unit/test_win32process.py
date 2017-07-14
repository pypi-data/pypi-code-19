import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
from win32process import *


@pytest.mark.xfail
def test_AttachThreadInput():
    AttachThreadInput()


@pytest.mark.xfail
def test_CreateProcess():
    CreateProcess()


@pytest.mark.xfail
def test_CreateProcessAsUser():
    CreateProcessAsUser()


@pytest.mark.xfail
def test_CreateRemoteThread():
    CreateRemoteThread()


@pytest.mark.xfail
def test_EnumProcessModules():
    EnumProcessModules()


def test_EnumProcesses():
    EnumProcesses()


@pytest.mark.xfail
def test_ExitProcess():
    ExitProcess()


def test_GetCurrentProcess():
    GetCurrentProcess()


def test_GetCurrentProcessId():
    GetCurrentProcessId()


@pytest.mark.xfail
def test_GetExitCodeProcess():
    GetExitCodeProcess()


@pytest.mark.xfail
def test_GetExitCodeThread():
    GetExitCodeThread()


@pytest.mark.xfail
def test_GetGuiResources():
    GetGuiResources()


@pytest.mark.xfail
def test_GetModuleFileNameEx():
    GetModuleFileNameEx()


@pytest.mark.xfail
def test_GetPriorityClass():
    GetPriorityClass()


@pytest.mark.xfail
def test_GetProcessAffinityMask():
    GetProcessAffinityMask()


@pytest.mark.xfail
def test_GetProcessId():
    GetProcessId()


@pytest.mark.xfail
def test_GetProcessIoCounters():
    GetProcessIoCounters()


@pytest.mark.xfail
def test_GetProcessMemoryInfo():
    GetProcessMemoryInfo()


@pytest.mark.xfail
def test_GetProcessPriorityBoost():
    GetProcessPriorityBoost()


def test_GetProcessShutdownParameters():
    GetProcessShutdownParameters()


@pytest.mark.xfail
def test_GetProcessTimes():
    GetProcessTimes()


@pytest.mark.xfail
def test_GetProcessVersion():
    GetProcessVersion()


def test_GetProcessWindowStation():
    GetProcessWindowStation()


@pytest.mark.xfail
def test_GetProcessWorkingSetSize():
    GetProcessWorkingSetSize()


def test_GetStartupInfo():
    GetStartupInfo()


@pytest.mark.xfail
def test_GetThreadIOPendingFlag():
    GetThreadIOPendingFlag()


@pytest.mark.xfail
def test_GetThreadPriority():
    GetThreadPriority()


@pytest.mark.xfail
def test_GetThreadPriorityBoost():
    GetThreadPriorityBoost()


@pytest.mark.xfail
def test_GetThreadTimes():
    GetThreadTimes()


@pytest.mark.xfail
def test_GetWindowThreadProcessId():
    GetWindowThreadProcessId()


def test_IsWow64Process():
    IsWow64Process()


@pytest.mark.xfail
def test_ResumeThread():
    ResumeThread()


def test_STARTUPINFO():
    STARTUPINFO()


@pytest.mark.xfail
def test_SetPriorityClass():
    SetPriorityClass()


@pytest.mark.xfail
def test_SetProcessAffinityMask():
    SetProcessAffinityMask()


@pytest.mark.xfail
def test_SetProcessPriorityBoost():
    SetProcessPriorityBoost()


@pytest.mark.xfail
def test_SetProcessShutdownParameters():
    SetProcessShutdownParameters()


@pytest.mark.xfail
def test_SetProcessWorkingSetSize():
    SetProcessWorkingSetSize()


@pytest.mark.xfail
def test_SetThreadAffinityMask():
    SetThreadAffinityMask()


@pytest.mark.xfail
def test_SetThreadIdealProcessor():
    SetThreadIdealProcessor()


@pytest.mark.xfail
def test_SetThreadPriority():
    SetThreadPriority()


@pytest.mark.xfail
def test_SetThreadPriorityBoost():
    SetThreadPriorityBoost()


@pytest.mark.xfail
def test_SuspendThread():
    SuspendThread()


@pytest.mark.xfail
def test_TerminateProcess():
    TerminateProcess()


@pytest.mark.xfail
def test_beginthreadex():
    beginthreadex()
