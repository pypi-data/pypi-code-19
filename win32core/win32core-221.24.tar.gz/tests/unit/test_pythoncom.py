import pytest

from pythoncom import *


@pytest.mark.skip
def test_CoCreateFreeThreadedMarshaler():
    CoCreateFreeThreadedMarshaler()


@pytest.mark.skip
def test_CoCreateInstance():
    CoCreateInstance()


@pytest.mark.skip
def test_CoCreateInstanceEx():
    CoCreateInstanceEx()


@pytest.mark.skip
def test_CoFreeUnusedLibraries():
    CoFreeUnusedLibraries()


@pytest.mark.skip
def test_CoGetInterfaceAndReleaseStream():
    CoGetInterfaceAndReleaseStream()


@pytest.mark.skip
def test_CoGetObject():
    CoGetObject()


@pytest.mark.skip
def test_CoInitialize():
    CoInitialize()


@pytest.mark.skip
def test_CoInitializeEx():
    CoInitializeEx()


@pytest.mark.skip
def test_CoInitializeSecurity():
    CoInitializeSecurity()


@pytest.mark.skip
def test_CoMarshalInterThreadInterfaceInStream():
    CoMarshalInterThreadInterfaceInStream()


@pytest.mark.skip
def test_CoMarshalInterface():
    CoMarshalInterface()


@pytest.mark.skip
def test_CoRegisterClassObject():
    CoRegisterClassObject()


@pytest.mark.skip
def test_CoReleaseMarshalData():
    CoReleaseMarshalData()


@pytest.mark.skip
def test_CoResumeClassObjects():
    CoResumeClassObjects()


@pytest.mark.skip
def test_CoRevokeClassObject():
    CoRevokeClassObject()


@pytest.mark.skip
def test_CoTreatAsClass():
    CoTreatAsClass()


@pytest.mark.skip
def test_CoUninitialize():
    CoUninitialize()


@pytest.mark.skip
def test_CoUnmarshalInterface():
    CoUnmarshalInterface()


@pytest.mark.skip
def test_CoWaitForMultipleHandles():
    CoWaitForMultipleHandles()


@pytest.mark.skip
def test_Connect():
    Connect()


@pytest.mark.skip
def test_CreateBindCtx():
    CreateBindCtx()


@pytest.mark.skip
def test_CreateFileMoniker():
    CreateFileMoniker()


@pytest.mark.skip
def test_CreateGuid():
    CreateGuid()


@pytest.mark.skip
def test_CreateILockBytesOnHGlobal():
    CreateILockBytesOnHGlobal()


@pytest.mark.skip
def test_CreateItemMoniker():
    CreateItemMoniker()


@pytest.mark.skip
def test_CreatePointerMoniker():
    CreatePointerMoniker()


@pytest.mark.skip
def test_CreateStreamOnHGlobal():
    CreateStreamOnHGlobal()


@pytest.mark.skip
def test_CreateTypeLib():
    CreateTypeLib()


@pytest.mark.skip
def test_CreateTypeLib2():
    CreateTypeLib2()


@pytest.mark.skip
def test_CreateURLMoniker():
    CreateURLMoniker()


@pytest.mark.skip
def test_DoDragDrop():
    DoDragDrop()


@pytest.mark.skip
def test_EnableQuitMessage():
    EnableQuitMessage()


@pytest.mark.skip
def test_FUNCDESC():
    FUNCDESC()


@pytest.mark.skip
def test_FmtIdToPropStgName():
    FmtIdToPropStgName()


@pytest.mark.skip
def test_GetActiveObject():
    GetActiveObject()


@pytest.mark.skip
def test_GetClassFile():
    GetClassFile()


@pytest.mark.skip
def test_GetFacilityString():
    GetFacilityString()


@pytest.mark.skip
def test_GetRecordFromGuids():
    GetRecordFromGuids()


@pytest.mark.skip
def test_GetRecordFromTypeInfo():
    GetRecordFromTypeInfo()


@pytest.mark.skip
def test_GetRunningObjectTable():
    GetRunningObjectTable()


@pytest.mark.skip
def test_GetScodeRangeString():
    GetScodeRangeString()


