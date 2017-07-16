import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
from servicemanager import *
@pytest.mark.xfail
def test_CoInitializeEx():
    CoInitializeEx()     



def test_CoUninitialize():
    CoUninitialize()     



def test_Debugging():
    Debugging()     



def test_Finalize():
    Finalize()     



def test_Initialize():
    Initialize()     



@pytest.mark.xfail
def test_LogErrorMsg():
    LogErrorMsg()     



@pytest.mark.xfail
def test_LogInfoMsg():
    LogInfoMsg()     



@pytest.mark.xfail
def test_LogMsg():
    LogMsg()     



@pytest.mark.xfail
def test_LogWarningMsg():
    LogWarningMsg()     



@pytest.mark.xfail
def test_PrepareToHostMultiple():
    PrepareToHostMultiple()     



def test_PrepareToHostSingle():
    PrepareToHostSingle()     



def test_PumpWaitingMessages():
    PumpWaitingMessages()     



@pytest.mark.xfail
def test_RegisterServiceCtrlHandler():
    RegisterServiceCtrlHandler()     



def test_RunningAsService():
    RunningAsService()     



@pytest.mark.xfail
def test_SetEventSourceName():
    SetEventSourceName()     



@pytest.mark.xfail
def test_StartServiceCtrlDispatcher():
    StartServiceCtrlDispatcher()     


