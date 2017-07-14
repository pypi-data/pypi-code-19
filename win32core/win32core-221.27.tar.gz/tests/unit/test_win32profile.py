import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
from win32profile import *
@pytest.mark.xfail
def test_CreateEnvironmentBlock():
    CreateEnvironmentBlock()     



@pytest.mark.xfail
def test_DeleteProfile():
    DeleteProfile()     



@pytest.mark.xfail
def test_ExpandEnvironmentStringsForUser():
    ExpandEnvironmentStringsForUser()     



def test_GetAllUsersProfileDirectory():
    GetAllUsersProfileDirectory()     



def test_GetDefaultUserProfileDirectory():
    GetDefaultUserProfileDirectory()     



def test_GetEnvironmentStrings():
    GetEnvironmentStrings()     



def test_GetProfileType():
    GetProfileType()     



def test_GetProfilesDirectory():
    GetProfilesDirectory()     



@pytest.mark.xfail
def test_GetUserProfileDirectory():
    GetUserProfileDirectory()     



@pytest.mark.xfail
def test_LoadUserProfile():
    LoadUserProfile()     



@pytest.mark.xfail
def test_UnloadUserProfile():
    UnloadUserProfile()     