@pytest.mark.skip
def test_GetScodeString():
    GetScodeString()


@pytest.mark.skip
def test_GetSeverityString():
    GetSeverityString()


@pytest.mark.skip
def test_IsGatewayRegistered():
    IsGatewayRegistered()


@pytest.mark.skip
def test_LoadRegTypeLib():
    LoadRegTypeLib()


@pytest.mark.skip
def test_LoadTypeLib():
    LoadTypeLib()


@pytest.mark.skip
def test_MakePyFactory():
    MakePyFactory()


@pytest.mark.skip
def test_MkParseDisplayName():
    MkParseDisplayName()


@pytest.mark.skip
def test_New():
    New()


@pytest.mark.skip
def test_ObjectFromAddress():
    ObjectFromAddress()


@pytest.mark.skip
def test_ObjectFromLresult():
    ObjectFromLresult()


@pytest.mark.skip
def test_OleFlushClipboard():
    OleFlushClipboard()


@pytest.mark.skip
def test_OleGetClipboard():
    OleGetClipboard()


@pytest.mark.skip
def test_OleInitialize():
    OleInitialize()


@pytest.mark.skip
def test_OleIsCurrentClipboard():
    OleIsCurrentClipboard()


@pytest.mark.skip
def test_OleLoad():
    OleLoad()


@pytest.mark.skip
def test_OleLoadFromStream():
    OleLoadFromStream()


@pytest.mark.skip
def test_OleSaveToStream():
    OleSaveToStream()


@pytest.mark.skip
def test_OleSetClipboard():
    OleSetClipboard()


@pytest.mark.skip
def test_ProgIDFromCLSID():
    ProgIDFromCLSID()


@pytest.mark.skip
def test_PropStgNameToFmtId():
    PropStgNameToFmtId()


@pytest.mark.skip
@pytest.mark.skip
def test_PumpMessages():
    PumpMessages()


@pytest.mark.skip
def test_PumpWaitingMessages():
    PumpWaitingMessages()


@pytest.mark.skip
def test_QueryPathOfRegTypeLib():
    QueryPathOfRegTypeLib()


@pytest.mark.skip
def test_ReadClassStg():
    ReadClassStg()


@pytest.mark.skip
def test_ReadClassStm():
    ReadClassStm()


@pytest.mark.skip
def test_RegisterActiveObject():
    RegisterActiveObject()


@pytest.mark.skip
def test_RegisterDragDrop():
    RegisterDragDrop()


@pytest.mark.skip
def test_RegisterTypeLib():
    RegisterTypeLib()


@pytest.mark.xfail
@pytest.mark.skip
def test_RevokeActiveObject():
    RevokeActiveObject()


@pytest.mark.skip
def test_RevokeDragDrop():
    RevokeDragDrop()


@pytest.mark.skip
def test_STGMEDIUM():
    STGMEDIUM()


@pytest.mark.skip
def test_StgCreateDocfile():
    StgCreateDocfile()


@pytest.mark.skip
def test_StgCreateDocfileOnILockBytes():
    StgCreateDocfileOnILockBytes()


@pytest.mark.skip
def test_StgIsStorageFile():
    StgIsStorageFile()


@pytest.mark.skip
def test_StgOpenStorage():
    StgOpenStorage()


@pytest.mark.skip
def test_StgOpenStorageEx():
    StgOpenStorageEx()


@pytest.mark.skip
def test_TYPEATTR():
    TYPEATTR()


@pytest.mark.skip
def test_UnRegisterTypeLib():
    UnRegisterTypeLib()


@pytest.mark.skip
def test_UnwrapObject():
    UnwrapObject()


@pytest.mark.skip
def test_VARDESC():
    VARDESC()


@pytest.mark.skip
def test_WrapObject():
    WrapObject()


@pytest.mark.skip
def test_WriteClassStg():
    WriteClassStg()


@pytest.mark.skip
def test_WriteClassStm():
    WriteClassStm()


@pytest.mark.skip
@pytest.mark.skip
def test_GetInterfaceCount():
    GetInterfaceCount()


@pytest.mark.skip
def test_GetInterfaceCount():
    GetInterfaceCount()
