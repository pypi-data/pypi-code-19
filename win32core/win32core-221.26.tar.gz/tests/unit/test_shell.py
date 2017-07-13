import pytest

from shell import *


@pytest.mark.xfail
def test_AddressAsPIDL():
    AddressAsPIDL()


def test_AssocCreate():
    AssocCreate()


@pytest.mark.xfail
def test_AssocCreateForClasses():
    AssocCreateForClasses()


@pytest.mark.xfail
def test_CIDAAsString():
    CIDAAsString()


@pytest.mark.xfail
def test_DragQueryFile():
    DragQueryFile()


@pytest.mark.xfail
def test_DragQueryFileW():
    DragQueryFileW()


@pytest.mark.xfail
def test_DragQueryPoint():
    DragQueryPoint()


@pytest.mark.xfail
def test_FILEGROUPDESCRIPTORAsString():
    FILEGROUPDESCRIPTORAsString()


def test_IsUserAnAdmin():
    IsUserAnAdmin()


@pytest.mark.xfail
def test_PIDLAsString():
    PIDLAsString()


@pytest.mark.xfail
def test_SHAddToRecentDocs():
    SHAddToRecentDocs()


@pytest.mark.skip
def test_SHBrowseForFolder():
    SHBrowseForFolder()


@pytest.mark.xfail
def test_SHChangeNotify():
    SHChangeNotify()


@pytest.mark.xfail
def test_SHChangeNotify():
    SHChangeNotify()


@pytest.mark.xfail
def test_SHChangeNotifyDeregister():
    SHChangeNotifyDeregister()


@pytest.mark.xfail
def test_SHChangeNotifyRegister():
    SHChangeNotifyRegister()


@pytest.mark.xfail
def test_SHCreateDataObject():
    SHCreateDataObject()


@pytest.mark.xfail
def test_SHCreateDefaultContextMenu():
    SHCreateDefaultContextMenu()


def test_SHCreateDefaultExtractIcon():
    SHCreateDefaultExtractIcon()


@pytest.mark.xfail
def test_SHCreateItemFromIDList():
    SHCreateItemFromIDList()


@pytest.mark.xfail
def test_SHCreateItemFromParsingName():
    SHCreateItemFromParsingName()


@pytest.mark.xfail
def test_SHCreateItemFromRelativeName():
    SHCreateItemFromRelativeName()


@pytest.mark.xfail
def test_SHCreateItemInKnownFolder():
    SHCreateItemInKnownFolder()


@pytest.mark.xfail
def test_SHCreateItemWithParent():
    SHCreateItemWithParent()


@pytest.mark.xfail
def test_SHCreateShellFolderView():
    SHCreateShellFolderView()


@pytest.mark.xfail
def test_SHCreateShellItemArray():
    SHCreateShellItemArray()


@pytest.mark.xfail
def test_SHCreateShellItemArrayFromDataObject():
    SHCreateShellItemArrayFromDataObject()


@pytest.mark.xfail
def test_SHCreateShellItemArrayFromIDLists():
    SHCreateShellItemArrayFromIDLists()


@pytest.mark.xfail
def test_SHCreateShellItemArrayFromIDLists():
    SHCreateShellItemArrayFromIDLists()


@pytest.mark.xfail
def test_SHEmptyRecycleBin():
    SHEmptyRecycleBin()


@pytest.mark.xfail
def test_SHFileOperation():
    SHFileOperation()


def test_SHGetDesktopFolder():
    SHGetDesktopFolder()


@pytest.mark.xfail
def test_SHGetFileInfo():
    SHGetFileInfo()


@pytest.mark.xfail
def test_SHGetFolderLocation():
    SHGetFolderLocation()


@pytest.mark.xfail
def test_SHGetFolderPath():
    SHGetFolderPath()


@pytest.mark.xfail
def test_SHGetIDListFromObject():
    SHGetIDListFromObject()


@pytest.mark.xfail
def test_SHGetInstanceExplorer():
    SHGetInstanceExplorer()


@pytest.mark.xfail
def test_SHGetNameFromIDList():
    SHGetNameFromIDList()


@pytest.mark.xfail
def test_SHGetPathFromIDList():
    SHGetPathFromIDList()


@pytest.mark.xfail
def test_SHGetPathFromIDListW():
    SHGetPathFromIDListW()


def test_SHGetSettings():
    SHGetSettings()


@pytest.mark.xfail
def test_SHGetSpecialFolderLocation():
    SHGetSpecialFolderLocation()


@pytest.mark.xfail
def test_SHGetSpecialFolderPath():
    SHGetSpecialFolderPath()


@pytest.mark.xfail
def test_SHGetViewStatePropertyBag():
    SHGetViewStatePropertyBag()


@pytest.mark.xfail
def test_SHILCreateFromPath():
    SHILCreateFromPath()


def test_SHQueryRecycleBin():
    SHQueryRecycleBin()


@pytest.mark.xfail
def test_SHSetFolderPath():
    SHSetFolderPath()


@pytest.mark.xfail
def test_SHUpdateImage():
    SHUpdateImage()


def test_ShellExecuteEx():
    ShellExecuteEx()


@pytest.mark.xfail
def test_StringAsCIDA():
    StringAsCIDA()


@pytest.mark.xfail
def test_StringAsFILEGROUPDESCRIPTOR():
    StringAsFILEGROUPDESCRIPTOR()


@pytest.mark.xfail
def test_StringAsPIDL():
    StringAsPIDL()
