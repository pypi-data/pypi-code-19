import pytest
import pytest
import pytest
import pytest
import pytest
import pytest
from win32transaction import *
@pytest.mark.xfail
def test_CommitTransaction():
    CommitTransaction()     



@pytest.mark.xfail
def test_CommitTransactionAsync():
    CommitTransactionAsync()     



def test_CreateTransaction():
    CreateTransaction()     



@pytest.mark.xfail
def test_GetTransactionId():
    GetTransactionId()     



@pytest.mark.xfail
def test_OpenTransaction():
    OpenTransaction()     



@pytest.mark.xfail
def test_RollbackTransaction():
    RollbackTransaction()     



@pytest.mark.xfail
def test_RollbackTransactionAsync():
    RollbackTransactionAsync()     


